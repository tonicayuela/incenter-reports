import os
import smtplib
import base64
import shutil
import pathlib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

SENDGRID_API = os.getenv("API_SENDGRID")

SMTP_SERVER = "smtp.sendgrid.net"
SMTP_PORT = 587
SMTP_USER = "apikey"

def send_email():
    FILE_PATH = next(pathlib.Path(".").glob("merged_reports*.xlsx"))

    msg = EmailMessage()

    msg["Subject"] = "[2024-004] - Projecte Incenter vs Neumacheck - Robot informes clients incenter"
    msg["From"] = "no-reply@rodi.es"
    msg["To"] = "antonio.cayuela@rodi.es"#, "ecodinach@rodi.es", "pau.casas@rodi.es", "marc.sanchez@rodi.es", "maria.pedros@rodi.es"

    msg.set_content("[2024-004] - Projecte Incenter vs Neumacheck - Robot informes clients incenter")

    with open(FILE_PATH, "rb") as f:
        file_data = f.read()

    msg.add_attachment(
        file_data,
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=FILE_PATH.name
    )

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:

        server.starttls()

        server.login(SMTP_USER, SENDGRID_API)

        server.send_message(msg)

    print("Email enviado correctamente")


if __name__ == "__main__":
    send_email()