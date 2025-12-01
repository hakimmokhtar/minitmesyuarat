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
template = st.selectbox("Pilih Template Mesyuarat", ["Harian", "EXCO",])

# --- Common header inputs ---
with st.expander("Maklumat Umum Mesyuarat", expanded=True):
    bil = st.text_input("BIL. (contoh: 3)", value="")
    tarikh = st.date_input("Tarikh", value=date.today())
    masa = st.text_input("Masa", value="9:00 PM")
    tempat = st.text_input("Tempat", value="Pejabat DPPK Rembau / Online")
    pengerusi = st.text_input("Pengerusi", value="")
    nama_su = st.text_input("Nama SU (Disediakan oleh)", value="")
    logo_file = st.file_uploader("Muat naik logo (png/jpg)", type=["png","jpg","jpeg"])

# --- Attendance table input (flexible rows) ---
st.markdown("### Kehadiran")
num_rows = st.number_input("Bilangan baris untuk jadual kehadiran", min_value=1, max_value=40, value=8, step=1)
att_rows = []
cols = st.columns([1,2,3,1,2])
st.write("Isikan jadual : No | Jawatan | Nama | Hadir (/) | Catatan")
for i in range(int(num_rows)):
    c1, c2, c3, c4, c5 = st.columns([1,2,3,1,2])
    no = c1.text_input(f"No {i+1}", value=str(i+1), key=f"no_{i}")
    jawatan = c2.text_input(f"Jawatan {i+1}", key=f"jawatan_{i}")
    nama = c3.text_input(f"Nama {i+1}", key=f"nama_{i}")
    hadir = c4.text_input(f"Hadir {i+1}", key=f"hadir_{i}")
    cat = c5.text_input(f"Catatan {i+1}", key=f"cat_{i}")
    att_rows.append({"no": no, "jawatan": jawatan, "nama": nama, "hadir": hadir, "cat": cat})

jumlah_kehadiran = st.text_input("Jumlah kehadiran (contoh: 12 / 15)", value="")

# --- Agenda input (dynamic) ---
st.markdown("### Agenda")
num_agenda = st.number_input("Bilangan Agenda", min_value=1, max_value=30, value=5, step=1)
agenda = []
for i in range(int(num_agenda)):
    title = st.text_input(f"Agenda {i+1} Tajuk", key=f"agenda_title_{i}")
    # For DPPKR-style, allow multi-level notes per agenda
    notes = st.text_area(f"Perbincangan & Keputusan untuk Agenda {i+1} (boleh tulis berlapis: 1.1, 1.1.1, ...)", key=f"agenda_notes_{i}")
    agenda.append({"title": title, "notes": notes})

# --- Template specific extras ---
if template == "Retreat / Program Planning":
    retreat_notes = st.text_area("Butiran Perancangan Retreat (PIC, Tarikh, Tugasan)", value="")
if template == "Mesyuarat Lajnah":
    lajnah_notes = st.text_area("Butiran khusus lajnah (aktiviti dan laporan)", value="")

# --- Hal-hal berbangkit & Penutup ---
hal_berbangkit = st.text_area("Hal-hal Berbangkit (6.x)", value="")
penutup = st.text_area("Penutup (contoh: Mesyuarat diakhiri dengan tasbih kafarah & Surah Al-Asr)", value="Mesyuarat diakhiri dengan tasbih kafarah & Surah Al-Asr")

# --- Helper for logo image scaling ---
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

