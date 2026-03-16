import json
import os
import re
import requests

REPORT_URL = "https://mscp.tyrecheck.com/api/api/Report"


def _auth_headers(access_token):
    return {
        "Authorization": f"Bearer {access_token}",
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Origin": "https://incenter-bi.tyrecheck.com",
        "Referer": "https://incenter-bi.tyrecheck.com/",
        "User-Agent": "Mozilla/5.0",
    }


def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()


def generate_report(session, token_data, payload):

    headers = _auth_headers(token_data["access_token"])

    r = session.post(REPORT_URL, json=payload, headers=headers, timeout=120)

    if r.status_code != 200:
        raise RuntimeError(r.text[:500])

    data = r.json()

    file_url = data.get("FileName")

    if not file_url:
        raise RuntimeError("Respuesta sin FileName")

    return file_url


def download_file(session, token_data, file_url):

    headers = _auth_headers(token_data["access_token"])

    r = session.get(file_url, headers=headers, stream=True, timeout=300)

    if r.status_code != 200:
        raise RuntimeError("Error descargando archivo")

    return r


def download_reports(session, token_data, start_date, end_date):

    with open("match_fleet_company_ids.json", "r", encoding="utf-8") as f:
        pairs = json.load(f)

    os.makedirs("downloads", exist_ok=True)

    total = len(pairs)
    success = 0

    print("\nDescargando reports...")
    print("Total combinaciones:", total)

    for i, pair in enumerate(pairs, 1):

        fleet_name = pair["FleetName"]
        company_name = pair["CompanyName"]

        fleet_id = pair["SecurityLevelId"]
        company_id = pair["SecurityLevelParentId"]

        payload = {
            "ReportTypeName": "ServicesAndMountedTyres",
            "ReportParameters": {
                "StartDate": start_date,
                "EndDate": end_date,
                "CompanyId": company_id,
                "FleetId": fleet_id,
                "LocationIds": [],
                "ProductTypeId": None,
                "OutputType": 5
            }
        }

        try:

            print(f"\n[{i}/{total}] {fleet_name}")

            file_url = generate_report(session, token_data, payload)

            response = download_file(session, token_data, file_url)

            fleet_clean = clean_filename(fleet_name)
            company_clean = clean_filename(company_name)

            filename = f"Flota {fleet_clean} - Empresa {company_clean}.xlsx"
            path = os.path.join("downloads", filename)

            with open(path, "wb") as f:
                for chunk in response.iter_content(1024 * 256):
                    f.write(chunk)

            print("✔ DESCARGADO:", filename)

            success += 1

        except Exception as e:

            print("✖ ERROR:", str(e)[:200])
            continue

    print("\nProceso terminado")
    print("Reports descargados:", success)