# app.py
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from PIL import Image as PILImage
from datetime import date

# Register signature font
try:
    pdfmetrics.registerFont(TTFont('MrDafoe', 'MrDafoe-Regular.ttf'))
except:
    st.warning("Font MrDafoe tidak dijumpai. Signature akan guna default font.")

# Page config
st.set_page_config(page_title="Minit Mesyuarat - DPPK Rembau", layout="centered")
st.title("Sistem Minit Mesyuarat — Dewan Pemuda PAS Kawasan Rembau")
st.write("Pilih template → isi borang → klik **Generate PDF** untuk muat turun minit mengikut format rasmi.")

# --- Template selection ---
template = st.selectbox("Pilih Template Mesyuarat", ["Harian", "EXCO"])

# --- Common header inputs ---
with st.expander("Maklumat Umum Mesyuarat", expanded=True):
    bil = st.text_input("BIL. (contoh: 3)", value="")
    tarikh = st.date_input("Tarikh", value=date.today())
    masa = st.text_input("Masa", value="9:00 PM")
    tempat = st.text_input("Tempat", value="")
    nama_anda = st.text_input("Disediakan oleh", value="")
    jawatan_anda = st.text_input("Jawatan", value="")
    sign_anda = st.text_input("Nama Sign", value="")
    bg_file = st.file_uploader("Upload Letterhead (PNG)", type=["png"])

# --- Kehadiran AJK ---
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
    hadir = c4.selectbox(f"Hadir {nama}", options=["/", "X"], key=f"hadir_{i}")
    catatan = c5.text_input(f"Catatan {nama}", key=f"catatan_{i}")
    att_rows.append({"no": str(i+1), "jawatan": jawatan, "nama": nama, "hadir": hadir, "cat": catatan})

# --- Agenda ---
st.markdown("### Agenda")
num_agenda = st.number_input("Bilangan Agenda", min_value=1, max_value=30, value=5, step=1)
agenda = []
for i in range(int(num_agenda)):
    title = st.text_input(f"Agenda {i+1}", key=f"agenda_title_{i}")
    notes = st.text_area(f"Perbincangan & Keputusan untuk Agenda {i+1}", key=f"agenda_notes_{i}")
    agenda.append({"title": title, "notes": notes})

# --- Hal-hal berbangkit dan Penutup ---
hal_berbangkit = st.text_area("Hal-hal Berbangkit", value="")
penutup = st.text_area("Penutup", value="Mesyuarat diakhiri dengan tasbih kafarah & Surah Al-Asr")

# --- Function add letterhead ---
def add_letterhead(file):
    if not file:
        return None
    try:
        img = PILImage.open(file)
        orig_width, orig_height = img.size
        max_width = 500
        scale = max_width / orig_width
        new_width = max_width
        new_height = int(orig_height * scale)
        return Image(file, width=new_width, height=new_height)
    except:
        return None

