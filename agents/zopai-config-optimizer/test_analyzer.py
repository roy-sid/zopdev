import yaml
from analyzer import analyze_values, compute_score, llm_suggestions
import os

# Load sample values.yaml
with open("values.yaml", "r") as f:
    values = yaml.safe_load(f)

# Run analysis
optimized, report = analyze_values(values)

# Compute score
health_score = compute_score(report)

# AI suggestions (optional, only if GOOGLE_API_KEY is set)
with open("values.yaml", "r") as f:
    raw_yaml = f.read()
ai_suggestions = llm_suggestions(raw_yaml)

# Print results to console
print("\n--- REPORT ---")
for line in report:
    print(line)

print("\n--- OPTIMIZED YAML ---")
print(yaml.dump(optimized, sort_keys=False))

# Save optimized YAML
with open("optimized_values.yaml", "w", encoding="utf-8") as f:
    yaml.dump(optimized, f, sort_keys=False, allow_unicode=True)

# Save text report
with open("analysis_report.txt", "w", encoding="utf-8") as f:
    f.write("ZopAI Config Optimizer Report\n")
    f.write("="*40 + "\n\n")
    f.write(f"Config Health Score: {health_score}/100\n\n")
    for line in report:
        f.write(line + "\n")
    f.write("\n---\n\n")
    f.write("AI-based Suggestions:\n")
    f.write(ai_suggestions + "\n")

print("\n Files generated: optimized_values.yaml, analysis_report.txt")

# -------------------------
# PDF Report
# -------------------------
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
import datetime

def generate_pdf_report(output_path, health_score, warnings, ai_suggestions, optimized_yaml):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title = Paragraph("<b>ZopAI Config Optimizer Report</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 20))

    # Date
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"Generated on: {date_str}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Health Score
    score_para = Paragraph(f"<b>Config Health Score:</b> {health_score}/100", styles['Heading2'])
    elements.append(score_para)
    elements.append(Spacer(1, 15))

    # Warnings
    if warnings:
        elements.append(Paragraph("<b>Detected Warnings:</b>", styles['Heading2']))
        data = [[w] for w in warnings]
        table = Table(data, colWidths=[450])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

    # AI Suggestions
    if ai_suggestions:
        elements.append(Paragraph("<b>AI Suggestions:</b>", styles['Heading2']))
        elements.append(Paragraph(ai_suggestions.replace("\n", "<br/>"), styles['Normal']))
        elements.append(Spacer(1, 20))

    # Optimized YAML
    elements.append(Paragraph("<b>Optimized YAML:</b>", styles['Heading2']))
    elements.append(Paragraph(f"<font face='Courier'>{optimized_yaml.replace(' ', '&nbsp;').replace('\n','<br/>')}</font>", styles['Normal']))

    doc.build(elements)
    print(f"✅ PDF report saved to {output_path}")


# Generate PDF
generate_pdf_report(
    "analysis_report.pdf",
    health_score,
    report,
    ai_suggestions,
    yaml.dump(optimized, sort_keys=False)
)
