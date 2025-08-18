from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from jinja2 import Template
import datetime
import os

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

    # Optimized YAML (fixed f-string issue)
    elements.append(Paragraph("<b>Optimized YAML:</b>", styles['Heading2']))
    formatted_yaml = optimized_yaml.replace(" ", "&nbsp;").replace("\n", "<br/>")
    elements.append(Paragraph(f"<font face='Courier'>{formatted_yaml}</font>", styles['Normal']))

    doc.build(elements)
    print(f"✅ PDF report saved to {output_path}")


def generate_html_report(output_path, score, warnings, suggestions, optimized_yaml):
    """
    Generate an HTML report with config analysis details.
    """
    template_str = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>ZopAI Config Optimizer Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f9f9f9; }
            h1 { color: #333; }
            .score { font-size: 20px; font-weight: bold; margin: 10px 0; }
            .warning { color: #b30000; margin: 5px 0; }
            pre { background: #eee; padding: 10px; border-radius: 5px; }
            .section { margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>🚀 ZopAI Config Optimizer Report</h1>
        <div class="score">Config Health Score: {{ score }}/100</div>

        <div class="section">
            <h2>⚠️ Warnings</h2>
            {% if warnings %}
                <ul>
                {% for w in warnings %}
                    <li class="warning">{{ w }}</li>
                {% endfor %}
                </ul>
            {% else %}
                <p>No warnings detected ✅</p>
            {% endif %}
        </div>

        <div class="section">
            <h2>🤖 AI Suggestions</h2>
            <p>{{ suggestions | safe }}</p>
        </div>

        <div class="section">
            <h2>📋 Optimized YAML</h2>
            <pre>{{ optimized_yaml }}</pre>
        </div>
    </body>
    </html>
    """

    template = Template(template_str)
    html_content = template.render(
        score=score,
        warnings=warnings,
        suggestions=suggestions.replace("\n", "<br>"),
        optimized_yaml=optimized_yaml
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
