from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

md_path = Path('chart_outputs/fairfield_sample_20260203_203506/01_Forensic_Dossier.md')
text = md_path.read_text(encoding='utf-8')
styles = getSampleStyleSheet()
doc = SimpleDocTemplate('chart_outputs/fairfield_sample_20260203_203506/Fairfield_Sample_Premium.pdf', pagesize=LETTER, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=1*inch, bottomMargin=1*inch)
story = [Paragraph('Codex Caelestis Forensic Report Sample', styles['Title']), Spacer(1, 12)]
for block in text.split('\n\n'):
    clean = block.strip()
    if not clean:
        continue
    story.append(Paragraph(clean.replace('\n', '<br/>'), styles['BodyText']))
    story.append(Spacer(1, 6))
story.append(Paragraph('Price point: $50 professional holography edition', styles['Heading2']))
doc.build(story)
