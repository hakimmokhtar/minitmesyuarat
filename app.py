# app.py
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from io import BytesIO
from datetime import date
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage

# Register font untuk signature
pdfmetrics.registerFont(TTFont('MrDafoe', 'MrDafoe-Regular.ttf'))

# ============================
#   PAGE SETTINGS
# ============================
st.set_page_config(page_title="Sistem Minit Mesyuarat — DPPKR", layout="centered")
st.title("Sistem Minit Mesyuarat — Dewan Pemuda PAS Kawasan Rembau")

# ============================
#   MULTI TEMPLATE SYSTEM
# ============================
TEMPLATES = {

    "Harian DPPKR": {
        "header_title": "MINIT MESYUARAT HARIAN DPPK REMBAU",
        "ajk_list": [
            "Ketua Pemuda - Irsyad",
            "Timbalan Ketua Pemuda - Zafreen",
            "Naib Ketua Pemuda - Rahman",
            "Setiausaha - Hakim",
            "Penolong Setiausaha - Naim",
            "Bendahari - Izzuddin",
        ],
        "default_agenda": [
            "Pembentangan Minit Lalu",
            "Perkara Berbangkit",
            "Makluman / Laporan",
            "Hal-hal Lain"
        ]
    },

    "EXCO DPPKR": {
        "header_title": "MESYUARAT EXCO DPPK REMBAU",
        "ajk_list": [
            "Ketua Pemuda - Irsyad",
            "Timbalan Ketua Pemuda - Zafreen",
            "Naib Ketua Pemuda - Rahman",
            "Setiausaha - Hakim",
            "Penolong Setiausaha - Naim",
            "Bendahari - Izzuddin",
            "Penerangan - Afiq",
            "Dakwah - Ust Zaid",
            "Amal - Umair",
        ],
        "default_agenda": [
            "Ucapan Pengerusi",
            "Laporan Setiausaha",
            "Laporan Bendahari",
            "Laporan Lajnah",
            "Hal-hal Lain"
        ]
    },

    "Lajnah Pengurusan": {
        "header_title": "MESYUARAT LAJNAH PENGURUSAN",
        "ajk_list": [
            "Pengarah - Zafreen",
            "Setiausaha - Hakim",
            "AJK - Naim",
        ],
        "default_agenda": [
            "Pelaksanaan Program",
            "Perancangan Kewangan",
            "Kemaskini Dokumen Rasmi",
        ]
    },

    "Lajnah Dakwah": {
        "header_title": "MESYUARAT LAJNAH DAKWAH",
        "ajk_list": [
            "Pengarah Dakwah - Ust Zaid",
            "Setiausaha - Hakim",
            "AJK - Azmil",
        ],
        "default_agenda": [
            "Tarbiah",
            "Kuliah / Ceramah",
            "Ziarah",
            "Hal-hal Lain"
        ]
    },

    "Lajnah Amal": {
        "header_title": "MESYUARAT JABATAN AMAL",
        "ajk_list": [
            "Pengarah Amal - Umair",
            "Setiausaha - Hakim",
            "AJK - Rahman",
        ],
        "default_agenda": [
            "Latihan Amal",
            "Kebajikan",
            "Bantuan Kecemasan",
        ]
    },

    "Lajnah Penerangan": {
        "header_title": "MESYUARAT LAJNAH PENERANGAN",
        "ajk_list": [
            "Ketua Penerangan - Afiq",
            "Setiausaha - Hakim",
            "AJK Media - Aman",
        ],
        "default_agenda": [
            "Media Sosial",
            "Siaran Berita",
            "Reka Grafik / Video",
            "Hal-hal Lain"
        ]
    }

}

# ============================
#   PILIH TEMPLATE
# ============================
template_name = st.selectbox("Pilih Template Mesyuarat", list(TEMPLATES.keys()))
config = TEMPLATES[template_name]

# ============================
#   MAKLUMAT MESYUARAT
# ============================
st.subheader("Maklumat Mesyuarat")

tarikh = st.date_input("Tarikh Mesyuarat", value=date.today())
masa = st.text_input("Masa Mesyuarat", "9:00 malam").upper()
tempat = st.text_input("Tempat Mesyuarat", "Pejabat PAS Rembau").upper()
pengerusi = st.text_input("Pengerusi Mesyuarat", "KETUA PEMUDA").upper()

# ============================
#   SENARAI KEHADIRAN
# ============================
st.write("---")
st.subheader("Senarai Kehadiran")

status_options = ["HADIR", "X"]
kehadiran = {}

for item in config["ajk_list"]:
    nama, jawatan = item.split(" - ")
    col1, col2, col3 = st.columns([3, 2, 2])

    with col1:
        st.text_input(f"Nama ({jawatan})", value=nama, key=f"nama_{nama}", disabled=True)

    with col2:
        st.text_input("Jawatan", value=jawatan, key=f"jawatan_{nama}", disabled=True)

    with col3:
        kehadiran[nama] = st.selectbox("Status", status_options, key=f"status_{nama}")

