import streamlit as st
import pandas as pd
from PIL import Image
from database import init_db, add_inspection, get_all, delete_inspection
from detector import analyze_image, estimate_unusual_color
from report import make_pdf

st.set_page_config(
    page_title="Smart HairScan AI",
    page_icon="✂️",
    layout="wide"
)
init_db()

st.markdown("""
<style>
.main {background-color: #f5f7fa;}
.block-container {padding-top: 1.5rem;}
div[data-testid="stMetric"] {
    background: white; padding: 14px; border-radius: 12px;
    border: 1px solid #e5eaf0;
}
</style>
""", unsafe_allow_html=True)

st.title("✂️ Smart HairScan AI")
st.caption("Sistem saringan pematuhan rambut pelajar berasaskan AI")

records = get_all()
page = st.sidebar.radio(
    "Menu utama",
    ["Dashboard", "Imbasan AI", "Rekod Pelajar", "Laporan PDF", "Panduan & Tetapan"]
)

def as_df(rows):
    return pd.DataFrame([dict(r) for r in rows]) if rows else pd.DataFrame()

if page == "Dashboard":
    st.header("Dashboard")
    df = as_df(records)
    if df.empty:
        st.info("Belum ada rekod pemeriksaan. Mulakan melalui menu Imbasan AI.")
    else:
        total = len(df)
        long_count = int((df["long_hair"] == "Disahkan tidak mematuhi").sum())
        color_count = int((df["colored_hair"] == "Disahkan tidak mematuhi").sum())
        compliant = int(
            ((df["long_hair"] == "Disahkan mematuhi") &
             (df["colored_hair"] == "Disahkan mematuhi")).sum()
        )
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Jumlah pemeriksaan", total)
        c2.metric("Disahkan mematuhi", compliant)
        c3.metric("Rambut panjang", long_count)
        c4.metric("Rambut berwarna", color_count)

        st.subheader("Ringkasan mengikut kelas")
        st.bar_chart(df.groupby("student_class").size())
        st.subheader("Pemeriksaan terkini")
        st.dataframe(
            df[["inspected_at", "student_id", "student_name",
                "student_class", "long_hair", "colored_hair"]],
            use_container_width=True, hide_index=True
        )

elif page == "Imbasan AI":
    st.header("Imbasan rambut pelajar")
    st.warning(
        "Ambil gambar dengan kebenaran yang sesuai. Gunakan latar dan "
        "pencahayaan yang baik. AI hanya membantu saringan; guru mesti "
        "menilai dan mengesahkan keputusan."
    )
    source = st.radio("Pilih sumber gambar", ["Kamera langsung", "Muat naik gambar"])
    image = None

    if source == "Kamera langsung":
        camera_file = st.camera_input("Ambil gambar untuk pemeriksaan")
        if camera_file:
            image = Image.open(camera_file).convert("RGB")
    else:
        upload = st.file_uploader(
            "Pilih gambar", type=["jpg", "jpeg", "png"]
        )
        if upload:
            image = Image.open(upload).convert("RGB")

    if image:
        st.image(image, caption="Gambar diterima", use_container_width=True)
        confidence = st.slider("Keyakinan minimum model", 0.10, 0.95, 0.40, 0.05)
        if st.button("Jalankan analisis", type="primary"):
            result = analyze_image(image, confidence)
            st.session_state["last_result"] = result
            st.session_state["last_image"] = image

    
    result = st.session_state.get("last_result")

    if result:
        st.subheader("Hasil Analisis AI")

        if result["model_ready"]:
            detections = result["detections"]

            if detections:
                best_result = max(
                    detections,
                    key=lambda x: x["confidence"]
                )

                st.success(
                    f"Kategori dikesan: {best_result['name']}"
                )

                st.metric(
                    "Keyakinan AI",
                    f"{best_result['confidence'] * 100:.2f}%"
                )

                st.subheader("Skor Empat Kategori")

                for item in detections:
                    score = item["confidence"]
                    st.write(
                        f"{item['name']}: {score * 100:.2f}%"
                    )
                    st.progress(float(score))
            else:
                st.warning("Tiada keputusan klasifikasi diperoleh.")

        else:
            st.error(result["notes"])

        st.write("**Panjang rambut:**", result["long_status"])
        st.write("**Warna rambut:**", result["color_status"])

        st.subheader("Pengesahan guru")
        st.caption("Pilih status selepas menyemak gambar dan peraturan sekolah.")
        with st.form("save_record"):
            student_id = st.text_input("ID / nombor pelajar")
            student_name = st.text_input("Nama pelajar")
            student_class = st.text_input("Kelas")
            long_status = st.selectbox(
                "Status panjang rambut",
                ["Belum disahkan", "Disahkan mematuhi",
                 "Disahkan tidak mematuhi", "Perlu pemeriksaan lanjut"]
            )
            color_status = st.selectbox(
                "Status warna rambut",
                ["Belum disahkan", "Disahkan mematuhi",
                 "Disahkan tidak mematuhi", "Perlu pemeriksaan lanjut"]
            )
            color_note = st.text_input("Catatan warna / pemerhatian")
            reviewer = st.text_input("Nama guru pemeriksa")
            notes = st.text_area("Catatan tambahan")
            submitted = st.form_submit_button("Simpan rekod pemeriksaan")
            if submitted:
                if not student_id.strip() or not student_name.strip() or not student_class.strip():
                    st.error("Sila isi ID, nama dan kelas pelajar.")
                else:
                    add_inspection(
                        student_id, student_name, student_class,
                        long_status, color_status, color_note,
                        notes, reviewer
                    )
                    st.success("Rekod berjaya disimpan.")
                    st.session_state.pop("last_result", None)
                    st.session_state.pop("last_image", None)
                    st.rerun()

