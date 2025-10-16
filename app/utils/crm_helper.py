import httpx
from dotenv import load_dotenv
import os

load_dotenv()

KOMMO_DOMAIN = os.getenv("KOMMO_DOMAIN")
KOMMO_KEY = os.getenv("KOMMO_KEY")


def kommo_api_base(payload, request_type, uri):
    if not KOMMO_DOMAIN or not KOMMO_KEY:
        raise ValueError("KOMMO_DOMAIN and KOMMO_KEY must be set in environment variables")
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {KOMMO_KEY}"
    }

    url = KOMMO_DOMAIN + uri

    with httpx.Client(headers=headers) as client:

        if request_type == 'POST':
            response = client.post(url=url, json=payload)
        elif request_type == 'GET':
            response = client.get(url=url)
        elif request_type == 'PATCH':
            response = client.patch(url=url, json=payload)
        elif request_type == 'DELETE':
            response = client.delete(url=url, json=payload)
        else:
            raise ValueError("Invalid request type")

    return response.json(), response.status_code