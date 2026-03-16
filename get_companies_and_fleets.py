import json

API_URL = "https://mscp.tyrecheck.com/api/api/tcLocation"

def chunk_list(lst, size=25):
    for i in range(0, len(lst), size):
        yield lst[i:i+size]


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


def extract_location_ids():

    with open("inspections_raw.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    location_ids = set()

    for item in data.get("items", []):
        loc = item.get("LocationId")
        if loc:
            location_ids.add(loc)

    location_ids = sorted(list(location_ids))

    print("LocationIds únicos encontrados:", len(location_ids))

    return location_ids


def fetch_locations(session, token_data):

    location_ids = extract_location_ids()

    headers = _auth_headers(token_data["access_token"])
    
    all_items = []
    
    for chunk in chunk_list(location_ids, 25):
        ids = ", ".join([f"'{i}'" for i in chunk])
        query = f"SecurityLevelId IN ({ids})"
        
        params = {
            "query": query,
            "items": json.dumps([
                {"name": "LocationName", "items": []},
                {
                    "name": "tcFleet",
                    "mode": "listed",
                    "items": [
                        {"name": "FleetName", "items": []},
                        {
                            "name": "tcCompany",
                            "mode": "listed",
                            "items": ["CompanyName"]
                            }
                    ]
                },
                "SecurityLevelId"
            ]),
            "mode": "listed",
            "applySecurity": "false",
            "applyLookup": "false",
            "applyArchived": "false"
        }
        
        r = session.get(API_URL, headers=headers, params=params, timeout=120)
        
        if r.status_code != 200:
            raise Exception(f"Error {r.status_code}: {r.text[:500]}")
            
        data = r.json()
        
        all_items.extend(data.get("items", []))
    
    data = {"items": all_items}
        
    with open("service_locations.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
            
    print("Archivo generado: service_locations.json")
    print("Locations encontradas:", len(data.get("items", [])))
        
    return data