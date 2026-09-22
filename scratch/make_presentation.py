import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # completely blank layout

    # Colors
    NAVY = RGBColor(15, 32, 67)       # #0F2043 (UGM Deep Navy)
    BLUE_ACCENT = RGBColor(0, 122, 204) # #007ACC
    CYAN = RGBColor(14, 165, 233)     # #0EA5E9
    DARK_TEXT = RGBColor(30, 41, 59)  # #1E293B
    MUTED_TEXT = RGBColor(100, 116, 139) # #64748B
    WHITE = RGBColor(255, 255, 255)
    BG_LIGHT = RGBColor(248, 250, 252) # #F8FAFC
    CARD_BG = RGBColor(255, 255, 255)
    BORDER_COLOR = RGBColor(226, 232, 240)
    GREEN = RGBColor(22, 163, 74)
    AMBER = RGBColor(217, 119, 6)

    def add_header(slide, title_text, category="PROYEK INDIVIDUAL — TEKNIK ELEKTRO FT UGM"):
        # Header banner
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p_cat = tf.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = BLUE_ACCENT
        
        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = NAVY
        p_title.space_before = Pt(4)

        # Subtle bottom line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.45), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = BORDER_COLOR
        line.line.color.rgb = BORDER_COLOR

    def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=BORDER_COLOR):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
        return shape

    # ==========================================
    # SLIDE 1: Title Slide (Dark Theme)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY
    bg1.line.fill.background()

    # Title box
    tbox = s1.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.333), Inches(3.2))
    tf1 = tbox.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "LAPORAN PROGRES RISET PROYEK INDIVIDUAL"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = CYAN
    
    p2 = tf1.add_paragraph()
    p2.text = "Frequency-Constrained Unit Commitment (FCUC)\ndengan Battery Virtual Inertia dan Regulasi Frekuensi\npada Penetrasi EBT Tinggi"
    p2.font.size = Pt(26)
    p2.font.bold = True
    p2.font.color.rgb = WHITE
    p2.space_before = Pt(12)

    p3 = tf1.add_paragraph()
    p3.text = "Penyelarasan Formulasi Matematika, Pemodelan PV-WT Pengotor, & Rencana Eksekusi 4 Skenario Baru"
    p3.font.size = Pt(13)
    p3.font.color.rgb = RGBColor(203, 213, 225)
    p3.space_before = Pt(10)

    # Info card at bottom
    info_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(4.7), Inches(11.333), Inches(1.9))
    info_card.fill.solid()
    info_card.fill.fore_color.rgb = RGBColor(24, 43, 82)
    info_card.line.color.rgb = RGBColor(37, 65, 120)
    
    itf = info_card.text_frame
    itf.word_wrap = True
    itf.margin_left = Inches(0.4)
    itf.margin_top = Inches(0.25)
    
    ip1 = itf.paragraphs[0]
    ip1.text = "TIM PENELITI & PEMBIMBING:"
    ip1.font.size = Pt(10)
    ip1.font.bold = True
    ip1.font.color.rgb = CYAN
    
    ip2 = itf.add_paragraph()
    ip2.text = "• Penulis 1 (Mahasiswa): Nathaniel Benelisha (Departemen Teknik Elektro & Teknologi Informasi, FT UGM)\n" \
               "• Pendamping / Co-Mentor (S3): Muhammad Aris Risnandar, S.T., M.T. (Kandidat Doktor DTETI UGM)\n" \
               "• Dosen Pembimbing: Ir. Lesnanto Multa Putranto, S.T., M.Eng., Ph.D., IPM., ASEAN Eng., SMIEEE"
    ip2.font.size = Pt(12)
    ip2.font.color.rgb = WHITE
    ip2.space_before = Pt(4)

    # ==========================================
    # SLIDE 2: Agenda Bimbingan
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Agenda Pembahasan Progres Riset")

    agendas = [
        ("01", "Latar Belakang & Masalah", "Isu penurunan inersia kisi (low-inertia grid), risiko lonjakan RoCoF, dan keterbatasan UC klasik."),
        ("02", "Metode & Formulasi Matematis", "Pendekatan 2 tahap: Optimasi MILP (CPLEX) dan Validasi Transien Dinamis (DIgSILENT PowerFactory)."),
        ("03", "Capaian Progres Sejauh Ini", "Review 84 paper, penyelarasan matematis cost linear & PFR, serta arsip draf paper Draf 1 s.d. 5."),
        ("04", "Desain 4 Skenario Simulasi Baru", "Restrukturisasi inkremental yang elegan: Sim 1 (Baseline), Sim 2 (+BESS), Sim 3 (+BESS VI), Sim 4 (+PV-WT Pengotor)."),
        ("05", "Rencana Kerja ke Depan (5 Tahap)", "Roadmap terstruktur: Eksekusi Pyomo, Analisis Komparatif, Plot Publikasi IEEE, DIgSILENT, & Paper v3."),
        ("06", "Permohonan Arahan Pembimbing", "Diskusi penalti curtailment cost, representativitas sistem uji IEEE 24-bus, dan target publikasi.")
    ]

    for i, (num, title, desc) in enumerate(agendas):
        row = i // 3
        col = i % 3
        left = Inches(0.8 + col * 4.0)
        top = Inches(1.8 + row * 2.5)
        
        card = add_card(s2, left, top, Inches(3.733), Inches(2.2))
        ctf = card.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.3)
        ctf.margin_top = Inches(0.25)
        
        p_num = ctf.paragraphs[0]
        p_num.text = num
        p_num.font.size = Pt(22)
        p_num.font.bold = True
        p_num.font.color.rgb = BLUE_ACCENT
        
        p_t = ctf.add_paragraph()
        p_t.text = title
        p_t.font.size = Pt(14)
        p_t.font.bold = True
        p_t.font.color.rgb = NAVY
        p_t.space_before = Pt(4)
        
        p_d = ctf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = MUTED_TEXT
        p_d.space_before = Pt(6)

    # ==========================================
    # SLIDE 3: Latar Belakang & Permasalahan
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Latar Belakang: Krisis Inersia pada Kisi Tenaga Modern")

    c1 = add_card(s3, Inches(0.8), Inches(1.8), Inches(3.733), Inches(5.0))
    ctf1 = c1.text_frame
    ctf1.word_wrap = True
    ctf1.margin_left = Inches(0.35)
    ctf1.margin_top = Inches(0.3)
    p = ctf1.paragraphs[0]
    p.text = "⚡ Penetrasi EBT Skala Besar"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p_desc = ctf1.add_paragraph()
    p_desc.text = "• Transisi energi mendorong masuknya PLTS dan PLTB secara masif ke sistem tenaga listrik.\n\n" \
                 "• PLTS dan PLTB terhubung melalui konverter elektronika daya (Inverter-Based Resources / IBR).\n\n" \
                 "• IBR beroperasi secara decoupled sehingga TIDAK menyumbang inersia mekanik alamiah ke grid."
    p_desc.font.size = Pt(12)
    p_desc.font.color.rgb = DARK_TEXT
    p_desc.space_before = Pt(10)

    c2 = add_card(s3, Inches(4.8), Inches(1.8), Inches(3.733), Inches(5.0))
    ctf2 = c2.text_frame
    ctf2.word_wrap = True
    ctf2.margin_left = Inches(0.35)
    ctf2.margin_top = Inches(0.3)
    p = ctf2.paragraphs[0]
    p.text = "⚠️ Ancaman Frekuensi Sistem"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = AMBER
    p_desc = ctf2.add_paragraph()
    p_desc.text = "• Hilangnya generator sinkron menyebabkan sistem masuk ke kondisi Low-Inertia Grid.\n\n" \
                 "• RoCoF Curam: Saat terjadi gangguan N-1 trip unit terbesar, frekuensi anjlok sangat cepat (RoCoF > 0.55 Hz/s).\n\n" \
                 "• Frequency Nadir Kritis: Frekuensi merosot menembus batas UFLS (49.0 Hz), berisiko memicu pemadaman meluas (blackout)."
    p_desc.font.size = Pt(12)
    p_desc.font.color.rgb = DARK_TEXT
    p_desc.space_before = Pt(10)

    c3 = add_card(s3, Inches(8.8), Inches(1.8), Inches(3.733), Inches(5.0))
    ctf3 = c3.text_frame
    ctf3.word_wrap = True
    ctf3.margin_left = Inches(0.35)
    ctf3.margin_top = Inches(0.3)
    p = ctf3.paragraphs[0]
    p.text = "💡 Solusi: FCUC + BESS VI"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = GREEN
    p_desc = ctf3.add_paragraph()
    p_desc.text = "• Mengintegrasikan batasan frekuensi dinamik langsung ke dalam optimasi jadwal Unit Commitment (FCUC).\n\n" \
                 "• BESS Virtual Inertia (VI): Baterai grid-forming mengemulasikan respon inersia sintetis untuk menahan laju RoCoF.\n\n" \
                 "• Unit termal mahal dapat di-decommit tanpa mengorbankan stabilitas frekuensi sistem."
    p_desc.font.size = Pt(12)
    p_desc.font.color.rgb = DARK_TEXT
    p_desc.space_before = Pt(10)

    # ==========================================
    # SLIDE 4: Metode Penelitian & Sistem Uji
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Metode Penelitian: Kerangka Kerja Dua Tahap")

    c_left = add_card(s4, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
    tf_l = c_left.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = Inches(0.4)
    tf_l.margin_top = Inches(0.3)
    
    p = tf_l.paragraphs[0]
    p.text = "1. Optimasi FCUC (Pyomo MILP + CPLEX)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    
    p_l = tf_l.add_paragraph()
    p_l.text = "• Menggunakan Pyomo Modeling Environment di Python.\n" \
               "• Solver: IBM ILOG CPLEX v22.1.1 (antarmuka cplex_direct).\n" \
               "• Optimasi jadwal biner generator (u_{g,t}, y, z) dan dispatch daya kontinu (P, P_ch, P_dis, P_VI).\n" \
               "• Mempertimbangkan 10 batasan teknis generator termal, dinamika BESS SOC, inersia minimum, dan cadangan PFR droop."
    p_l.font.size = Pt(12)
    p_l.font.color.rgb = DARK_TEXT
    p_l.space_before = Pt(10)

    c_right = add_card(s4, Inches(6.8), Inches(1.8), Inches(5.733), Inches(5.0))
    tf_r = c_right.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = Inches(0.4)
    tf_r.margin_top = Inches(0.3)
    
    p = tf_r.paragraphs[0]
    p.text = "2. Validasi Transien (DIgSILENT PowerFactory)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    
    p_r = tf_r.add_paragraph()
    p_r.text = "• Jadwal komitmen unit dan tingkat pembebanan hasil CPLEX diekspor dan diimpor ke DIgSILENT.\n" \
               "• Simulasi Dinamik Domain Waktu (RMS Simulation):\n" \
               "   - Skenario N-1 Trip Generator Terbesar (Unit G1 400 MW).\n" \
               "   - Pengujian kondisi inersia minimum (jam penetrasi surya tinggi).\n" \
               "• Output: Kurva f(t), nilai riil frequency nadir, dan pembuktian kepatuhan standar grid code."
    p_r.font.size = Pt(12)
    p_r.font.color.rgb = DARK_TEXT
    p_r.space_before = Pt(10)

    # ==========================================
    # SLIDE 5: Sistem Uji IEEE 24-Bus
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Konfigurasi Sistem Uji & Data Parameter")

    # 4 metrics boxes
    metrics = [
        ("10 Unit Termal", "G1–G10 (PLTU, PLTGU, PLTG)\nTotal Kapasitas: 3.405 MW", CYAN),
        ("Beban Sistem 24 Jam", "Rata-rata: 1.168 MW\nBeban Puncak: 1.500 MW", BLUE_ACCENT),
        ("EBT Intermiten", "PLTB: 400 MW (100 x 4 MW)\nPLTS: Puncak ~200 MW", AMBER),
        ("Penyimpan BESS", "2 Unit BESS (B1 & B2)\n200 MW / 400 MWh, Eff 90%", GREEN)
    ]

    for i, (m_title, m_desc, col) in enumerate(metrics):
        b = add_card(s5, Inches(0.8 + i * 2.98), Inches(1.8), Inches(2.8), Inches(1.6))
        btf = b.text_frame
        btf.word_wrap = True
        btf.margin_left = Inches(0.2)
        btf.margin_top = Inches(0.15)
        p = btf.paragraphs[0]
        p.text = m_title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = col
        p2 = btf.add_paragraph()
        p2.text = m_desc
        p2.font.size = Pt(10)
        p2.font.color.rgb = DARK_TEXT
        p2.space_before = Pt(4)

    # Table of 10 thermal generators
    rows, cols = 11, 6
    table_shape = s5.shapes.add_table(rows, cols, Inches(0.8), Inches(3.65), Inches(11.733), Inches(3.2))
    table = table_shape.table
    table.columns[0].width = Inches(1.5)
    table.columns[1].width = Inches(2.0)
    table.columns[2].width = Inches(2.0)
    table.columns[3].width = Inches(2.0)
    table.columns[4].width = Inches(2.0)
    table.columns[5].width = Inches(2.233)

    headers = ["Unit", "Tipe Pembangkit", "Pmin (MW)", "Pmax (MW)", "Inersia H (s)", "Droop / Gov"]
    for c, h in enumerate(headers):
        cell = table.cell(0, c)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = WHITE
            p.alignment = PP_ALIGN.CENTER

    gen_data = [
        ("G1", "PLTU 1 (Coal)", "627.0", "1176.0", "5.00 s", "5.0% / Free Gov"),
        ("G2", "PLTGU 1 (CCGT)", "340.0", "1125.0", "4.00 s", "4.0% / Free Gov"),
        ("G3", "PLTU 2 (Coal)", "600.0", "969.0", "5.00 s", "5.0% / Free Gov"),
        ("G4", "PLTG 1 (Gas)", "85.0", "130.0", "3.50 s", "4.0% / Free Gov"),
        ("G5", "PLTG 2 (Gas)", "66.0", "108.0", "3.50 s", "4.0% / Free Gov"),
        ("G6", "PLTGU 2 (CCGT)", "250.0", "1095.0", "4.00 s", "4.0% / Free Gov"),
        ("G7", "PLTGU 3 (CCGT)", "248.0", "810.0", "4.00 s", "4.0% / Free Gov"),
        ("G8", "PLTGU 4 (CCGT)", "347.8", "773.0", "4.00 s", "4.0% / Free Gov"),
        ("G9", "PLTU 3 (Coal)", "540.0", "870.0", "5.00 s", "5.0% / Free Gov"),
        ("G10", "PLTU 4 (Coal)", "600.0", "840.0", "5.00 s", "5.0% / Free Gov"),
    ]

    for r, row_data in enumerate(gen_data):
        for c, val in enumerate(row_data):
            cell = table.cell(r + 1, c)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(241, 245, 249) if r % 2 == 1 else WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(10)
                p.font.color.rgb = DARK_TEXT
                p.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 6: Formulasi Kunci & Inovasi BESS VI
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Formulasi Kunci: Alokasi Konverter BESS & Keamanan Frekuensi")

    c1 = add_card(s6, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.0))
    tf1 = c1.text_frame
    tf1.word_wrap = True
    tf1.margin_left = Inches(0.4)
    tf1.margin_top = Inches(0.3)
    p = tf1.paragraphs[0]
    p.text = "1. Kopling Alokasi Konverter BESS (Headroom)"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p_b = tf1.add_paragraph()
    p_b.text = "Kapasitas inverter baterai (DR_max) diperebutkan bersama oleh daya aktif discharge dan respon inersia virtual:\n\n" \
               "   P_discharge + (P_VI / eta_VI) <= DR_max * u_dis\n\n" \
               "• Inovasi: Mencegah baterai mengklaim kapasitas ganda.\n" \
               "• BESS VI hanya dapat disuplai saat baterai tidak sedang diisi (u_dis = 1).\n" \
               "• Inersia BESS sintetis:\n" \
               "   H_batt_vi = sum( Kb_VI * P_VI_batt )"
    p_b.font.size = Pt(12)
    p_b.font.color.rgb = DARK_TEXT
    p_b.space_before = Pt(8)

    c2 = add_card(s6, Inches(6.8), Inches(1.8), Inches(5.733), Inches(5.0))
    tf2 = c2.text_frame
    tf2.word_wrap = True
    tf2.margin_left = Inches(0.4)
    tf2.margin_top = Inches(0.3)
    p = tf2.paragraphs[0]
    p.text = "2. Dua Pilar Batasan Frekuensi (RoCoF + QSS)"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p_b2 = tf2.add_paragraph()
    p_b2.text = "A. Batasan RoCoF (t = 0+ detik):\n" \
                "   2 * RoCoF_lim * H_sys >= f0 * LargestLoss\n" \
                "   -> RoCoF maksimum dibatasi 0.55 Hz/s via gabungan inersia generator sinkron & BESS VI.\n\n" \
                "B. Batasan QSS Frequency (t = 10-30 detik):\n" \
                "   LargestLoss <= (f0 - f_qss_min) * (D * Demand + TotalPFR)\n" \
                "   -> Frekuensi kuasi-tunak pasca-gangguan dijamin tetap di atas 49.5 Hz melalui cadangan PFR droop governor generator."
    p_b2.font.size = Pt(12)
    p_b2.font.color.rgb = DARK_TEXT
    p_b2.space_before = Pt(8)

    # ==========================================
    # SLIDE 7: PV & WT sebagai Pengotor vs Virtual Inertia
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Penegasan Konsep: PV & WT sebagai 'Pengotor' vs Deloading")

    c1 = add_card(s7, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.0))
    tf1 = c1.text_frame
    tf1.word_wrap = True
    tf1.margin_left = Inches(0.4)
    tf1.margin_top = Inches(0.3)
    p = tf1.paragraphs[0]
    p.text = "EBT Sebagai Penyedia VI (Deloading)"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = MUTED_TEXT
    p_b = tf1.add_paragraph()
    p_b.text = "• Bila EBT difungsikan sebagai penyedia inersia virtual (misal WT-VI):\n\n" \
               "• Turbin angin / PV harus dioperasikan menyimpang di bawah kurva MPPT optimal (deloaded mode 10-20%).\n\n" \
               "• Menyimpan cadangan kinetik rotor untuk dilepas saat frekuensi anjlok.\n\n" \
               "• Menyebabkan hilangnya energi hijau sepanjang hari (Opportunity Cost tinggi)."
    p_b.font.size = Pt(12)
    p_b.font.color.rgb = DARK_TEXT
    p_b.space_before = Pt(10)

    c2 = add_card(s7, Inches(6.8), Inches(1.8), Inches(5.733), Inches(5.0), bg_color=RGBColor(254, 243, 199), border_color=AMBER)
    tf2 = c2.text_frame
    tf2.word_wrap = True
    tf2.margin_left = Inches(0.4)
    tf2.margin_top = Inches(0.3)
    p = tf2.paragraphs[0]
    p.text = "EBT Sebagai 'Pengotor' (Riset Ini: Curtailment)"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = AMBER
    p_b2 = tf2.add_paragraph()
    p_b2.text = "• PV & WT ditegaskan MURNI sebagai pengotor (Zero Inersia).\n\n" \
                "• Beroperasi pada MPPT maksimal untuk memanen daya murah.\n\n" \
                "• Efek Pengotor: Mengikis komitmen termal sehingga inersia grid anjlok drastis.\n\n" \
                "• Mekanisme Pemotongan Daya: BUKAN deloading, melainkan CURTAILMENT jika sistem kelebihan daya / terancam krisis inersia.\n\n" \
                "• Dihitung CURTAILMENT COST sebagai penalti ekonomi:\n" \
                "   Cost_curt = sum( C_curt_wt * P_curt_wt + C_curt_pv * P_curt_pv )"
    p_b2.font.size = Pt(12)
    p_b2.font.color.rgb = DARK_TEXT
    p_b2.space_before = Pt(10)

    # ==========================================
    # SLIDE 8: Capaian Progres Sejauh Ini
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Capaian Progres Sejauh Ini (Bimbingan Bersama Mas Aris)")

    milestones = [
        ("Koleksi & Telaah Literatur", "Telah mengumpulkan dan menelaah 84 paper akademik internasional (IEEE, Elsevier), mencakup kajian fundamental BESS VI dan regulasi frekuensi primer Pak Lesnanto (ICITEE 2020).", GREEN),
        ("Perumusan Kode Pyomo MILP", "Membangun model optimasi matematis FCUC di Python Pyomo terintegrasi solver CPLEX 22.1.1 (cplex_direct) yang mampu menyelesaikan jadwal 24 jam dalam waktu hitung cepat.", GREEN),
        ("Penyelarasan Formulasi Matematis", "Memperbaiki fungsi biaya menjadi bentuk linear murni (a*u + b*P), menyelaraskan alokasi converter BESS VI headroom, dan mengisolasi VI secara tegas hanya pada BESS.", GREEN),
        ("Penyusunan Manuskrip Publikasi", "Telah menyusun naskah paper IEEEtran secara berkala dari Draf 1 hingga Draf 5 (tersedia dalam kompilasi PDF mutakhir di direktori Paper/PI_Draf5.pdf).", GREEN)
    ]

    for i, (m_t, m_d, col) in enumerate(milestones):
        card = add_card(s8, Inches(0.8), Inches(1.8 + i * 1.3), Inches(11.733), Inches(1.15))
        ctf = card.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.3)
        ctf.margin_top = Inches(0.15)
        
        p = ctf.paragraphs[0]
        p.text = f"✔ {m_t}"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = col
        
        p2 = ctf.add_paragraph()
        p2.text = m_d
        p2.font.size = Pt(11)
        p2.font.color.rgb = DARK_TEXT
        p2.space_before = Pt(3)

    # ==========================================
    # SLIDE 9: Desain 4 Skenario Baru (Inti Diskusi)
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Desain 4 Skenario Simulasi Baru (Inti Diskusi Hari Ini)")

    # Table of 4 scenarios
    rows, cols = 8, 5
    t_shape = s9.shapes.add_table(rows, cols, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.3))
    tbl = t_shape.table
    tbl.columns[0].width = Inches(3.733)
    tbl.columns[1].width = Inches(2.0)
    tbl.columns[2].width = Inches(2.0)
    tbl.columns[3].width = Inches(2.0)
    tbl.columns[4].width = Inches(2.0)

    s_headers = ["Parameter Pemodelan", "Simulasi 1\n(Baseline FCUC)", "Simulasi 2\n(+ BESS Standar)", "Simulasi 3\n(+ BESS VI)", "Simulasi 4\n(+ PV-WT Pengotor)"]
    for c, h in enumerate(s_headers):
        cell = tbl.cell(0, c)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = WHITE
            p.alignment = PP_ALIGN.CENTER

    scen_data = [
        ("Generator Termal (10 Unit)", "Aktif (G1-G10)", "Aktif (G1-G10)", "Aktif (G1-G10)", "Aktif (G1-G10)"),
        ("10 Batasan Dasar UC Konvensional", "Aktif", "Aktif", "Aktif", "Aktif"),
        ("Batasan RoCoF (Inersia Min.)", "Aktif (<=0.55 Hz/s)", "Aktif (<=0.55 Hz/s)", "Aktif (<=0.55 Hz/s)", "Aktif (<=0.55 Hz/s)"),
        ("Regulasi Frekuensi Primer (QSS)", "Aktif (>=49.5 Hz)", "Aktif (>=49.5 Hz)", "Aktif (>=49.5 Hz)", "Aktif (>=49.5 Hz)"),
        ("Penyedia Inersia Sistem", "100% Termal SG", "100% Termal SG", "Termal + BESS VI", "Termal + BESS VI"),
        ("Operasi BESS (B1 & B2)", "Non-Aktif", "Arbitrase Saja (P_VI=0)", "Arbitrase + VI Headroom", "Arbitrase + VI Headroom"),
        ("PLTB & PLTS (Pengotor)", "Non-Aktif", "Non-Aktif", "Non-Aktif", "Aktif (Zero Inersia)"),
    ]

    for r, row_data in enumerate(scen_data):
        for c, val in enumerate(row_data):
            cell = tbl.cell(r + 1, c)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(241, 245, 249) if r % 2 == 1 else WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(10)
                p.font.color.rgb = DARK_TEXT
                p.alignment = PP_ALIGN.CENTER

    # Note below table
    note_box = s9.shapes.add_textbox(Inches(0.8), Inches(6.25), Inches(11.733), Inches(0.8))
    ntf = note_box.text_frame
    ntf.word_wrap = True
    np = ntf.paragraphs[0]
    np.text = "💡 Dua Dimensi Frekuensi Aktif di Seluruh Skenario: RoCoF dijaga inersia (t=0+), sedangkan QSS dijaga droop governor (t=10-30s)."
    np.font.size = Pt(11)
    np.font.bold = True
    np.font.color.rgb = BLUE_ACCENT

    # ==========================================
    # SLIDE 10: Rencana Aksi ke Depan (5 Tahap)
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Rencana Kerja ke Depan (5 Tahapan Terstruktur)")

    steps = [
        ("Tahap 1: Eksekusi Pyomo & CPLEX", "Menyusun skrip run_4_simulations.py, membangun model PV dan WT curtailment limit, serta menjalankan optimasi 4 simulasi dengan solver CPLEX 22.1.1."),
        ("Tahap 2: Ekstraksi & Analisis Komparatif", "Mengekstrak tabel komparasi detail biaya (Fuel, Startup, Curtailment Cost) dan menganalisis perbandingan 'Dengan vs Tanpa PV-WT'."),
        ("Tahap 3: Visualisasi Grafik Publikasi IEEE", "Menghasilkan 4 grafik standar IEEE 300 DPI di Paper/figures/ (Stacked Dispatch, Inersia & RoCoF 24h, BESS VI Headroom, Curtailment Area)."),
        ("Tahap 4: Validasi Transien DIgSILENT", "Mengimpor jadwal dispatch ke DIgSILENT PowerFactory untuk simulasi domain-waktu N-1 contingency trip unit terbesar dan mengekstrak kurva f(t)."),
        ("Tahap 5: Manuskrip Paper Baru (main_v3.tex)", "Menyusun manuskrip lengkap baru main_v3.tex (mempertahankan v2) dengan formulasi baru, tabel hasil numerik, dan mengompilasi PDF terbaru.")
    ]

    for i, (st_title, st_desc) in enumerate(steps):
        card = add_card(s10, Inches(0.8), Inches(1.8 + i * 1.05), Inches(11.733), Inches(0.95))
        ctf = card.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.3)
        ctf.margin_top = Inches(0.12)
        
        p = ctf.paragraphs[0]
        p.text = f"📍 {st_title}"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = NAVY
        
        p2 = ctf.add_paragraph()
        p2.text = st_desc
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = DARK_TEXT
        p2.space_before = Pt(2)

    # ==========================================
    # SLIDE 11: Permohonan Arahan kepada Dosen Pembimbing
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Poin Diskusi & Permohonan Arahan kepada Dosen Pembimbing")

    questions = [
        ("1. Nilai Penalti Biaya Curtailment (C_curt)", 
         "Apakah penetapan nilai penalti pembuangan energi terbarukan sebesar $30/MWh atau $50/MWh dipandang cukup representatif dalam mencerminkan kerugian ekonomi di sistem tenaga modern?"),
        ("2. Representativitas Sistem Uji IEEE 24-Bus", 
         "Apakah penyederhanaan sistem uji IEEE 24-bus menjadi model tembaga 10 generator sinkron sudah cukup kuat untuk luaran publikasi jurnal bereputasi (IEEE / MDPI), atau diperlukan variasi beban ekstrem?"),
        ("3. Skenario Uji Transien di DIgSILENT PowerFactory", 
         "Untuk simulasi transien di DIgSILENT (Tahap 4), apakah cukup difokuskan pada kontingensi N-1 trip unit terbesar (G1 400 MW), ataukah perlu diuji pula saat jam penetrasi EBT puncak (jam 12.00-13.00)?"),
        ("4. Rekomendasi Target Publikasi Jurnal", 
         "Dengan struktur pembuktian 4 skenario baru dan validasi transien DIgSILENT, mohon arahan Bapak mengenai target jurnal internasional bereputasi yang paling tepat untuk disasar.")
    ]

    for i, (q_title, q_desc) in enumerate(questions):
        card = add_card(s11, Inches(0.8), Inches(1.8 + i * 1.3), Inches(11.733), Inches(1.15))
        ctf = card.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.3)
        ctf.margin_top = Inches(0.15)
        
        p = ctf.paragraphs[0]
        p.text = f"❓ {q_title}"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = AMBER
        
        p2 = ctf.add_paragraph()
        p2.text = q_desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = DARK_TEXT
        p2.space_before = Pt(3)

    # ==========================================
    # SLIDE 12: Penutup Slide (Dark Theme)
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    bg12 = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg12.fill.solid()
    bg12.fill.fore_color.rgb = NAVY
    bg12.line.fill.background()

    tbox12 = s12.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.333), Inches(3.0))
    tf12 = tbox12.text_frame
    tf12.word_wrap = True
    
    p = tf12.paragraphs[0]
    p.text = "TERIMA KASIH"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER
    
    p2 = tf12.add_paragraph()
    p2.text = "Mohon Masukan, Kritik, dan Arahan dari Bapak Ir. Lesnanto Multa Putranto, Ph.D."
    p2.font.size = Pt(16)
    p2.font.color.rgb = CYAN
    p2.space_before = Pt(14)
    p2.alignment = PP_ALIGN.CENTER

    p3 = tf12.add_paragraph()
    p3.text = "Departemen Teknik Elektro dan Teknologi Informasi\nFakultas Teknik — Universitas Gadjah Mada"
    p3.font.size = Pt(13)
    p3.font.color.rgb = RGBColor(203, 213, 225)
    p3.space_before = Pt(14)
    p3.alignment = PP_ALIGN.CENTER

    prs.save(output_path)
    print(f"File presentasi PPTX berhasil disimpan ke: {output_path}")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "Presentasi_Progres_Bimbingan_Pak_Lesnanto.pptx"
    create_deck(out)
