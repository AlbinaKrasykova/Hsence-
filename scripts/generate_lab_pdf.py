#!/usr/bin/env python3
"""Generate printable fake lab PDF from data/fake-lab-panel.json"""
import json
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "data" / "fake-lab-panel.json"
OUT_PATH = ROOT / "data" / "Maya-Chen-Sample-Lab-Report.pdf"


class LabPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "Medichecks", ln=True)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, "Advanced Hormone & Metabolic Panel  |  SAMPLE / FICTIONAL", ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(120, 120, 120)
        self.cell(
            0,
            10,
            f"Page {self.page_no()}  |  Fictional demo for Hsence  |  Not for clinical use",
            align="C",
        )


def flag_symbol(flag: str) -> str:
    return {"high": "H", "low": "L", "ok": ""}.get(flag, "")


def ascii_safe(text: str) -> str:
    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u00b7": " ",
        "\u00b5": "u",
        "\u00d7": "x",
        "\u2079": "9",
        "\u00b2": "2",
        "\u00b9": "1",
        "\u00b0": " ",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode("ascii", "replace").decode("ascii")


def main():
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    p = data["patient"]
    r = data["report"]

    pdf = LabPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Laboratory Report", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(95, 5, f"Patient: {p['name']}")
    pdf.cell(0, 5, f"ID: {p['id']}", ln=True)
    pdf.cell(95, 5, f"DOB: {p['dob']}  |  Sex: {p['sex']}")
    pdf.cell(0, 5, f"Collected: {r['collected'][:10]}", ln=True)
    pdf.cell(0, 5, f"Panel: {ascii_safe(r['lab'])}", ln=True)
    pdf.cell(0, 5, f"Fasting: {'Yes' if r['fasting'] else 'No'}  |  Cycle: {ascii_safe(r['cycleDay'])}", ln=True)
    pdf.ln(3)

    pdf.set_fill_color(250, 245, 239)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(
        0,
        5,
        "CLINICAL NOTE: This is fictional demo data for product testing only. "
        "Not a real patient result. Do not use for medical decisions.",
        fill=True,
    )
    pdf.ln(4)

    col_w = [62, 22, 18, 42, 10]
    headers = ["Test", "Result", "Units", "Reference", "Flag"]

    for section in data["sections"]:
        if pdf.get_y() > 250:
            pdf.add_page()

        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(240, 238, 234)
        pdf.cell(0, 7, ascii_safe(section["title"]), ln=True, fill=True)
        pdf.ln(1)

        pdf.set_font("Helvetica", "B", 7)
        pdf.set_fill_color(248, 248, 248)
        for i, h in enumerate(headers):
            pdf.cell(col_w[i], 6, h, border="B", fill=True)
        pdf.ln()

        pdf.set_font("Helvetica", "", 8)
        for test in section["tests"]:
            if pdf.get_y() > 272:
                pdf.add_page()
                pdf.set_font("Helvetica", "B", 8)
                pdf.cell(0, 6, section["title"] + " (continued)", ln=True)
                pdf.set_font("Helvetica", "", 8)

            val = test["value"]
            if isinstance(val, float):
                val = f"{val:.2f}".rstrip("0").rstrip(".")

            flag = flag_symbol(test["flag"])
            if test["flag"] == "high":
                pdf.set_text_color(180, 70, 70)
            elif test["flag"] == "low":
                pdf.set_text_color(70, 90, 140)
            else:
                pdf.set_text_color(0, 0, 0)

            name = test["name"]
            if test.get("note"):
                name += f" ({test['note']})"

            ref = test["ref"][:38] + (".." if len(test["ref"]) > 38 else "")
            row = [name[:48], str(val), test["unit"][:10], ref, flag]
            for i, cell in enumerate(row):
                pdf.cell(col_w[i], 5.5, ascii_safe(str(cell)), border="B")
            pdf.ln()
            pdf.set_text_color(0, 0, 0)

        pdf.ln(3)

    if pdf.get_y() > 220:
        pdf.add_page()

    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 7, "Pattern summary (automated demo)", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 5, ascii_safe(data["summary"]["pattern"]))
    pdf.ln(2)
    for item in data["summary"]["highlights"]:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 5, "- " + ascii_safe(item))

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUT_PATH))
    print(f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
