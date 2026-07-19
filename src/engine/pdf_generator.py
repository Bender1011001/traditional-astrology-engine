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
    """Compact seven-planet whole-sign wheel for the report cover."""

    SIGNS = ("Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi")
    PLANET_LABELS = {
        "Sun": "Su",
        "Moon": "Mo",
        "Mercury": "Me",
        "Venus": "Ve",
        "Mars": "Ma",
        "Jupiter": "Ju",
        "Saturn": "Sa",
    }

    def __init__(self, chart_data, size=250):
        super().__init__()
        self.chart_data = chart_data
        self.width = size
        self.height = size
        self.hAlign = "CENTER"

    @staticmethod
    def _point(cx, cy, radius, longitude, ascendant):
        angle = math.radians(180.0 - ((float(longitude) - ascendant) % 360.0))
        return cx + radius * math.cos(angle), cy + radius * math.sin(angle)

    def draw(self):
        canvas = self.canv
        cx = self.width / 2
        cy = self.height / 2
        outer = self.width * 0.46
        inner = self.width * 0.34
        analysis = self.chart_data.get("analysis", {}) or {}
        angles = analysis.get("angles", {}) or {}
        asc = (angles.get("Ascendant", {}) or {}).get("longitude", 0.0)
        if isinstance(asc, dict):
            asc = asc.get("lon_abs", 0.0)
        asc = float(asc or 0.0)

        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#172554"))
        canvas.setFillColor(colors.HexColor("#172554"))
        canvas.setLineWidth(1.1)
        canvas.circle(cx, cy, outer, stroke=1, fill=0)
        canvas.setLineWidth(0.6)
        canvas.circle(cx, cy, inner, stroke=1, fill=0)

        asc_sign = int(asc // 30) % 12
        for offset in range(12):
            longitude = (asc_sign + offset) * 30.0
            x1, y1 = self._point(cx, cy, inner, longitude, asc)
            x2, y2 = self._point(cx, cy, outer, longitude, asc)
            canvas.line(x1, y1, x2, y2)
            middle = longitude + 15.0
            tx, ty = self._point(cx, cy, outer - 13, middle, asc)
            canvas.setFont("Times-Bold", 7.5)
            canvas.drawCentredString(tx, ty - 2.5, self.SIGNS[(asc_sign + offset) % 12])

        planets = [
            item
            for item in analysis.get("planets_forensic", []) or []
            if item.get("name") in self.PLANET_LABELS
        ]
        planets.sort(key=lambda item: float(item.get("longitude", 0.0)))
        last_lon = None
        cluster_level = 0
        for planet in planets:
            lon = float(planet.get("longitude", 0.0))
            if last_lon is not None and min((lon - last_lon) % 360, (last_lon - lon) % 360) < 8:
                cluster_level = (cluster_level + 1) % 3
            else:
                cluster_level = 0
            radius = inner - 20 - cluster_level * 13
            px, py = self._point(cx, cy, radius, lon, asc)
            canvas.setFillColor(colors.HexColor("#8B1E1E"))
            canvas.circle(px, py, 7.5, stroke=0, fill=1)
            canvas.setFillColor(colors.white)
            canvas.setFont("Helvetica-Bold", 5.8)
            canvas.drawCentredString(px, py - 2, self.PLANET_LABELS[planet["name"]])
            last_lon = lon

        canvas.setStrokeColor(colors.HexColor("#8B1E1E"))
        canvas.setLineWidth(1.2)
        left_x, left_y = self._point(cx, cy, outer + 5, asc, asc)
        right_x, right_y = self._point(cx, cy, outer + 5, asc + 180, asc)
        canvas.line(left_x, left_y, right_x, right_y)
        canvas.setFillColor(colors.HexColor("#8B1E1E"))
        canvas.setFont("Times-Bold", 7)
        canvas.drawString(4, cy + 4, "ASC")
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

    def _parse_markdown(self, text):
        """
        Simple, robust Markdown parser for ReportLab.
        Converts # Headers, **bold**, *italics*, and lists; tolerates malformed
        inline markup without failing the document.
        """
        flowables = []
        lines = text.split("\n")
        in_code_block = False
        in_evidence_notes = False

        for line in lines:
            line = line.strip()

            if line.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
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
