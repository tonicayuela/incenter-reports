# main.py
import requests
import shutil
from auth import login
from context import build_user_context
from companies import download_companies_and_fleets
from inspections_from_service_centers import fetch_inspections
from get_companies_and_fleets import fetch_locations
from extract_fleet_company_pairs import extract_pairs
from match_fleets import match_fleets
from download_reports import download_reports
from date_range import get_date_range
from merge_excels import merge_excels
from send_email import send_email
import sentry_sdk
import pathlib
 
sentry_sdk.init(
    dsn="https://15152c97f4f7bace02c57cf72f5ec551@o4504479594250240.ingest.us.sentry.io/4511026571444224",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)


def main():
    # Eliminar excels "merged" generados en ejecuciones anteriores
    for f in pathlib.Path(".").glob("merged_reports*.xlsx"):
        f.unlink()

    # Vaciar la carpeta downloads
    shutil.rmtree("downloads", ignore_errors=True)
    session = requests.Session()

    # Definir el rango de fechas
    start_date, end_date = get_date_range()    
    print("Fecha inicio:", start_date)
    print("Fecha fin:", end_date)

    # Login
    token_data = login()

    # Obtener contexto usuario 
    user_context = build_user_context(session, token_data)
    
    # Descargar la base de empresas entera
    download_companies_and_fleets(session, token_data)

    # Descargar las inspecciones que se han hecho en los talleres Rodi
    inspections = fetch_inspections(session, token_data, start_date, end_date)

    # Obtener las empresas a las que se les han hecho esas inspecciones
    locations = fetch_locations(session, token_data)

    # Aislar los IDs de flotas y empresas
    pairs = extract_pairs()

    # Cruzar los nombres de las flotas con sus IDs
    match_fleets()

    # Descargar los reports
    download_reports(session, token_data, start_date, end_date)

    # Combinar reports
    merge_excels(start_date, end_date)

    # Enviar report merged
    send_email()

"""
    # Obtener los reports
    payload = {
            "ReportTypeName": "ServicesAndMountedTyres",
            "ReportParameters": {
                "StartDate": "2025-02-03T12:00:00.000+01:00",
                "EndDate": "2026-03-03T12:59:59.999+01:00",
                "CompanyId": "58131849-f02b-47a3-a419-9b3eecff2bc7",
                "FleetId": "9282d489-0f34-4e06-8a37-1ae64db9b657",
                "LocationIds": [],
                "ProductTypeId": None,
                "OutputType": 5
            }
        }

    file_url = generate_report(session, token_data, payload)
    print("FILE URL:", file_url)

    saved_path = download_file(session, token_data, file_url, out_dir="downloads")
    print("GUARDADO EN:", saved_path)"""

if __name__ == "__main__":
    main()