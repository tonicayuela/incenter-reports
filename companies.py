import json

API_BASE = "https://mscp.tyrecheck.com/api/api/"


def _headers(token_data):
    return {
        "Authorization": f"Bearer {token_data['access_token']}",
        "Accept": "*/*",
        "Origin": "https://incenter-bi.tyrecheck.com",
        "Referer": "https://incenter-bi.tyrecheck.com/",
        "User-Agent": "Mozilla/5.0",
    }


def get_all(session, token_data, endpoint):

    headers = _headers(token_data)

    limit = 1000
    offset = 0
    results = []

    while True:

        params = {
            "limit": limit,
            "offset": offset,
        }

        url = API_BASE + endpoint

        r = session.get(url, headers=headers, params=params, timeout=300)

        if r.status_code != 200:
            raise Exception(f"{endpoint} error: {r.status_code} {r.text[:200]}")

        data = r.json()
        batch = data.get("items", [])

        if not batch:
            break

        results.extend(batch)
        offset += limit

        print(endpoint, "descargados:", len(results))

    return results


def download_companies_and_fleets(session, token_data):

    print("\nDescargando árbol completo de seguridad...")

    levels = get_all(session, token_data, "tcSecurityLevel")

    with open("companies_and_fleets.json", "w", encoding="utf-8") as f:
        json.dump(levels, f, indent=2, ensure_ascii=False)

    print("\nArchivo generado: companies_and_fleets.json")
    print("Total registros:", len(levels))

    return levels