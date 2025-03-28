from . import models
import qrcode
import secrets
import os
from wedding_website import settings

QR_CODES_DIR = os.path.join(settings.BASE_DIR, "qr_codes")

def get_qr(hostname:str=None,auth_token:str=None):
    url = f"https://{hostname}/qr/{auth_token}"
    return qrcode.make(url)

def create_auth_qr(email:str=None, hostname:str=None) -> str:
    party = models.Party.objects.get(email=email)
    if party is None:
        raise f"Party not found {email}"
    auth_token = secrets.token_urlsafe(32)
    hashed_auth_token = models.Party.get_token_hash(auth_token)
    party.authentication_token_hash = hashed_auth_token
    party.save()
    img = get_qr(hostname=hostname, auth_token=auth_token)
    if not os.path.isdir(QR_CODES_DIR):
        os.mkdir(QR_CODES_DIR)
    safe_email = "".join(c if c.isalnum() or c in "-._" else "_" for c in email)
    filename = os.path.join(QR_CODES_DIR, f"qr_{safe_email}.png")
    img.save(filename)
    return filename

def create_all_qr_codes(hostname, emails:list[str]=None) -> None:
    if emails is None:
        emails = [party.email for party in models.Party.objects.all()]
    for email in emails:
        create_auth_qr(hostname=hostname, email=email)

