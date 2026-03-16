# context.py
import json
import requests
from auth import login, token_is_expired

TCUSER_URL = "https://mscp.tyrecheck.com/api/api/tcUser"

def _auth_headers(access_token: str) -> dict:
    return {
        "Authorization": f"Bearer {access_token}",
        "Accept": "*/*",
        "Origin": "https://mscp.tyrecheck.com",
        "Referer": "https://mscp.tyrecheck.com/",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/145.0.0.0 Safari/537.36"
        ),
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

def build_user_context(session: requests.Session, token_data: dict, user_code: str = "SPM3DS0317"):

    if token_is_expired(token_data):
        token_data.update(login())

    # IMPORTANTE: generar cookies ai_user / ai_session
    session.get("https://mscp.tyrecheck.com/", timeout=30)

    headers = _auth_headers(token_data["access_token"])

    items = [
        "Avatar",
        "tcLanguage",
        {"name": "tcRole", "items": ["Name"]},
        "tcUnitPressure",
        "tcUnitTreadDepth",
        "tcUnitDistance",
        "tcUserCustomAttributes",
        "tcCurrency",
        "tcUnitTemperature",
        "tcUnitTorque",
        "tcUnitAngle",
        {"name": "tcContactAssignments", "items": ["tcSecurityLevel"]},
        {"name": "tcUserInServiceCenters", "items": ["tcServiceCenter"]}
    ]

    params = {
        "query": f"UserCode = '{user_code}'",   # con espacios EXACTAMENTE como navegador
        "items": json.dumps(items, separators=(",", ":"))  # compacto como DevTools
    }

    r = session.get(TCUSER_URL, headers=headers, params=params, timeout=60)

    if r.status_code != 200:
        raise Exception(f"Error obteniendo contexto usuario: {r.status_code} - {r.text[:800]}")

    data = r.json()

    with open("talleres_rodi.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("UIDs actualizados correctamente.")
    return data