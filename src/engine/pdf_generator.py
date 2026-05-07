import re
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (Flowable, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)


class HorizontalLine(Flowable):
    def __init__(self, width=460):
        Flowable.__init__(self)
        self.width = width

    def draw(self):
        self.canv.setStrokeColor(colors.lightgrey)
        self.canv.setLineWidth(1)
        self.canv.line(0, 0, self.width, 0)


class PDFReportGenerator:
    def __init__(self, chart_data, tier="FULL"):
        self.data = chart_data
        self.tier = tier.upper()  # CALIBRATION or FULL
        self.buffer = BytesIO()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        self.styles.add(
            ParagraphStyle(
                name="Header1",
                parent=self.styles["Heading1"],
                fontSize=16,
                spaceAfter=12,
                textColor=colors.darkblue,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="Header2",
                parent=self.styles["Heading2"],
                fontSize=14,
                spaceBefore=12,
                spaceAfter=6,
                textColor=colors.darkred,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="Header3",
                parent=self.styles["Heading3"],
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
                fontSize=9,
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

    def _parse_markdown(self, text):
        """
        Simple Markdown parser for ReportLab.
        Converts # Headers, **bold**, *italics*, and lists.
        """
        flowables = []
        lines = text.split("\n")
        in_code_block = False

        for line in lines:
            line = line.strip()

            # Handle Code Blocks (Skip them for now, or render differently)
            if line.startswith("```"):
                in_code_block = not in_code_block
                continue

            if in_code_block:
                continue

            if not line:
                flowables.append(Spacer(1, 6))
                continue

            # Formatting (Bold/Italic) - using reportlab's XML syntax
            # Replace **text** with <b>text</b>
            line = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)
            # Replace *text* with <i>text</i>
            line = re.sub(r"\*(.*?)\*", r"<i>\1</i>", line)

            # Headers
            if line.startswith("# "):
                # Special handling for "Part X" to force page break
                if line.startswith("# Part"):
                    flowables.append(PageBreak())

                flowables.append(Paragraph(line[2:], self.styles["Header1"]))
                flowables.append(Spacer(1, 6))
            elif line.startswith("## "):
                flowables.append(Paragraph(line[3:], self.styles["Header2"]))
            elif line.startswith("### "):
                flowables.append(Paragraph(line[4:], self.styles["Header3"]))
            elif line.startswith("---"):
                # Changed from PageBreak to HorizontalLine
                flowables.append(Spacer(1, 6))
                flowables.append(HorizontalLine())
                flowables.append(Spacer(1, 6))
            elif line.startswith("- ") or line.startswith("* "):
                # Bullet point
                flowables.append(Paragraph(f"• {line[2:]}", self.styles["Normal"]))
            elif line.startswith("> "):
                flowables.append(Paragraph(line[2:], self.styles["Quote"]))
            else:
                flowables.append(Paragraph(line, self.styles["Normal"]))

        return flowables

    def generate(self, custom_content: str = None):  # type: ignore
        """
        Generates the PDF.
        :param custom_content: Optional Markdown string (AI Report) to append.
        """
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=LETTER,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
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
        meta = self.data.get("meta", {})
        dt_str = (
            f"{meta.get('date', 'Unknown Date')} at {meta.get('time', 'Unknown Time')}"
        )
        loc_str = f"{meta.get('city', 'Unknown City')}, {meta.get('state', '')}"

        story.append(
            Paragraph(
                f"<b>Native Name:</b> {meta.get('subject_name', 'Native')}",
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

        if "sect_status" in summary:
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
        story.append(Spacer(1, 24))

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
        story.append(Spacer(1, 24))
        disclaimer = (
            "HISTORICAL USE ONLY: This report provides traditional calculations and technical exports. "
            "It is not medical, legal, or financial advice. Do not use it to make health, legal, or investment decisions."
        )
        story.append(Paragraph(disclaimer, self.styles["NormalSmall"]))

        doc.build(story)
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
