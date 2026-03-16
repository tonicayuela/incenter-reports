import json


def match_fleets():

    with open("service_fleet_company_pairs.json", "r", encoding="utf-8") as f:
        service_pairs = json.load(f)

    with open("companies_and_fleets.json", "r", encoding="utf-8") as f:
        security_levels = json.load(f)

    # índice FleetName -> lista de security levels
    fleet_index = {}

    for level in security_levels:

        name = level.get("SecurityLevelName")

        if not name:
            continue

        if name not in fleet_index:
            fleet_index[name] = []

        fleet_index[name].append(level)

    results = []

    for pair in service_pairs:

        fleet_name = pair.get("FleetName")

        matches = fleet_index.get(fleet_name)

        if not matches:
            print("⚠ Fleet no encontrada:", fleet_name)
            continue

        for level in matches:

            new_entry = pair.copy()

            new_entry["SecurityLevelId"] = level.get("SecurityLevelId")
            new_entry["SecurityLevelParentId"] = level.get("SecurityLevelParentId")

            results.append(new_entry)

    with open("match_fleet_company_ids.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print("\nArchivo generado: match_fleet_company_ids.json")
    print("Total registros:", len(results))


if __name__ == "__main__":
    match_fleets()