#auth.py
import os
import time
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

TOKEN_URL = "https://mscp.tyrecheck.com/api/token"

def login() -> dict:
    
    # Devuelve dict con access_token, refresh_token, expires_at (epoch), raw response, etc.
    username = os.getenv("USER")
    password = os.getenv("PASS")

    if not username or not password:
        raise RuntimeError("Faltan USER/PASS en el .env")

    payload = {
        "grant_type": "password",
        "username": username,
        "password": password,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        # No es obligatorio, pero ayuda a parecer “browser-like”
        "Origin": "https://mscp.tyrecheck.com",
        "Referer": "https://mscp.tyrecheck.com/",
        "User-Agent": "Mozilla/5.0",
    }

    r = requests.post(TOKEN_URL, data=payload, headers=headers, timeout=60)

    if r.status_code != 200:
        raise RuntimeError(f"Login HTTP {r.status_code}: {r.text[:500]}")

    data = r.json()

    # expires_in viene en segundos
    expires_in = int(data.get("expires_in", 0))
    # guardamos un margen de seguridad de 60s
    data["expires_at"] = int(time.time()) + max(expires_in - 60, 0)

    return data


def token_is_expired(token_data: dict) -> bool:
    expires_at = token_data.get("expires_at")
    if not expires_at:
        return True
    return time.time() >= float(expires_at)