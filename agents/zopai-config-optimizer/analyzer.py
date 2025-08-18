import yaml
import os
import google.generativeai as genai

# -------------------------
# Rule-based Analyzer
# -------------------------
def analyze_values(values):
    report = []

    # existing rules
    sec = values.get("securityContext", {})
    if sec.get("runAsUser", 1000) == 0:
        report.append("WARNING! runAsRoot detected -> set runAsNonRoot=true, runAsUser=1000")
        sec["runAsUser"] = 1000
        sec["runAsNonRoot"] = True
        values["securityContext"] = sec

    res = values.get("resources", {})
    if "limits" not in res or "requests" not in res:
        report.append("WARNING! Resources: Missing CPU/memory -> added default requests/limits")
        values["resources"] = {
            "limits": {"cpu": "500m", "memory": "512Mi"},
            "requests": {"cpu": "250m", "memory": "256Mi"}
        }

    if "livenessProbe" not in values:
        report.append("WARNING! Missing livenessProbe -> added HTTP probe")
        values["livenessProbe"] = {
            "httpGet": {"path": "/", "port": 80},
            "initialDelaySeconds": 10,
            "periodSeconds": 5
        }

    if "readinessProbe" not in values:
        report.append("WARNING! Missing readinessProbe -> added HTTP probe")
        values["readinessProbe"] = {
            "httpGet": {"path": "/", "port": 80},
            "initialDelaySeconds": 10,
            "periodSeconds": 5
        }

    rbac = values.get("rbac", {})
    if not rbac.get("create", False):
        report.append("WARNING! RBAC disabled -> set rbac.create=true")
        values["rbac"] = {"create": True}

    return values, report

# -------------------------
# Heuristic Scoring
# -------------------------
def compute_score(report):
    max_score = 100
    penalty = len(report) * 10   # -10 per warning
    score = max(max_score - penalty, 0)
    return score

# -------------------------
# LLM-based Suggestion Mode (Optional)
# -------------------------
def llm_suggestions(yaml_str: str):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "(AI suggestions disabled: No GOOGLE_API_KEY found)"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"Suggest Kubernetes best practices for this config:\n{yaml_str}")
        return response.text
    except Exception as e:
        return f"(LLM suggestions unavailable: {str(e)})"

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)

    with open("values.yaml") as f:
        values = yaml.safe_load(f)

    optimized, report = analyze_values(values)

    # Write optimized YAML
    with open("outputs/optimized_values.yaml", "w", encoding="utf-8") as f:
        yaml.dump(optimized, f)

    # Compute score
    score = compute_score(report)

    # LLM suggestions (optional)
    with open("values.yaml") as f:
        raw_yaml = f.read()
    suggestions = llm_suggestions(raw_yaml)

    # Write analysis report
    with open("outputs/analysis_report.txt", "w", encoding="utf-8") as f:
        f.write("ZopAI Config Optimizer Report\n")
        f.write("="*40 + "\n\n")
        f.write(f"Config Health Score: {score}/100\n\n")
        for line in report:
            f.write(line + "\n")
        f.write("\n---\n\n")
        f.write("AI-based Suggestions:\n")
        f.write(suggestions + "\n")

    print("Analysis complete. Files written to outputs/")
