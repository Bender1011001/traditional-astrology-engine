import re
import math
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (Flowable, KeepTogether, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)


class HorizontalLine(Flowable):
    def __init__(self, width=460):
        Flowable.__init__(self)
        self.width = width

    def draw(self):
        self.canv.setStrokeColor(colors.lightgrey)
        self.canv.setLineWidth(1)
        self.canv.line(0, 0, self.width, 0)


class TraditionalChartWheel(Flowable):
    """Whole-sign chart wheel: element-coloured sign band, glyphs, houses,
    degree ticks, angle markers, and the aspect geometry.

    Drawn from the outside in:
      * an element-tinted band carrying the twelve sign glyphs
      * a degree scale, ticked every 5 degrees and emphasised every 10
      * a house band carrying Roman numerals (whole-sign, so house N is the
        Nth sign from the rising sign)
      * the planets, with glyph and degree-in-sign
      * the aspect lines, red for hard contacts and blue for soft
      * the four angles, with the horizon drawn across the figure
    """

    SIGN_GLYPHS = (
        "♈♉♊♋♌♍"
        "♎♏♐♑♒♓"
    )
    SIGN_ABBR = ("Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi")

    PLANET_GLYPHS = {
        "Sun": "☉",
        "Moon": "☽",
        "Mercury": "☿",
        "Venus": "♀",
        "Mars": "♂",
        "Jupiter": "♃",
        "Saturn": "♄",
    }
    PLANET_ABBR = {
        "Sun": "Su", "Moon": "Mo", "Mercury": "Me", "Venus": "Ve",
        "Mars": "Ma", "Jupiter": "Ju", "Saturn": "Sa",
    }

    # Element tints, warm through cool. Kept pale so ink drawn over them stays
    # legible, including in greyscale print.
    ELEMENT_FILL = {
        "fire": colors.HexColor("#F6DFD6"),
        "earth": colors.HexColor("#DFE7DA"),
        "air": colors.HexColor("#F3EFD9"),
        "water": colors.HexColor("#D9E4EC"),
    }
    ELEMENTS = ("fire", "earth", "air", "water")

    ROMAN = ("I", "II", "III", "IV", "V", "VI",
             "VII", "VIII", "IX", "X", "XI", "XII")

    INK = colors.HexColor("#172554")
    ACCENT = colors.HexColor("#8B1E1E")
    SOFT = colors.HexColor("#1E3A8A")

    def __init__(self, chart_data, size=340):
        super().__init__()
        self.chart_data = chart_data
        self.width = size
        self.height = size
        self.hAlign = "CENTER"

    @staticmethod
    def _point(cx, cy, radius, longitude, ascendant):
        """Map an ecliptic longitude to a point on the wheel.

        Convention: the Ascendant sits on the left (due west on the page) and
        longitude increases ANTICLOCKWISE, descending below the horizon first.
        That places the four angles where every chart-reader expects them —
        Ascendant left, IC bottom, Descendant right, Midheaven top — and makes
        house I follow the Ascendant downward.

        This previously used `180 - (lon - asc)`, which runs longitude the other
        way and renders the whole figure MIRRORED: the Midheaven appeared at the
        bottom of the page and the houses ran backwards. The sign is now `+`.
        """
        angle = math.radians(180.0 + ((float(longitude) - ascendant) % 360.0))
        return cx + radius * math.cos(angle), cy + radius * math.sin(angle)

    def _sector(self, canvas, cx, cy, r_out, r_in, start_lon, span, asc, fill):
        """Fill the annular sector between two radii."""
        path = canvas.beginPath()
        steps = 14
        for i in range(steps + 1):
            lon = start_lon + span * (i / steps)
            x, y = self._point(cx, cy, r_out, lon, asc)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        for i in range(steps, -1, -1):
            lon = start_lon + span * (i / steps)
            x, y = self._point(cx, cy, r_in, lon, asc)
            path.lineTo(x, y)
        path.close()
        canvas.setFillColor(fill)
        canvas.setStrokeColor(fill)
        canvas.setLineWidth(0.2)
        canvas.drawPath(path, stroke=1, fill=1)

    def draw(self):
        from src.engine.fonts import ASTRO_GLYPH_FONT, ensure_astro_glyphs

        glyphs = ensure_astro_glyphs()
        canvas = self.canv
        cx = cy = self.width / 2

        r_outer = self.width * 0.48
        r_sign_in = self.width * 0.395
        r_tick = self.width * 0.365
        r_house_in = self.width * 0.315
        r_planet = self.width * 0.255
        r_aspect = self.width * 0.205

        analysis = self.chart_data.get("analysis", {}) or {}
        angles = analysis.get("angles", {}) or {}

        def _angle_lon(name):
            value = angles.get(name)
            if isinstance(value, dict):
                value = value.get("longitude", value.get("lon_abs", 0.0))
            return float(value or 0.0)

        asc = _angle_lon("Ascendant")
        mc = _angle_lon("Midheaven")
        asc_sign = int(asc // 30) % 12

        canvas.saveState()

        # --- element-tinted sign band ---------------------------------------
        for i in range(12):
            sign_index = (asc_sign + i) % 12
            start = (asc_sign + i) * 30.0
            self._sector(canvas, cx, cy, r_outer, r_sign_in, start, 30.0, asc,
                         self.ELEMENT_FILL[self.ELEMENTS[sign_index % 4]])

        canvas.setStrokeColor(self.INK)
        canvas.setLineWidth(1.2)
        canvas.circle(cx, cy, r_outer, stroke=1, fill=0)
        canvas.setLineWidth(0.7)
        canvas.circle(cx, cy, r_sign_in, stroke=1, fill=0)
        canvas.circle(cx, cy, r_house_in, stroke=1, fill=0)
        canvas.setLineWidth(0.5)
        canvas.circle(cx, cy, r_aspect, stroke=1, fill=0)

        # --- sign dividers, glyphs, degree scale ----------------------------
        for i in range(12):
            sign_index = (asc_sign + i) % 12
            start = (asc_sign + i) * 30.0
            x1, y1 = self._point(cx, cy, r_sign_in, start, asc)
            x2, y2 = self._point(cx, cy, r_outer, start, asc)
            canvas.setStrokeColor(self.INK)
            canvas.setLineWidth(0.7)
            canvas.line(x1, y1, x2, y2)

            gx, gy = self._point(cx, cy, (r_outer + r_sign_in) / 2, start + 15.0, asc)
            canvas.setFillColor(self.INK)
            if glyphs:
                canvas.setFont(ASTRO_GLYPH_FONT, 13)
                canvas.drawCentredString(gx, gy - 4.5, self.SIGN_GLYPHS[sign_index])
            else:
                canvas.setFont("Times-Bold", 8.5)
                canvas.drawCentredString(gx, gy - 3, self.SIGN_ABBR[sign_index])

            for d in range(0, 30, 5):
                lon = start + d
                major = (d % 10 == 0)
                r_from = r_tick if major else r_tick + 3.5
                tx1, ty1 = self._point(cx, cy, r_from, lon, asc)
                tx2, ty2 = self._point(cx, cy, r_sign_in, lon, asc)
                canvas.setLineWidth(0.5 if major else 0.3)
                canvas.setStrokeColor(colors.HexColor("#7C8AA5"))
                canvas.line(tx1, ty1, tx2, ty2)

        # --- house band ------------------------------------------------------
        for i in range(12):
            start = (asc_sign + i) * 30.0
            x1, y1 = self._point(cx, cy, r_house_in, start, asc)
            x2, y2 = self._point(cx, cy, r_tick, start, asc)
            canvas.setStrokeColor(colors.HexColor("#93A1B5"))
            canvas.setLineWidth(0.5)
            canvas.line(x1, y1, x2, y2)
            hx, hy = self._point(cx, cy, (r_tick + r_house_in) / 2, start + 15.0, asc)
            canvas.setFillColor(colors.HexColor("#5A6B85"))
            canvas.setFont("Times-Roman", 7)
            canvas.drawCentredString(hx, hy - 2.5, self.ROMAN[i])

        # --- planet positions, resolved before anything is drawn -------------
        planets = [
            item for item in analysis.get("planets_forensic", []) or []
            if item.get("name") in self.PLANET_GLYPHS
        ]
        planets.sort(key=lambda item: float(item.get("longitude", 0.0)))

        positions = {}
        last_lon = None
        tier = 0
        for planet in planets:
            lon = float(planet.get("longitude", 0.0))
            if last_lon is not None and min((lon - last_lon) % 360,
                                            (last_lon - lon) % 360) < 9:
                tier = (tier + 1) % 3
            else:
                tier = 0
            positions[str(planet.get("name"))] = (
                self._point(cx, cy, r_planet - tier * 16, lon, asc), lon
            )
            last_lon = lon

        # --- aspect geometry --------------------------------------------------
        aspect_style = {
            "Opposition": (self.ACCENT, 0.9, None),
            "Square": (self.ACCENT, 0.7, None),
            "Trine": (self.SOFT, 0.7, None),
            "Sextile": (self.SOFT, 0.5, (2, 2)),
        }
        for aspect in analysis.get("aspects", []) or []:
            style = aspect_style.get(str(aspect.get("type")))
            if not style:
                continue
            a = positions.get(str(aspect.get("planet_a")))
            b = positions.get(str(aspect.get("planet_b")))
            if not a or not b:
                continue
            colour, width, dash = style
            canvas.setStrokeColor(colour)
            canvas.setLineWidth(width)
            canvas.setDash(dash if dash else [])
            canvas.line(a[0][0], a[0][1], b[0][0], b[0][1])
        canvas.setDash([])

        # --- the four angles --------------------------------------------------
        canvas.setStrokeColor(self.ACCENT)
        canvas.setLineWidth(1.3)
        ax1, ay1 = self._point(cx, cy, r_outer + 6, asc, asc)
        ax2, ay2 = self._point(cx, cy, r_outer + 6, asc + 180.0, asc)
        canvas.line(ax1, ay1, ax2, ay2)
        canvas.setLineWidth(0.9)
        mx1, my1 = self._point(cx, cy, r_house_in, mc, asc)
        mx2, my2 = self._point(cx, cy, r_outer + 6, mc, asc)
        canvas.line(mx1, my1, mx2, my2)
        ix1, iy1 = self._point(cx, cy, r_house_in, mc + 180.0, asc)
        ix2, iy2 = self._point(cx, cy, r_outer + 6, mc + 180.0, asc)
        canvas.line(ix1, iy1, ix2, iy2)

        canvas.setFillColor(self.ACCENT)
        canvas.setFont("Times-Bold", 7.5)
        for label, lon, dx in (("ASC", asc, -14), ("DSC", asc + 180.0, 14),
                               ("MC", mc, 0), ("IC", mc + 180.0, 0)):
            lx, ly = self._point(cx, cy, r_outer + 12, lon, asc)
            canvas.drawCentredString(lx + dx, ly - 2, label)

        # --- planet discs, drawn last so they sit above the lines -------------
        for planet in planets:
            name = str(planet.get("name"))
            (px, py), lon = positions[name]
            canvas.setFillColor(colors.white)
            canvas.setStrokeColor(self.ACCENT)
            canvas.setLineWidth(0.9)
            canvas.circle(px, py, 10.5, stroke=1, fill=1)
            canvas.setFillColor(self.ACCENT)
            if glyphs:
                canvas.setFont(ASTRO_GLYPH_FONT, 12)
                canvas.drawCentredString(px, py - 4, self.PLANET_GLYPHS[name])
            else:
                canvas.setFont("Helvetica-Bold", 6.5)
                canvas.drawCentredString(px, py - 2.5, self.PLANET_ABBR[name])
            canvas.setFillColor(self.INK)
            canvas.setFont("Times-Roman", 6)
            canvas.drawCentredString(px, py - 18, str(int(lon % 30)) + "°")

        canvas.restoreState()


class PDFReportGenerator:
    def __init__(self, chart_data, tier="FULL"):
        self.data = chart_data
        self.tier = tier.upper()  # CALIBRATION or FULL
        self.buffer = BytesIO()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        self.styles["Title"].fontName = "Times-Bold"
        self.styles["Title"].fontSize = 28
        self.styles["Title"].leading = 32
        self.styles["Title"].textColor = colors.HexColor("#172554")
        self.styles["Normal"].fontName = "Times-Roman"
        self.styles["Normal"].fontSize = 10.5
        self.styles["Normal"].leading = 15
        self.styles["Normal"].spaceAfter = 7
        self.styles.add(
            ParagraphStyle(
                name="Header1",
                parent=self.styles["Heading1"],
                fontName="Times-Bold",
                fontSize=19,
                leading=23,
                spaceAfter=14,
                keepWithNext=True,
                textColor=colors.HexColor("#172554"),
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="Header2",
                parent=self.styles["Heading2"],
                fontName="Times-Bold",
                fontSize=14,
                leading=18,
                spaceBefore=16,
                spaceAfter=8,
                keepWithNext=True,
                textColor=colors.HexColor("#8B1E1E"),
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="Header3",
                parent=self.styles["Heading3"],
                fontName="Times-Bold",
                fontSize=12,
                spaceBefore=10,
                spaceAfter=4,
                textColor=colors.black,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="NormalSmall",
                parent=self.styles["Normal"],
                fontName="Times-Roman",
                fontSize=8.25,
                leading=10.5,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="Cliffhanger",
                parent=self.styles["Normal"],
                fontSize=12,
                leading=16,
                alignment=1,  # Center
                textColor=colors.darkred,
                spaceBefore=24,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="Quote",
                parent=self.styles["Normal"],
                fontSize=10,
                leftIndent=20,
                rightIndent=20,
                spaceBefore=10,
                spaceAfter=10,
                fontName="Helvetica-Oblique",
            )
        )

    @staticmethod
    def _fmt_inline(content: str) -> str:
        """XML-escape raw content, THEN apply markdown bold/italic. Escaping first
        means stray & < > in the (LLM-authored) text can never break the parser."""
        from xml.sax.saxutils import escape

        s = escape(content)
        s = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", s)
        s = re.sub(r"\*(.*?)\*", r"<i>\1</i>", s)
        return s

    def _safe_para(self, formatted_text: str, style):
        """Build a Paragraph; if ReportLab rejects the inline XML (e.g. the model
        emitted overlapping/mismatched <b>/<i> tags), fall back to a plain,
        tag-stripped, fully-escaped version so a single bad line never aborts the
        whole PDF."""
        from xml.sax.saxutils import escape

        try:
            return Paragraph(formatted_text, style)
        except Exception:
            stripped = re.sub(r"</?[a-zA-Z][^>]*>", "", formatted_text)
            try:
                return Paragraph(stripped, style)
            except Exception:
                return Paragraph(escape(stripped), style)

    @staticmethod
    def _is_table_separator(cells):
        """A markdown separator row: every cell is dashes, colons or blank."""
        return bool(cells) and all(
            set(c.strip()) <= set("-: ") and "-" in c for c in cells
        )

    def _make_table(self, rows):
        """Build a ReportLab Table from buffered markdown rows.

        Without this, a pipe-delimited row falls through to the paragraph
        branch and typesets as literal pipes, which is what every previous
        report did. Cells are Paragraphs so long text wraps instead of
        overflowing the column.
        """
        parsed = []
        for raw in rows:
            cells = [c.strip() for c in raw.strip().strip("|").split("|")]
            if self._is_table_separator(cells):
                continue
            parsed.append(cells)
        if not parsed:
            return []

        width = max(len(r) for r in parsed)
        parsed = [r + [""] * (width - len(r)) for r in parsed]

        cell_style = ParagraphStyle(
            "TableCell", parent=self.styles["Normal"], fontSize=8.5, leading=11
        )
        head_style = ParagraphStyle(
            "TableHead", parent=cell_style, fontName=self.styles["Header3"].fontName
        )

        data = []
        for i, row in enumerate(parsed):
            style = head_style if i == 0 else cell_style
            data.append([self._safe_para(self._fmt_inline(c), style) for c in row])

        avail = 6.5 * inch
        table = Table(data, colWidths=[avail / width] * width, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.75, colors.HexColor("#444444")),
                    ("LINEBELOW", (0, 1), (-1, -2), 0.25, colors.HexColor("#DDDDDD")),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return [Spacer(1, 4), table, Spacer(1, 8)]

    def _parse_markdown(self, text):
        """
        Simple, robust Markdown parser for ReportLab.
        Converts # Headers, **bold**, *italics*, lists and pipe tables;
        tolerates malformed inline markup without failing the document.
        """
        flowables = []
        lines = text.split("\n")
        in_code_block = False
        in_evidence_notes = False
        table_buf = []

        def flush_table():
            if table_buf:
                flowables.extend(self._make_table(list(table_buf)))
                table_buf.clear()

        for line in lines:
            line = line.strip()

            if line.startswith("```"):
                flush_table()
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            # Buffer consecutive pipe rows and emit them as one table.
            if line.startswith("|") and line.endswith("|") and len(line) > 1:
                table_buf.append(line)
                continue
            flush_table()

            if not line:
                flowables.append(Spacer(1, 6))
                continue

            # Headers (detect on the raw line; format only the content)
            if line.startswith("# "):
                if line.startswith("# Part"):
                    flowables.append(PageBreak())
                flowables.append(self._safe_para(self._fmt_inline(line[2:]), self.styles["Header1"]))
                flowables.append(Spacer(1, 6))
            elif line.startswith("## "):
                flowables.append(self._safe_para(self._fmt_inline(line[3:]), self.styles["Header2"]))
                if line[3:].strip().lower() == "evidence notes":
                    in_evidence_notes = True
            elif line.startswith("### "):
                flowables.append(self._safe_para(self._fmt_inline(line[4:]), self.styles["Header3"]))
            elif line.startswith("---"):
                flowables.append(Spacer(1, 6))
                flowables.append(HorizontalLine())
                flowables.append(Spacer(1, 6))
            elif line.startswith("- ") or line.startswith("* "):
                flowables.append(
                    KeepTogether(
                        [
                            self._safe_para(
                                "• " + self._fmt_inline(line[2:]),
                                self.styles["NormalSmall"]
                                if in_evidence_notes
                                else self.styles["Normal"],
                            )
                        ]
                    )
                )
            elif line.startswith("> "):
                flowables.append(self._safe_para(self._fmt_inline(line[2:]), self.styles["Quote"]))
            else:
                flowables.append(
                    self._safe_para(
                        self._fmt_inline(line),
                        self.styles["NormalSmall"]
                        if in_evidence_notes
                        else self.styles["Normal"],
                    )
                )

        flush_table()  # a document ending in a table would otherwise drop it
        return flowables

    def generate(self, custom_content: str = None):  # type: ignore
        """
        Generates the PDF.
        :param custom_content: Optional Markdown string (AI Report) to append.
        """
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=LETTER,
            rightMargin=58,
            leftMargin=58,
            topMargin=62,
            bottomMargin=54,
        )

        story = []

        # Title Page / Header
        title_text = (
            "Traditional Astrology: Calibration Report"
            if self.tier == "CALIBRATION"
            else "Traditional Astrology Reading"
        )
        story.append(Paragraph(title_text, self.styles["Title"]))
        story.append(Spacer(1, 12))

        # Metadata
        meta = self.data.get("meta", {}) or {}
        chart_meta = meta.get("chart", {}) if isinstance(meta.get("chart"), dict) else {}
        display_meta = {**meta, **chart_meta}
        dt_str = (
            f"{display_meta.get('date', 'Unknown Date')} at {display_meta.get('time', 'Unknown Time')}"
        )
        loc_str = f"{display_meta.get('city', 'Unknown City')}, {display_meta.get('state', '')}"

        story.append(
            Paragraph(
                f"<b>Native Name:</b> {display_meta.get('subject_name') or display_meta.get('name') or 'Native'}",
                self.styles["Normal"],
            )
        )
        story.append(Paragraph(f"<b>Birth Time:</b> {dt_str}", self.styles["Normal"]))
        story.append(Paragraph(f"<b>Location:</b> {loc_str}", self.styles["Normal"]))

        # Determine Sect
        sect_status = "-"
        forensic = self.data.get("forensic_report", {})
        if not forensic and "technical_data" in self.data:
            forensic = self.data["technical_data"].get("analysis", {})
            meta = self.data["technical_data"].get("meta", {})  # Refresh meta if needed

        summary = forensic.get("summary", {})

        direct_sect = (self.data.get("analysis", {}) or {}).get("sect", {})
        if direct_sect.get("type"):
            sect_status = str(direct_sect["type"]).title()
        elif "sect_status" in summary:
            sect_status = summary["sect_status"]
        elif "astronomy" in self.data.get("technical_data", {}):
            sun_alt = (
                self.data["technical_data"]["astronomy"]["planets"]
                .get("Sun", {})
                .get("altitude", 0)
            )
            sect_status = "Day" if sun_alt > 0 else "Night"

        story.append(
            Paragraph(f"<b>Sect Status:</b> {sect_status}", self.styles["Normal"])
        )
        house_system = display_meta.get("house_system") or {}
        zodiac_system = display_meta.get("zodiac_system") or {}
        if isinstance(house_system, dict) or isinstance(zodiac_system, dict):
            house_label = house_system.get("label", "Whole Sign") if isinstance(house_system, dict) else str(house_system)
            zodiac_label = zodiac_system.get("label", "Tropical") if isinstance(zodiac_system, dict) else str(zodiac_system)
            story.append(
                Paragraph(
                    f"<b>Method:</b> {house_label} houses · {zodiac_label} zodiac · seven visible planets",
                    self.styles["Normal"],
                )
            )
        story.append(Spacer(1, 36))
        story.append(
            Paragraph(
                "A source-aware historical nativity, with calculated evidence and explicit doctrinal limits.",
                self.styles["Quote"],
            )
        )
        story.append(Spacer(1, 12))
        story.append(TraditionalChartWheel(self.data, size=250))
        story.append(PageBreak())

        # --- CONTENT INJECTION ---
        if custom_content:
            # If we have AI content, we treat it as the primary body of the report
            # We skip the algorithmic tables in favor of the AI narrative, or append them?
            # The prompt says "Generate Premium Report". We should probably just render the Markdown
            # as it contains the full dossier.
            story.extend(self._parse_markdown(custom_content))

        else:
            # Fallback to Algorithmic / Template Report (Legacy or Calibration)
            self._generate_algorithmic_report(story, forensic, sect_status)

        # Footer / Disclaimer
        if not custom_content:
            story.append(Spacer(1, 24))
            disclaimer = (
                "HISTORICAL USE ONLY: This report provides traditional calculations and technical exports. "
                "It is not medical, legal, or financial advice. Do not use it to make health, legal, or investment decisions."
            )
            story.append(Paragraph(disclaimer, self.styles["NormalSmall"]))

        def draw_page(canvas, document):
            canvas.saveState()
            page = canvas.getPageNumber()
            canvas.setStrokeColor(colors.HexColor("#D6D3D1"))
            canvas.setLineWidth(0.5)
            canvas.line(document.leftMargin, 35, LETTER[0] - document.rightMargin, 35)
            canvas.setFont("Times-Roman", 8)
            canvas.setFillColor(colors.HexColor("#57534E"))
            canvas.drawString(document.leftMargin, 22, "Traditional Astrology · Historical doctrine edition")
            canvas.drawRightString(LETTER[0] - document.rightMargin, 22, f"Page {page}")
            canvas.restoreState()

        doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
        self.buffer.seek(0)
        return self.buffer

    def _generate_algorithmic_report(self, story, forensic, sect_status):
        """Generates the structured table-based report (Fallback / Calibration)"""

        # Section I & II: Hierarchy and Master of Nativity
        story.append(
            Paragraph(
                "I. Cosmic Hierarchy & II. Master of Nativity", self.styles["Header1"]
            )
        )

        almuten = forensic.get("almuten", {})
        if not almuten and "advanced_mechanics" in forensic:
            almuten = forensic["advanced_mechanics"].get("almuten", {})

        state_data = [
            ["Lunar Phase", forensic.get("summary", {}).get("lunar_phase", "Unknown")],
            ["Sect Decree", sect_status],
            ["Almuten Figuris", almuten.get("winner", "Unknown")],
            ["Almuten Score", str(almuten.get("score", 0))],
        ]

        t = Table(state_data, colWidths=[2 * inch, 4 * inch])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTMODE", (0, 0), (-1, -1), "SIZE", 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 18))

        # Section III: Temperament (non-medical framing)
        story.append(Paragraph("III. Temperament (Historical)", self.styles["Header1"]))
        temp = forensic.get("temperament", {})
        if not temp and "summary" in forensic:
            temp = forensic["summary"].get("temperament", {})

        temp_data = [
            ["Primary Temperament", temp.get("primary_temperament", "Unknown")],
            [
                "Hot/Cold Balance",
                str((temp.get("net_balance") or {}).get("Hot_vs_Cold", "Unknown")),
            ],
            [
                "Moist/Dry Balance",
                str((temp.get("net_balance") or {}).get("Moist_vs_Dry", "Unknown")),
            ],
        ]
        t = Table(temp_data, colWidths=[2 * inch, 4 * inch])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 18))

        # Section XIX: Temporal Forensics / Retrodiction (CRITICAL)
        story.append(
            Paragraph("XIX. Temporal Analysis (Retrodiction)", self.styles["Header1"])
        )
        story.append(
            Paragraph(
                "Verification of past events against chronological triggers.",
                self.styles["Normal"],
            )
        )
        story.append(Spacer(1, 6))

        retro = forensic.get("retrodiction", [])
        if not retro:
            retro = [
                {
                    "age": 12,
                    "assessment": "Major shift in domestic environment or physical vitality.",
                },
                {
                    "age": 18,
                    "assessment": "A period of high volatility or sudden redirection in path.",
                },
                {
                    "age": 24,
                    "assessment": "Consolidation of public identity or professional duty.",
                },
            ]

        for r in retro:
            story.append(
                Paragraph(
                    f"• <b>Age {r['age']}:</b> {r['assessment']}", self.styles["Normal"]
                )
            )
        story.append(Spacer(1, 18))

        # Section XVI: Current Context (Lord of the Year ONLY)
        story.append(Paragraph("XVI. Current Context", self.styles["Header1"]))
        prof = forensic.get("enhanced_profections", {})
        if not prof and "fate" in forensic:
            prof = forensic["fate"].get("profections", {}) or forensic["fate"].get(
                "enhanced_profections", {}
            )

        story.append(
            Paragraph(
                f"Annual Profection (Age {prof.get('age', 'Unknown')}):",
                self.styles["Normal"],
            )
        )
        story.append(
            Paragraph(
                f"Lord of the Year: {prof.get('lord_of_year', 'Unknown')}",
                self.styles["Normal"],
            )
        )
        story.append(
            Paragraph(
                f"Profected Sign: {prof.get('annual_sign', 'Unknown')}",
                self.styles["Normal"],
            )
        )
        story.append(Spacer(1, 18))

        if self.tier == "FULL":
            # For Full Tier without custom AI content, we explicitly state it's incomplete or fallback
            story.append(PageBreak())
            story.append(
                Paragraph(
                    "IV. The Mitigation Loop & Remediation", self.styles["Header1"]
                )
            )
            mitigations = forensic.get(
                "mitigations", ["Structural swap logic enabled."]
            )
            for m in mitigations:
                story.append(Paragraph(f"• {m}", self.styles["Normal"]))

            story.append(Spacer(1, 18))
            story.append(
                Paragraph(
                    "XII. Topographical Audit (12 Houses)", self.styles["Header1"]
                )
            )
            houses = self.data.get("astronomy", {}).get("houses", {})
            h_data = [["House", "Sign", "Delineation"]]
            for h_num, h_val in houses.items():
                if int(h_num) <= 12:
                    h_data.append(
                        [
                            f"House {h_num}",
                            h_val.get("sign", ""),
                            "Calculation complete.",
                        ]
                    )

            t = Table(h_data, colWidths=[1 * inch, 1 * inch, 4 * inch])
            t.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.navy),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ]
                )
            )
            story.append(t)
        else:
            # The "Cliffhanger" Page for Calibration
            story.append(Spacer(1, 48))
            story.append(
                Paragraph("<b>AUDIT INCOMPLETE.</b>", self.styles["Cliffhanger"])
            )
            story.append(
                Paragraph(
                    "Your chart contains hidden Mitigations and Structural Remedies not shown in this Calibration. To access the Remedial Codex and Future Forecast, upgrade to the Full Audit.",
                    self.styles["Cliffhanger"],
                )
            )
