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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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
    tempat = st.text_input("Tempat", value="")
    nama_anda = st.text_input("Disediakan oleh (contoh: Muhammad Hakim bin Mokhtar)", value="")
    jawatan_anda = st.text_input("Jawatan (contoh: Setiausaha DPPKR)", value="")
    sign_anda = st.text_input("Nama Sign (contoh: Hakim)", value="")
    bg_file = st.file_uploader("", type=["png"])

    
    

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
    title = st.text_input(f"Agenda {i+1}", key=f"agenda_title_{i}")
    notes = st.text_area(f"Perbincangan & Keputusan untuk Agenda {i+1} (boleh tulis berlapis: {i+1}.1, {i+1}.1.1, ...)", key=f"agenda_notes_{i}")
    agenda.append({"title": title, "notes": notes})




# ======== Hal-hal berbangkit dan Penutup ========
hal_berbangkit = st.text_area("Hal-hal Berbangkit", value="")
penutup = st.text_area(
    "Penutup",
    value="Mesyuarat diakhiri dengan tasbih kafarah & Surah Al-Asr"
)


# ======== PDF Builder ========

def draw_bg(canvas, doc, bg_file):
    if bg_file is None:
        return

    canvas.saveState()
    canvas.drawImage(
        bg_file, 
        0, 0,
        width=A4[0],
        height=A4[1],
        preserveAspectRatio=True,
        mask='auto'
    )
    canvas.restoreState()

def draw_bg(canvas, doc, bg_file):
    if bg_file is None:
        return
    canvas.saveState()
    canvas.drawImage(bg_file, 0, 0, width=A4[0], height=A4[1])
    canvas.restoreState()
def build_pdf(logo_file=None, bg_file=None):
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
        fontName="MrDafoe-Regular.ttf",  # boleh tukar ke BrushScriptMT kalau font ada
        fontSize=25,
        leading=14
    )

    # Signature
    elems.append(Paragraph("Disediakan oleh:", normal))
    elems.append(Spacer(1,20))
    elems.append(Paragraph(f"<b>{sign_anda}</b>", signature_style))
    sign_line = "_ _ _ _ _ _ _ _ _ _"
    elems.append(Paragraph(sign_line, normal))
    elems.append(Paragraph(f"<b>{nama_anda}</b>", normal))
    elems.append(Paragraph(f"<b>{jawatan_anda}</b>", normal))

    doc.build(
    elems, 
    onFirstPage=lambda c, d: draw_bg(c, d, bg_file),
    onLaterPages=lambda c, d: draw_bg(c, d, bg_file)
)

    buffer.seek(0)
    return buffer

# ======== Generate Button ========
if st.button("Generate PDF"):
    if not nama_anda:
        st.warning("Sila isi nama SU sebelum generate PDF.")

    else:
        pdf_buf = build_pdf(logo_file=None, bg_file=None)
        st.success("PDF berjaya dihasilkan.")
        st.download_button("Muat Turun Minit (PDF)", data=pdf_buf,
                           file_name=f"minit_BIL{bil or 'x'}_{tarikh}.pdf", mime="application/pdf")