# ============================
#   AGENDA
# ============================
st.write("---")
st.subheader("Agenda Mesyuarat")

agenda_list = []

st.markdown("### Agenda Default")
for ag in config["default_agenda"]:
    agenda_list.append(st.text_input(f"Agenda:", value=ag, key=f"agenda_{ag}").upper())

st.markdown("### Agenda Tambahan")
extra_count = st.number_input("Bilangan Agenda Tambahan", 0, 10, 0)

for i in range(extra_count):
    extra = st.text_input(f"Agenda Tambahan {i+1}").upper()
    if extra.strip() != "":
        agenda_list.append(extra)

# ============================
#   CATATAN
# ============================
st.write("---")
st.subheader("Catatan / Hal-hal Lain")
catatan = st.text_area("Catatan", "").upper()

# ============================
#   PDF GENERATOR
# ============================
def add_letterhead():
    try:
        img = PILImage.open("letterhead.png")
        orig_width, orig_height = img.size

        # Lebar PDF (A4) dalam pixel approx
        max_width = 500  

        # Kira ratio untuk kekalkan bentuk asal
        scale = max_width / orig_width
        new_width = max_width
        new_height = int(orig_height * scale)

        return Image("letterhead.png", width=new_width, height=new_height)
        
    except:
        return None

def build_pdf():
    buffer = BytesIO()
    try:
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=30, leftMargin=30,
                                topMargin=40, bottomMargin=30)

        elements = []

        # Letterhead
        letter = add_letterhead()
        if letter is not None:
            elements.append(letter)
            elements.append(Spacer(1,10))

        # Contoh tambah text
        elements.append(Paragraph("TEST PDF", getSampleStyleSheet()["Normal"]))

        # Build PDF
        doc.build(elements)

        # Ambil content PDF
        pdf = buffer.getvalue()

    except Exception as e:
        st.error(f"Error semasa build PDF: {e}")
        pdf = None

    finally:
        buffer.close()

    return pdf

    
    # Letterhead

    letter = add_letterhead()
    if letter:
        elements.append(letter)
        elements.append(Spacer(1, 10))
        
    
    # Tajuk
    elements.append(Paragraph(f"<b>{config['header_title']}</b>", bold_center))
    elements.append(Spacer(1, 10))

    # Info Mesyuarat
    info_text = f"""
    <b>Tarikh:</b> {tarikh.strftime('%d/%m/%Y')}<br/>
    <b>Masa:</b> {masa}<br/>
    <b>Tempat:</b> {tempat}<br/>
    <b>Pengerusi:</b> {pengerusi}<br/>
    """
    elements.append(Paragraph(info_text.upper(), normal))
    elements.append(Spacer(1, 15))

    # Kehadiran Table
    elements.append(Paragraph("<b>SENARAI KEHADIRAN</b>", normal))
    elements.append(Spacer(1, 5))

    table_data = [["NAMA", "JAWATAN", "STATUS"]]

    for item in config["ajk_list"]:
        nama, jawatan = item.split(" - ")
        table_data.append([nama.upper(), jawatan.upper(), kehadiran[nama]])

    table = Table(table_data, colWidths=[180, 150, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.8, colors.black),
        ("ALIGN", (2,1), (2,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 15))

    # Agenda
    elements.append(Paragraph("<b>AGENDA MESYUARAT</b>", normal))
    elements.append(Spacer(1, 5))

    for i, ag in enumerate(agenda_list, start=1):
        elements.append(Paragraph(f"{i}. {ag}", normal))
        elements.append(Spacer(1, 3))

    elements.append(Spacer(1, 15))

    # Catatan
    if catatan.strip() != "":
        elements.append(Paragraph("<b>CATATAN / HAL-HAL LAIN</b>", normal))
        elements.append(Paragraph(catatan.upper(), normal))
        elements.append(Spacer(1, 20))

    # Signature
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Disediakan oleh,", normal))
    elements.append(Spacer(1, 45))

    signature_html = f"""
    <font name='MrDafoe' size='24'>{pengerusi.title()}</font><br/>
    <b>Pengerusi Mesyuarat</b>
    """
    elements.append(Paragraph(signature_html, ParagraphStyle("sig", alignment=0)))
    elements.append(Spacer(1, 20))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

# ============================
#   DOWNLOAD BUTTON
# ============================
st.write("## Muat Turun Dokumen")

if st.button("Generate PDF Minit Mesyuarat"):
    pdf_output = build_pdf()
    st.success("PDF berjaya dijana!")

    st.download_button(
        label="📄 Download PDF",
        data=pdf_output,
        file_name=f"minit_mesyuarat_{tarikh}.pdf",
        mime="application/pdf"
    )







