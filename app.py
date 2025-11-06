from flask import Flask, render_template, request, send_file, jsonify
import gspread
from google.oauth2.service_account import Credentials
from io import BytesIO
from zipfile import ZipFile
import openpyxl
import os
import json

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)

# ===== GOOGLE SHEET CONNECTION =====
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_env = os.environ.get("GOOGLE_CREDS")
if not creds_env:
    raise RuntimeError("❌ Missing GOOGLE_CREDS environment variable with service account JSON")

creds_info = json.loads(creds_env)
creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open("Site_database").sheet1

# ===== REPORT NAMES =====
REPORT_NAMES = {
    1: "REGISTER OF DEDUCTIONS FOR DAMAGE OR LOSS",
    2: "REGISTER OF ADVANCES",
    3: "REGISTER OF OVERTIME",
    4: "REGISTER OF FINES",
    5: "REGISTER OF ACCIDENTS AND DANGEROUS OCCURENCES",
    6: "ACCIDENT BOOK",
    7: "Maternity Benefit Register"
}

# ===== ROUTES =====

@app.route("/add_site", methods=["POST"])
def add_site():
    data = request.get_json()
    site_name = data.get("site_name")
    site_address = data.get("site_address")
    if not site_name or not site_address:
        return jsonify({"message": "Both fields required!"}), 400
    sheet.append_row([site_name, site_address])
    return jsonify({"message": "✅ Site added successfully!"}), 200


@app.route('/')
def index():
    sites = sheet.get_all_records()
    site_names = [s.get('site_name') or s.get('Site Name') or "Unknown Site" for s in sites]
    return render_template('index.html', sites=site_names)


@app.route('/generate', methods=['POST'])
def generate():
    month_year = request.form['month_year']
    selected_sites = request.form.getlist('sites')

    all_sites = sheet.get_all_records()

    if "ALL" in selected_sites:
        sites_to_generate = all_sites
    else:
        sites_to_generate = [s for s in all_sites if (s.get('site_name') or s.get('Site Name')) in selected_sites]

    if not sites_to_generate:
        return "❌ No site selected."

    buffer = BytesIO()

    # ===== CREATE ZIP FILE IN MEMORY =====
    with ZipFile(buffer, "w") as zipf:
        for site in sites_to_generate:
            site_name = site.get('site_name') or site.get('Site Name') or "Unknown_Site"
            site_address = next((v for k, v in site.items() if 'address' in k.lower()), " ")
            folder_name = site_name.replace(" ", "_")

            for i in range(1, 8):
                res = fill_excel_and_export_bytes(site_name, site_address, month_year, i)
                if res is None:
                    continue
                pdf_bytes, report_filename = res
                zipf.writestr(os.path.join(folder_name, report_filename), pdf_bytes)

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"Reports_{month_year}.zip",
        mimetype="application/zip"
    )


# ===== PDF GENERATION USING REPORTLAB =====

def fill_excel_and_export_bytes(site_name, site_address, month_year, report_no):
    """
    Generate PDF using ReportLab from Excel template data.
    """
    template_path = os.path.join("static", f"Report{report_no}.xlsx")
    if not os.path.exists(template_path):
        print(f"⚠️ Missing template: {template_path}")
        return None

    try:
        # Load Excel (optional, if you want to read content)
        wb = openpyxl.load_workbook(template_path)
        ws = wb.active

        # Create PDF in memory
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 50

        # Report title
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, REPORT_NAMES.get(report_no, f"Report {report_no}"))
        y -= 30

        # Site info
        c.setFont("Helvetica", 12)
        c.drawString(50, y, f"Site Name: {site_name}")
        y -= 20
        c.drawString(50, y, f"Site Address: {site_address}")
        y -= 20
        c.drawString(50, y, f"Month/Year: {month_year}")
        y -= 30

        # Custom content based on report
        if report_no in range(1, 6):
            # Example: write first 10 rows from column A
            for i, row in enumerate(ws.iter_rows(min_row=1, max_row=10, min_col=1, max_col=1)):
                val = row[0].value
                if val:
                    c.drawString(50, y, str(val))
                    y -= 15
        elif report_no == 6:
            c.drawString(50, y, f"Accident info: There are no Accidents for the Month {month_year}")
        elif report_no == 7:
            c.drawString(50, y, f"Maternity Benefit info for Month: {month_year}")

        # Finish PDF page
        c.showPage()
        c.save()

        buffer.seek(0)
        pdf_bytes = buffer.read()
        report_filename = f"{REPORT_NAMES.get(report_no, f'Report{report_no}')}.pdf"
        return pdf_bytes, report_filename

    except Exception as e:
        print(f"❌ Error generating Report {report_no} for {site_name}: {e}")
        return None


# ===== RUN APP =====
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
