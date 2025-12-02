# app.py
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from io import BytesIO
from PIL import Image as PILImage
from datetime import date

st.set_page_config(page_title="Minit Mesyuarat - DPPK Rembau (Multi-Template)", layout="centered")
st.title("Sistem Minit Mesyuarat — Dewan Pemuda PAS Kawasan Rembau")
st.write("Pilih template mesyuarat → isi borang → klik **Generate PDF** untuk muat turun minit mengikut format rasmi.")

# --- Template selection ---
template = st.selectbox("Pilih Template Mesyuarat", ["Harian", "EXCO"])

# --- Common header inputs ---
with st.expander("Maklumat Umum Mesyuarat", expanded=True):
    bil = st.text_input("BIL. (contoh: 3)", value="")
    tarikh = st.date_input("Tarikh", value=date.today())
    masa = st.text_input("Masa", value="9:00 PM")
    tempat = st.text_input("Tempat", value="Pejabat DPPK Rembau / Online")
    nama_su = st.text_input("Nama SU (Disediakan oleh)", value="")
    

    
    

# ======== Kehadiran Automasuk – Pilih Nama, Pilih Hadir/X ========
st.markdown("### Kehadiran AJK")

AJK_LIST = [
    "Ketua Pemuda - Irsyad",
    "Timbalan Ketua Pemuda - Zafreen",
    "Naib Ketua Pemuda - Rahman",
    "Setiausaha - Hakim",
    "Penolong Setiausaha - Naim",
    "Bendahari - Izzuddin",
    "Penerangan - Afiq Asnawi",
    "Jabatan Pembangunan Remaja - Muzammil",
    "Pilihanraya & Kebajikan - Ma’az",
    "Aktar - Arif Aiman",
    "Jabatan Amal - Umair",
    "Dakwah - Ust Zaid",
    "Ketua DACS - Adhwa",
    "Timbalan Ketua DACS - Azmil",
    "Ekonomi - Aman"
]

att_rows = []

for i, ajk in enumerate(AJK_LIST):
    jawatan, nama = ajk.split(" - ")

    c1, c2, c3, c4, c5 = st.columns([1, 2, 3, 1, 2])

    hadir = c4.selectbox(
        f"Hadir {nama}",
        options=["/", "X"],
        key=f"hadir_{i}"
    )

    catatan = c5.text_input(f"Catatan {nama}", key=f"catatan_{i}")

    att_rows.append({
        "no": str(i+1),
        "jawatan": jawatan,
        "nama": nama,
        "hadir": hadir,
        "cat": catatan
    })

# ======== Agenda Input ========
st.markdown("### Agenda")
num_agenda = st.number_input("Bilangan Agenda", min_value=1, max_value=30, value=5, step=1)


agenda = []
for i in range(int(num_agenda)):
    title = st.text_input(f"Agenda {i+1} Tajuk", key=f"agenda_title_{i}")
    notes = st.text_area(f"Perbincangan & Keputusan untuk Agenda {i+1} (boleh tulis berlapis: 1.1, 1.1.1, ...)", key=f"agenda_notes_{i}")
    agenda.append({"title": title, "notes": notes})




# ======== Hal-hal berbangkit dan Penutup ========
hal_berbangkit = st.text_area("Hal-hal Berbangkit (6.x)", value="")
penutup = st.text_area(
    "Penutup",
    value="Mesyuarat diakhiri dengan tasbih kafarah & Surah Al-Asr"
)

# ======== Helper: Logo scaling ========
def get_reportlab_image(file, max_width_mm=30):
    if not file:
        return None
    img = PILImage.open(file)
    max_w_px = int(max_width_mm * (72/25.4))
    w, h = img.size
    if w > max_w_px:
        ratio = max_w_px / w
        img = img.resize((int(w*ratio), int(h*ratio)))
    bio = BytesIO()
    img.save(bio, format='PNG')
    bio.seek(0)
    return bio