# --- PDF builder ---
def build_pdf():
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
    if logo_file:
        img_bio = get_reportlab_image(logo_file, max_width_mm=30)
        if img_bio:
            img = Image(img_bio)
            img.drawHeight = 22*mm
            elems.append(img)

    elems.append(Paragraph("Jabatan Setiausaha", h1))
    elems.append(Paragraph("Dewan Pemuda PAS Kawasan Rembau", h1))
    elems.append(Paragraph("<b>MINIT MESYUARAT AHLI JAWATANKUASA</b>", h1))
    bil_text = bil.strip() or "___"
    elems.append(Paragraph(f"<b>DEWAN PEMUDA PAS KAWASAN REMBAU</b>", h1))
    elems.append(Paragraph(f"<b>BIL. {bil_text} / 2025–2027</b>", h1))
    elems.append(Spacer(1,6))

    # Meta table
    meta = [
        ["Tarikh:", tarikh.strftime("%d %B %Y")],
        ["Masa:", masa],
        ["Tempat:", tempat],
        ["Pengerusi:", pengerusi]
    ]
    mt = Table(meta, colWidths=[40*mm, 110*mm])
    mt.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP')]))
    elems.append(mt)
    elems.append(Spacer(1,6))

    # Kehadiran table
    elems.append(Paragraph("<b>KEHADIRAN</b>", h2))
    table_data = [["No","Jawatan","Nama","Hadir","Catatan"]]
    for r in att_rows:
        table_data.append([r['no'] or "-", r['jawatan'] or "-", r['nama'] or "-", r['hadir'] or "-", r['cat'] or "-"])
    tbl = Table(table_data, colWidths=[12*mm, 40*mm, 70*mm, 18*mm, 30*mm])
    tbl.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),0.4,colors.grey),
        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE')
    ]))
    elems.append(tbl)
    elems.append(Spacer(1,4))
    elems.append(Paragraph(f"Jumlah kehadiran : {jumlah_kehadiran or '-'}", normal))
    elems.append(Spacer(1,8))

    # Agenda list
    elems.append(Paragraph("<b>AGENDA</b>", h2))
    for i, ag in enumerate(agenda, start=1):
        elems.append(Paragraph(f"{i}) {ag['title'] or '-'}", normal))
    elems.append(Spacer(1,8))

    # Detailed discussion per template (structured numbering)
    elems.append(Paragraph("<b>PERBINCANGAN</b>", h2))
    # For AJK template mimic DPPKR numbering & sections
    # We'll create sections based on content: 1,2,3,... with subpoints in notes text
    for idx, ag in enumerate(agenda, start=1):
        # show section header like "1. <TITLE>"
        elems.append(Paragraph(f"<b>{idx}. {ag['title'] or '-'}</b>", normal))
        # Parse notes: user can put line breaks to represent 1.1, 1.1.1 etc.
        notes = ag['notes'] or ""
        lines = [ln.strip() for ln in notes.splitlines() if ln.strip()]
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
            if ln.strip():
                elems.append(Paragraph(ln.strip(), normal))
    else:
        elems.append(Paragraph("-", normal))
    elems.append(Spacer(1,8))

    # Retreat/Lajnah extras
    if template == "Retreat / Program Planning":
        elems.append(Paragraph("<b>RETREAT - PERINCIAN</b>", h2))
        elems.append(Paragraph(retreat_notes or "-", normal))
        elems.append(Spacer(1,8))
    if template == "Mesyuarat Lajnah":
        elems.append(Paragraph("<b>LAJNAH - PERINCIAN</b>", h2))
        elems.append(Paragraph(lajnah_notes or "-", normal))
        elems.append(Spacer(1,8))

    # Penutup
    elems.append(Paragraph("<b>PENUTUP</b>", h2))
    elems.append(Paragraph(penutup or "-", normal))
    elems.append(Spacer(1,14))

    # Disediakan oleh
    elems.append(Paragraph("Disediakan oleh:", normal))
    elems.append(Spacer(1,8))
    elems.append(Paragraph("…………………………………….", normal))
    elems.append(Paragraph(f"{nama_su or '-'}", normal))
    elems.append(Paragraph("Setiausaha\nDewan Pemuda PAS Kawasan Rembau", normal))

    doc.build(elems)
    buffer.seek(0)
    return buffer

# --- Generate button ---
if st.button("Generate PDF"):
    if not nama_su:
        st.warning("Sila isi nama SU sebelum generate PDF.")
    else:
        pdf_buf = build_pdf()
        st.success("PDF berjaya dihasilkan.")
        st.download_button("Muat Turun Minit (PDF)", data=pdf_buf, file_name=f"minit_BIL{bil or 'x'}_{tarikh}.pdf", mime="application/pdf")

# Optional: save JSON record locally
if st.checkbox("Simpan rekod minit (lokal JSON)"):
    import json, os
    rec = {
        "template": template,
        "bil": bil,
        "tarikh": tarikh.isoformat(),
        "masa": masa,
        "tempat": tempat,
        "pengerusi": pengerusi,
        "nama_su": nama_su,
        "kehadiran": att_rows,
        "jumlah_kehadiran": jumlah_kehadiran,
        "agenda": agenda,
        "hal_berbangkit": hal_berbangkit,
        "penutup": penutup
    }
    os.makedirs("minit_records", exist_ok=True)
    fname = f"minit_BIL{bil or 'x'}_{tarikh}.json"
    with open(f"minit_records/{fname}", "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    st.info(f"Rekod disimpan: minit_records/{fname}")

st.markdown("---")
st.write("Versi: 1.1 — Multi-Template (AJK / Lajnah / Retreat).")

