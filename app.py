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
    tarikh = st.date_input("Tarikh :", value=date.today())
    masa = st.text_input("Masa : (contoh: 9 pm)", value="")
    tempat = st.text_input("Tempat/Platform :", value="")
    nama_anda = st.text_input("Disediakan oleh : (contoh: Muhammad Hakim bin Mokhtar)", value="")
    jawatan_anda = st.text_input("Jawatan : (contoh: Setiausaha DPPKR)", value="")
    sign_anda = st.text_input("Nama Sign : (contoh: hakim)", value="")
    letterhead_image = st.file_uploader("Upload Letterhead (PNG)", type=["png"])


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
    notes = st.text_area(f"Perbincangan & Keputusan untuk Agenda {i+1} (boleh tulis berlapis: 1.1, 1.1.1, ...)", key=f"agenda_notes_{i}")
    agenda.append({"title": title, "notes": notes})




# ======== Hal-hal berbangkit dan Penutup ========
hal_berbangkit = st.text_area("Hal-hal Berbangkit", value="")
penutup = st.text_area(
    "Penutup",
    value="Mesyuarat diakhiri dengan tasbih kafarah & Surah Al-Asr"
)


# ======== PDF Builder ========

def build_pdf(logo_file=None, letterhead=None):
    buffer = BytesIO()

    # create canvas
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # ============= LETTERHEAD BACKGROUND =============
    if letterhead is not None:
        bg = ImageReader(letterhead)
        c.drawImage(bg, 0, 0, width=width, height=height)

    # ============= MULAKAN TULISAN =============  
    text = c.beginText(40, height - 120)
    text.setFont("Helvetica", 11)

    text.textLine("Jabatan Setiausaha")
    text.textLine("Dewan Pemuda PAS Kawasan Rembau")
    text.textLine(f"MINIT MESYUARAT AJK — BIL {bil}")

    text.textLine("")
    text.textLine(f"Tarikh : {tarikh.strftime('%d %B %Y')}")
    text.textLine(f"Masa   : {masa}")
    text.textLine(f"Tempat : {tempat}")
    text.textLine("")

    # KEHADIRAN
    text.textLine("KEHADIRAN:")
    for r in att_rows:
        text.textLine(f"{r['no']}. {r['jawatan']} - {r['nama']} [{r['hadir']}]")

    # AGENDA
    text.textLine("")
    text.textLine("AGENDA:")
    for i, ag in enumerate(agenda, start=1):
        text.textLine(f"{i}. {ag['title']}")

    # PENUTUP
    text.textLine("")
    text.textLine("PENUTUP:")
    text.textLine(penutup)

    # SIGNATURE
    text.textLine("")
    text.textLine("Disediakan oleh,")
    text.textLine("")
    text.textLine(nama_su)

    c.drawText(text)
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer

    elems = []

    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader

    # --- Semua content minit ----
    elems.append(Paragraph("Jabatan Setiausaha", h1))
    elems.append(Paragraph("Dewan Pemuda PAS Kawasan Rembau", h1))
    elems.append(Paragraph("<b>MINIT MESYUARAT</b>", h1))
    # … (SEMUA kod minit kekal seperti biasa)

    doc.build(elems)
    buffer.seek(0)
    return buffer

    def merge_with_letterhead(body_pdf, letterhead_pdf):
        letter = PdfReader(letterhead_pdf)
        body = PdfReader(body_pdf)

        writer = PdfWriter()

        # Page 1: merge
        first_letter = letter.pages[0]
        first_body = body.pages[0]

        PageMerge(first_letter).add(first_body).render()
        writer.addpage(first_letter)

        # Page 2+
        for page in body.pages[1:]:
            writer.addpage(page)

        out = BytesIO()
        writer.write(out)
        out.seek(0)
        return out


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
        fontSize=20,
        leading=14
    )

    # Signature
    elems.append(Paragraph("Disediakan oleh:", normal))
    elems.append(Spacer(1,20))
    elems.append(Paragraph(f"<b>{sign_anda}</b>", signature_style))
    sign_line = "________________"
    elems.append(Paragraph(sign_line, normal))
    elems.append(Spacer(1,8))
    elems.append(Paragraph(f"<b>{nama_anda}</b>", normal))
    elems.append(Paragraph(f"<b>{jawatan_anda}</b>", normal))

    doc.build(elems)
    buffer.seek(0)
    return buffer

# ======== Generate Button ========
if st.button("Generate PDF"):
    if not all([bil, tarikh, masa, tempat, nama_anda, jawatan_anda, sign_anda]):
        st.warning("Sila lengkapkan semua maklumat.")
    
    else:
        pdf_buf = build_pdf(letterhead_image)
        st.success("PDF berjaya.")
        st.download_button(
            "Muat Turun Minit",
            data=pdf_buf.getvalue(),
            file_name="minit.pdf",
            mime="application/pdf"
        )







































































