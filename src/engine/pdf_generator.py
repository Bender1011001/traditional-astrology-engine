from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime

class PDFReportGenerator:
    def __init__(self, chart_data):
        self.data = chart_data
        self.buffer = BytesIO()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='Header1',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        ))
        self.styles.add(ParagraphStyle(
            name='Header2',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.darkred
        ))
        self.styles.add(ParagraphStyle(
            name='NormalSmall',
            parent=self.styles['Normal'],
            fontSize=9,
        ))

    def generate(self):
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=LETTER,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        story = []

        # Title Page / Header
        story.append(Paragraph("Codex Caelestis: Forensic Astrology Report", self.styles['Title']))
        story.append(Spacer(1, 12))

        # Metadata
        meta = self.data.get("meta", {})
        dt_str = f"{meta.get('date', 'Unknown Date')} at {meta.get('time', 'Unknown Time')}"
        loc_str = f"{meta.get('city', 'Unknown City')}, {meta.get('state', '')}"
        
        story.append(Paragraph(f"<b>Date:</b> {dt_str}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Location:</b> {loc_str}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Julian Day:</b> {meta.get('julian_day', 0):.4f}", self.styles['Normal']))
        story.append(Paragraph(f"<b>House System:</b> {meta.get('house_system', {}).get('label', 'Placidus')}", self.styles['Normal']))
        story.append(Spacer(1, 24))

        # Solar/Lunar Summary
        forensic = self.data.get("forensic_report", {})
        summary = forensic.get("summary", {})
        
        story.append(Paragraph("Cosmic State", self.styles['Header1']))
        
        state_data = [
            ["Lunar Phase", summary.get("lunar_phase", "Unknown")],
            ["Temperament", summary.get("temperament", {}).get("primary_temperament", "Unknown")],
            ["Soul Guardian", forensic.get("soul_guardian", {}).get("almuten", "Unknown")],
            ["Jones Pattern", summary.get("jones_pattern", "Unknown")]
        ]
        
        t = Table(state_data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTMODE', (0,0), (-1,-1), 'SIZE', 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ]))
        story.append(t)
        story.append(Spacer(1, 18))

        # Planetary Table
        story.append(Paragraph("Planetary Positions & Dignity", self.styles['Header1']))
        
        # Header Row
        p_data = [['Planet', 'Sign', 'Longitude', 'House', 'Power', 'Sect']]
        
        f_planets = forensic.get("planets", [])
        # If forensic_report isn't populated fully, we might fallback to self.data['planets'] but forensic is better formatted
        
        for p in f_planets:
            name = p.get('planet')
            sign = p.get('sign')
            lon = f"{p.get('longitude'):.2f}"
            house = str(p.get('house_number'))
            power = p.get('power_label', 'Neutral')
            sect = p.get('sect_status', '-')
            
            p_data.append([name, sign, lon, house, power, sect])

        t = Table(p_data, colWidths=[1*inch, 1*inch, 1*inch, 0.8*inch, 1.2*inch, 1*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.navy),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke])
        ]))
        story.append(t)
        story.append(Spacer(1, 18))

        # Detailed Analysis
        story.append(Paragraph("Forensic Analysis", self.styles['Header1']))
        
        for p in f_planets:
            planet_name = p.get('planet')
            story.append(Paragraph(f"{planet_name}: {p.get('power_label')}", self.styles['Header2']))
            
            # Delineation
            delineation = p.get('delineation_text', '')
            if delineation:
                story.append(Paragraph(f"<b>Delineation:</b> {delineation}", self.styles['Normal']))
            
            # Impacts
            impacts = p.get('impacts', [])
            if impacts:
                story.append(Spacer(1, 4))
                story.append(Paragraph("<b>Judgments:</b>", self.styles['NormalSmall']))
                for imp in impacts:
                    cause = imp.get('cause')
                    effect = imp.get('effect')
                    story.append(Paragraph(f"• IF {cause} THEN {effect}", self.styles['NormalSmall']))
            
            story.append(Spacer(1, 8))

        # Plain Reading
        plain = self.data.get("plain_reading")
        if plain:
            story.append(PageBreak())
            story.append(Paragraph("Plain Language Synthesis", self.styles['Header1']))
            # Plain reading usually has newlines, handle them
            paragraphs = plain.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip().replace('\n', ' '), self.styles['Normal']))
                    story.append(Spacer(1, 6))

        # Footer / Disclaimer
        story.append(Spacer(1, 24))
        disclaimer = ("MEDICAL DISCLAIMER: This report is for historical and educational research purposes only. "
                      "It is NOT medical advice. Do not use for health decisions.")
        story.append(Paragraph(disclaimer, self.styles['NormalSmall']))

        doc.build(story)
        self.buffer.seek(0)
        return self.buffer