elif page == "Rekod Pelajar":
    st.header("Rekod pemeriksaan")
    df = as_df(records)
    if df.empty:
        st.info("Tiada rekod untuk dipaparkan.")
    else:
        search = st.text_input("Cari nama, ID atau kelas")
        if search:
            mask = (
                df["student_name"].astype(str).str.contains(search, case=False) |
                df["student_id"].astype(str).str.contains(search, case=False) |
                df["student_class"].astype(str).str.contains(search, case=False)
            )
            df = df[mask]
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption("Padam rekod hanya jika anda mempunyai kebenaran.")
        ids = [int(x) for x in df["id"].tolist()]
        if ids:
            chosen = st.selectbox("Pilih ID rekod untuk dipadam", ids)
            if st.button("Padam rekod terpilih"):
                delete_inspection(chosen)
                st.success("Rekod dipadam.")
                st.rerun()

elif page == "Laporan PDF":
    st.header("Laporan PDF")
    df = as_df(records)
    if df.empty:
        st.info("Belum ada rekod untuk dijadikan laporan.")
    else:
        st.write(f"Jumlah rekod: **{len(df)}**")
        pdf = make_pdf(records)
        st.download_button(
            "Muat turun laporan PDF",
            data=pdf,
            file_name="laporan_smarthairscan.pdf",
            mime="application/pdf"
        )
        st.download_button(
            "Muat turun data CSV",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name="rekod_smarthairscan.csv",
            mime="text/csv"
        )

elif page == "Panduan & Tetapan":
    st.header("Panduan penggunaan")
    st.markdown("""
1. Buka menu **Imbasan AI**.
2. Ambil gambar menggunakan kamera atau muat naik gambar.
3. Jalankan analisis AI.
4. Semak hasil pengesanan dan gambar.
5. Guru memilih status pengesahan secara manual.
6. Simpan rekod untuk dimasukkan ke Dashboard dan Laporan PDF.

### Status model AI
- Letakkan fail model terlatih bernama `best.pt` di folder yang sama dengan `app.py`.
- Tanpa model itu, aplikasi masih boleh menyimpan rekod dan menjana laporan,
  tetapi pengesanan YOLO belum aktif.
- Petunjuk warna berasaskan piksel bukan pengesanan rambut dan tidak boleh
  dijadikan bukti pelanggaran peraturan.

### Privasi
- Gunakan gambar hanya dengan kebenaran dan tujuan yang sah.
- Hadkan akses kepada guru yang diberi kuasa.
- Jangan muat naik gambar pelajar ke hosting awam tanpa kelulusan sekolah.
- Sediakan tempoh penyimpanan dan pemadaman data yang jelas.
""")