# --- Build PDF ---
def build_pdf():
    buffer = BytesIO()
    pdf = None
    try:
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=18*mm, leftMargin=18*mm,
                                topMargin=18*mm, bottomMargin=18*mm)
        elements = []

        # Letterhead
        letter = add_letterhead(bg_file)
        if letter is not None:
            elements.append(letter)
            elements.append(Spacer(1, 10))

        # Header
        styles = getSampleStyleSheet()
        normal = styles['Normal']
        h1 = ParagraphStyle(name='CenterTitle', fontSize=12, leading=14, alignment=1, spaceAfter=6)
        h2 = ParagraphStyle(name='SmallBold', fontSize=10, leading=12, spaceAfter=4)

        elements.append(Paragraph("Jabatan Setiausaha", h1))
        elements.append(Paragraph("Dewan Pemuda PAS Kawasan Rembau", h1))
        elements.append(Paragraph("<b>MINIT MESYUARAT AHLI JAWATANKUASA</b>", h1))
        bil_text = bil.strip() or "___"
        elements.append(Paragraph(f"<b>BIL. {bil_text} / 2025–2027</b>", h1))
        elements.append(Spacer(1,6))

        # Meta
        meta = [["Tarikh:", tarikh.strftime("%d %B %Y")], ["Masa:", masa], ["Tempat:", tempat]]
        mt = Table(meta, colWidths=[40*mm, 110*mm])
        elements.append(mt)
        elements.append(Spacer(1,6))

        # Kehadiran
        elements.append(Paragraph("<b>KEHADIRAN</b>", h2))
        table_data = [["No","Jawatan","Nama","Hadir","Catatan"]]
        for r in att_rows:
            table_data.append([r["no"], r["jawatan"], r["nama"], r["hadir"], r["cat"]])
        tbl = Table(table_data, colWidths=[12*mm, 70*mm, 40*mm, 18*mm, 30*mm])
        tbl.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.4,colors.grey),
                                 ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
                                 ('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
        elements.append(tbl)
        elements.append(Spacer(1,4))
        jumlah_kehadiran_auto = sum(1 for r in att_rows if r["hadir"] == "/")
        elements.append(Paragraph(f"Jumlah kehadiran : {jumlah_kehadiran_auto} / {len(att_rows)}", normal))
        elements.append(Spacer(1,8))

        # Agenda & perbincangan
        elements.append(Paragraph("<b>AGENDA</b>", h2))
        for i, ag in enumerate(agenda, start=1):
            elements.append(Paragraph(f"{i}) {ag['title']}", normal))
            elements.append(Spacer(1,4))

        elements.append(Paragraph("<b>PERBINCANGAN</b>", h2))
        for idx, ag in enumerate(agenda, start=1):
            elements.append(Paragraph(f"<b>{idx}. {ag['title']}</b>", normal))
            lines = [ln.strip() for ln in (ag['notes'] or "").splitlines() if ln.strip()]
            if lines:
                for ln in lines:
                    elements.append(Paragraph(ln, normal))
            else:
                elements.append(Paragraph("-", normal))
            elements.append(Spacer(1,4))

        # Hal-hal berbangkit
        elements.append(Paragraph("<b>HAL-HAL BERBANGKIT</b>", h2))
        if hal_berbangkit.strip():
            for ln in hal_berbangkit.splitlines():
                elements.append(Paragraph(ln, normal))
        else:
            elements.append(Paragraph("-", normal))
        elements.append(Spacer(1,10))

        # Penutup
        elements.append(Paragraph("<b>PENUTUP</b>", h2))
        elements.append(Paragraph(penutup or "-", normal))
        elements.append(Spacer(1,14))

        # Signature
        signature_style = ParagraphStyle(name="Signature", fontName="MrDafoe", fontSize=25, leading=14)
        elements.append(Paragraph("Disediakan oleh:", normal))
        elements.append(Spacer(1,20))
        elements.append(Paragraph(f"<b>{sign_anda}</b>", signature_style))
        elements.append(Paragraph("____________________", normal))
        elements.append(Paragraph(f"<b>{nama_anda.upper()}</b>", normal))
        elements.append(Paragraph(f"<b>{jawatan_anda.upper()}</b>", normal))

        # Build PDF
        doc.build(elements)
        pdf = buffer.getvalue()

    except Exception as e:
        st.error(f"Gagal generate PDF: {e}")
        pdf = None
    finally:
        buffer.close()

    return pdf

# --- Generate Button ---
if st.button("Generate PDF"):
    if not all([bil, tarikh, masa, tempat, nama_anda, jawatan_anda, sign_anda]):
        st.warning("Sila lengkapkan semua maklumat.")
    else:
        pdf_output = build_pdf()
        if pdf_output:
            st.success("PDF berjaya dihasilkan.")
            st.download_button("Muat Turun Minit (PDF)", data=pdf_output,
                               file_name=f"minit_BIL{bil or 'x'}_{tarikh}.pdf",
                               mime="application/pdf")
        else:
            st.error("PDF gagal dijana. Sila semak input / font / gambar.")
