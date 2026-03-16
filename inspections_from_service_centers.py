# inspections_from_service_centers.py

import json

API_URL = "https://mscp.tyrecheck.com/api/api/tcInspection"


def _auth_headers(access_token):
    return {
        "Authorization": f"Bearer {access_token}",
        "Accept": "*/*",
        "Origin": "https://incenter-bi.tyrecheck.com",
        "Referer": "https://incenter-bi.tyrecheck.com/",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/145.0.0.0 Safari/537.36"
        ),
    }


def load_service_center_ids():

    with open("talleres_rodi.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    ids = set()

    for user in data["items"]:
        for sc in user.get("tcUserInServiceCenters", []):
            ids.add(sc["ServiceCenterId"])

    return list(ids)


def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def build_query(service_center_ids, start_date, end_date):

    ids = ", ".join([f"'{i}'" for i in service_center_ids])

    return (
        f"InspectionEndTime > '{start_date}' "
        f"AND InspectionEndTime < '{end_date}' "
        f"AND tcUser.tcUserInServiceCenters ANY (ServiceCenterId IN ({ids})) "
        "AND tcUser.tcRole.RoleTypeEnum = '4' "
        "AND tcServiceType.ServiceTypeEnum IN ('0','11','1')"
    )


def fetch_inspections(session, token_data, start_date, end_date):

    service_center_ids = load_service_center_ids()

    print("Service centers encontrados:", len(service_center_ids))

    headers = _auth_headers(token_data["access_token"])

    all_items = []

    for batch in chunk_list(service_center_ids, 20):

        query = build_query(batch, start_date, end_date)

        params = {
            "query": query,
            "items": json.dumps([
                {"name": "InspectionId", "items": []},
                {"name": "InspectionEndTime", "items": []},
                {"name": "InspectionFullNumber", "items": []},
                {"name": "tcUser", "mode": "listed", "items": ["Name"]},
                "VehicleId",
                "LocationId",
                {
                    "name": "tcServiceCenter",
                    "mode": "listed",
                    "items": [
                        {"name": "ServiceCenterName", "items": []},
                        {"name": "ServiceCenterCode", "items": []},
                        {
                            "name": "tcCompany",
                            "mode": "listed",
                            "items": [
                                {"name": "CompanyName", "items": []},
                                {"name": "Code", "items": []}
                            ]
                        }
                    ]
                }
            ]),
            "mode": "listed",
            "limit": 10000,
            "offset": 0
        }

        r = session.get(API_URL, headers=headers, params=params, timeout=120)

        if r.status_code != 200:
            raise Exception(f"Error {r.status_code}: {r.text[:400]}")

        data = r.json()

        items = data.get("items", [])

        print("Inspections recibidas:", len(items))

        all_items.extend(items)

    result = {"items": all_items}

    with open("inspections_raw.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print("Archivo generado: inspections_raw.json")
    print("Total inspections:", len(all_items))

    return result