# ======== PDF Builder ========
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=18*mm, leftMargin=18*mm,
                            topMargin=18*mm, bottomMargin=18*mm)
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    h1 = ParagraphStyle(name='CenterTitle', fontSize=12, leading=14, alignment=1, spaceAfter=6)
    h2 = ParagraphStyle(name='SmallBold', fontSize=10, leading=12, spaceAfter=4)
    elems = []

    # Header
    if logo_file is not None:
        img_bio = get_reportlab_image(logo_file, max_width_mm=30)
        if img_bio:
            img = Image(img_bio)
            img.drawHeight = 22*mm
            elems.append(img)

    elems.append(Paragraph("Jabatan Setiausaha", h1))
    elems.append(Paragraph("Dewan Pemuda PAS Kawasan Rembau", h1))
    elems.append(Paragraph("<b>MINIT MESYUARAT AHLI JAWATANKUASA</b>", h1))
    bil_text = bil.strip() or "___"
    elems.append(Paragraph(f"<b>BIL. {bil_text} / 2025–2027</b>", h1))
    elems.append(Spacer(1,6))

    meta = [
        ["Tarikh:", tarikh.strftime("%d %B %Y")],
        ["Masa:", masa],
        ["Tempat:", tempat]
    ]
    mt = Table(meta, colWidths=[40*mm, 110*mm])
    elems.append(mt)
    elems.append(Spacer(1,6))

    # Kehadiran table
    elems.append(Paragraph("<b>KEHADIRAN</b>", h2))
    table_data = [["No","Jawatan","Nama","Hadir","Catatan"]]
    for r in att_rows:
        table_data.append([r["no"], r["jawatan"], r["nama"], r["hadir"], r["cat"]])

    tbl = Table(table_data, colWidths=[12*mm, 70*mm, 40*mm, 18*mm, 30*mm])
    tbl.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),0.4,colors.grey),
        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE')
    ]))
    elems.append(tbl)
    elems.append(Spacer(1,4))

    # Auto jumlah kehadiran
    jumlah_kehadiran_auto = sum(1 for r in att_rows if r["hadir"] == "/")
    elems.append(Paragraph(f"Jumlah kehadiran : {jumlah_kehadiran_auto} / {len(att_rows)}", normal))
    elems.append(Spacer(1,8))

    # Agenda
    elems.append(Paragraph("<b>AGENDA</b>", h2))
    for i, ag in enumerate(agenda, start=1):
        elems.append(Paragraph(f"{i}) {ag['title']}", normal))
        elems.append(Spacer(1,8))

    # Perbincangan
    elems.append(Paragraph("<b>PERBINCANGAN</b>", h2))
    for idx, ag in enumerate(agenda, start=1):
        elems.append(Paragraph(f"<b>{idx}. {ag['title']}</b>", normal))
        lines = [ln.strip() for ln in (ag['notes'] or "").splitlines() if ln.strip()]
        if lines:
            for ln in lines:
                elems.append(Paragraph(ln, normal))
        else:
            elems.append(Paragraph("-", normal))
        elems.append(Spacer(1,4))

    # Hal-hal berbangkit
    elems.append(Paragraph("<b>HAL-HAL BERBANGKIT</b>", h2))
    if hal_berbangkit.strip():
        for ln in hal_berbangkit.splitlines():
            elems.append(Paragraph(ln, normal))
    else:
        elems.append(Paragraph("-", normal))
    elems.append(Spacer(1,10))

    # Penutup
    elems.append(Paragraph("<b>PENUTUP</b>", h2))
    elems.append(Paragraph(penutup or "-", normal))
    elems.append(Spacer(1,14))

    # Signature style
    signature_style = ParagraphStyle(
        name="Signature",
        fontName="Helvetica-Oblique",  # boleh tukar ke BrushScriptMT kalau font ada
        fontSize=12,
        leading=14
    )

    # Signature
    elems.append(Paragraph("Disediakan oleh:", normal))
    elems.append(Spacer(1,8))
    sign_line = "__________________________"
    elems.append(Paragraph(sign_line, normal))
    elems.append(Paragraph(f"{nama_su}", signature_style))
    elems.append(Paragraph("Setiausaha\nDewan Pemuda PAS Kawasan Rembau", normal))

    doc.build(elems)

    buffer.seek(0)
    return buffer

# ======== Generate Button ========
if st.button("Generate PDF"):
    if not nama_su:
        st.warning("Sila isi nama SU sebelum generate PDF.")

    else:
        st.success("PDF berjaya dihasilkan.")
        st.download_button(
            "Muat Turun Minit (PDF)",
    )





























