from flask import Flask, render_template, request, send_file, jsonify
import gspread
from google.oauth2.service_account import Credentials
from io import BytesIO
from zipfile import ZipFile
import openpyxl
import win32com.client as win32
import pythoncom
import os

app = Flask(__name__)

# ===== GOOGLE SHEET CONNECTION =====
import json

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

if os.path.exists("credentials.json"):
    # Local development: use the file
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
else:
    # Render deployment: load from environment variable
    creds_json = os.getenv("GOOGLE_CREDS_JSON")
    if not creds_json:
        raise RuntimeError("❌ Missing GOOGLE_CREDS_JSON environment variable")
    creds_info = json.loads(creds_json)
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

@app.route("/add_site", methods=["POST"])
def add_site():
    data = request.get_json()
    site_name = data.get("site_name")
    site_address = data.get("site_address")

    if not site_name or not site_address:
        return jsonify({"message": "Both fields required!"}), 400

    # Append to Google Sheet
    sheet.append_row([site_name, site_address])
    return jsonify({"message": "✅ Site added successfully!"}), 200

@app.route('/')
def index():
    sites = sheet.get_all_records()
    # Normalize site names to ensure clean display
    site_names = [s.get('site_name') or s.get('Site Name') or "Unknown Site" for s in sites]
    print(f"✅ Normalized site list: {site_names}")
    return render_template('index.html', sites=site_names)


@app.route('/generate', methods=['POST'])
def generate():
    month_year = request.form['month_year']
    selected_sites = request.form.getlist('sites')

    all_sites = sheet.get_all_records()
    all_site_names = [s.get('site_name') or s.get('Site Name') or "Unknown Site" for s in all_sites]

    if "ALL" in selected_sites:
        sites_to_generate = all_sites
    else:
        sites_to_generate = [s for s in all_sites if (s.get('site_name') or s.get('Site Name')) in selected_sites]

    if not sites_to_generate:
        return "❌ No site selected."

    buffer = BytesIO()

    # ===== CREATE ZIP FILE =====
    with ZipFile(buffer, "w") as zipf:
        for site in sites_to_generate:
            site_name = site.get('site_name') or site.get('Site Name') or "Unknown_Site"
            site_address = next((v for k, v in site.items() if 'address' in k.lower()), " ")

            # Create folder name for the site
            folder_name = site_name.replace(" ", "_")

            for i in range(1, 8):
                pdf_path = fill_excel_and_export(site_name, site_address, month_year, i)
                if pdf_path:
                    # Use proper report name instead of "ReportX"
                    report_filename = f"{REPORT_NAMES[i]}.pdf"
                    zipf.write(pdf_path, os.path.join(folder_name, report_filename))
                    os.remove(pdf_path)

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"Reports_{month_year}.zip",
        mimetype="application/zip"
    )


def fill_excel_and_export(site_name, site_address, month_year, report_no):
    """Fill Excel template cells and export to PDF."""
    pythoncom.CoInitialize()

    try:
        template_path = f"Static/Report{report_no}.xlsx"
        if not os.path.exists(template_path):
            print(f"⚠️ Missing template: {template_path}")
            return None

        output_xlsx = f"temp_{site_name}_Report{report_no}.xlsx"
        output_pdf = f"temp_{site_name}_Report{report_no}.pdf"

        # ===== LOAD TEMPLATE =====
        wb = openpyxl.load_workbook(template_path)
        ws = wb.active

        # ===== FILL CELLS =====
        if 1 <= report_no <= 5:
            ws["I5"] = site_address
            ws["I8"] = site_address
            ws["I10"] = site_address
            ws["D10"] = month_year

        elif report_no == 6:
            ws["A5"] = f"Name and address of the Establishment:- {site_address}"
            ws["A9"] = f"There are no Accident for the Month {month_year}"

        elif report_no == 7:
            ws["A4"] = f"Name and address of the Establishment:- {site_address}"
            ws["R4"] = month_year

        wb.save(output_xlsx)

        # ===== EXPORT TO PDF =====
        excel = win32.gencache.EnsureDispatch('Excel.Application')
        excel.Visible = False
        wb_obj = excel.Workbooks.Open(os.path.abspath(output_xlsx))
        wb_obj.ExportAsFixedFormat(0, os.path.abspath(output_pdf))
        wb_obj.Close(False)
        excel.Quit()

        os.remove(output_xlsx)
        return output_pdf

    except Exception as e:
        print(f"❌ Error generating Report {report_no} for {site_name}: {e}")
        return None

    finally:
        pythoncom.CoUninitialize()


if __name__ == '__main__':
    app.run(debug=True)
