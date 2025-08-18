from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import yaml
import os

from report_generator import generate_pdf_report
from analyzer import analyze_values, compute_score, llm_suggestions

app = FastAPI(
    title="ZopAI Config Optimizer",
    description="A tool to analyze and optimize Kubernetes YAML configs. "
                "Generates optimized YAML, text reports, PDF, and HTML outputs.",
    version="1.0.0",
    contact={
        "name": "Siddhant Roy",
        "url": "https://github.com/roy-sid",
        
    },
)

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_html_report(path, score, report, suggestions, optimized_yaml):
    html_content = f"""
    <html>
    <head>
        <title>ZopAI Config Optimizer Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #16a085; }}
            .score {{ font-size: 20px; font-weight: bold; }}
            .warnings {{ color: #e74c3c; }}
            .suggestions {{ color: #2980b9; }}
            pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>ZopAI Config Optimizer Report</h1>
        <p class="score">Config Health Score: <b>{score}/100</b></p>

        <h2>Warnings</h2>
        <ul class="warnings">
            {''.join(f"<li>{w}</li>" for w in report)}
        </ul>

        <h2>AI-based Suggestions</h2>
        <div class="suggestions">
            <pre>{suggestions}</pre>
        </div>

        <h2>Optimized YAML</h2>
        <pre>{optimized_yaml}</pre>
    </body>
    </html>
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write(html_content)


@app.post("/analyze")
async def analyze_config(file: UploadFile = File(...)):
    contents = await file.read()
    values = yaml.safe_load(contents)

    # Run rule-based analyzer
    optimized, report = analyze_values(values)

    # Save optimized YAML
    opt_path = f"{OUTPUT_DIR}/optimized_values.yaml"
    with open(opt_path, "w", encoding="utf-8") as f:
        yaml.dump(optimized, f)

    # Compute score
    score = compute_score(report)

    # LLM suggestions
    suggestions = llm_suggestions(contents.decode())

    # Save text report
    report_path = f"{OUTPUT_DIR}/analysis_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("ZopAI Config Optimizer Report\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Config Health Score: {score}/100\n\n")
        for line in report:
            f.write(line + "\n")
        f.write("\n---\n\n")
        f.write("AI-based Suggestions:\n")
        f.write(suggestions + "\n")

    # ✅ Save PDF report
    pdf_path = f"{OUTPUT_DIR}/analysis_report.pdf"
    generate_pdf_report(
        pdf_path,
        score,
        [line for line in report if "WARNING" in line],
        suggestions,
        yaml.dump(optimized),
    )

    # ✅ Save HTML report
    html_path = f"{OUTPUT_DIR}/analysis_report.html"
    generate_html_report(
        html_path, score, report, suggestions, yaml.dump(optimized)
    )

    # Return single JSON response
    return JSONResponse(
        content={
            "score": score,
            "warnings": report,
            "optimized_yaml": optimized,
            "ai_suggestions": suggestions,
            "artifacts": {
                "optimized_yaml": opt_path,
                "text_report": report_path,
                "pdf_report": pdf_path,
                "html_report": html_path,
            },
        }
    )


# ============================
# File Download Endpoints
# ============================

@app.get("/download/optimized")
async def download_optimized():
    return FileResponse(
        f"{OUTPUT_DIR}/optimized_values.yaml",
        filename="optimized_values.yaml"
    )


@app.get("/download/report")
async def download_report():
    return FileResponse(
        f"{OUTPUT_DIR}/analysis_report.txt",
        filename="analysis_report.txt"
    )


@app.get("/download/pdf")
async def download_pdf():
    pdf_path = f"{OUTPUT_DIR}/analysis_report.pdf"
    if os.path.exists(pdf_path):
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename="analysis_report.pdf"
        )
    return JSONResponse(content={"error": "Report not found"}, status_code=404)


@app.get("/download/html")
async def download_html():
    html_path = f"{OUTPUT_DIR}/analysis_report.html"
    if os.path.exists(html_path):
        return FileResponse(
            html_path,
            media_type="text/html",
            filename="analysis_report.html"
        )
    return JSONResponse(content={"error": "Report not found"}, status_code=404)
