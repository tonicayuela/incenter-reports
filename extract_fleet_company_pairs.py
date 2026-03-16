# extract_fleet_company_pairs.py

import json


def extract_pairs():

    with open("service_locations.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    pairs = set()

    for item in data.get("items", []):

        fleet = item.get("tcFleet", {}).get("FleetName")
        company = item.get("tcFleet", {}).get("tcCompany", {}).get("CompanyName")

        if fleet and company:
            pairs.add((fleet, company))

    result = []

    for fleet, company in sorted(pairs):
        result.append({
            "FleetName": fleet,
            "CompanyName": company
        })

    with open("service_fleet_company_pairs.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print("Pares únicos encontrados:", len(result))
    print("Archivo generado: service_fleet_company_pairs.json")

    return result