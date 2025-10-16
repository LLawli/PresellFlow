from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.utils.crm_helper import kommo_api_base



router = APIRouter(prefix="/api/v1")

@router.post("/captura")
async def captura_lead(lead: dict):
    tracking_data = {"UTM_CONTENT": None, "UTM_MEDIUM": None, "UTM_SOURCE": None, "UTM_CAMPAIGN": None, "UTM_TERM": None, "UTM_REFERRER": None, "GCLIENTID": None, "GCLID": None, "FBCLID": None}

    for key, value in lead.get("tracking", {}).items():
        if key.upper() in tracking_data:
            tracking_data[key.upper()] = value

    custom_fields = []
    for field, value in tracking_data.items():
        if value:
            custom_fields.append({
                "field_code": field,
                "values": [{"value": value}]
            })
    
    payload_contact = [
        {
            "name": lead.get("name"),
            "custom_fields_values": [
                {
                    "field_code": "PHONE",
                    "values": [
                        {"value": lead.get("tel")}
                    ]
                }
            ]
        }
    ]

    contact_response, contact_status = kommo_api_base(payload_contact, 'POST', '/api/v4/contacts')

    if contact_status != 200:
        return JSONResponse(status_code=contact_status, content={"error": "Failed to create contact", "details": contact_response})
    
    contact_id = contact_response["_embedded"]["contacts"][0]["id"]

    payload_lead = [
        {
            "name": lead.get("name"),
            "pipeline_id": 11704932,
            "status_id": 90440911,
            "custom_fields_values": custom_fields,
            "_embedded": {
                "contacts": [
                    {
                        "id": contact_id,
                        "is_main": True
                    }
                ]
            }
        }
    ]

    lead_response, lead_status = kommo_api_base(payload_lead, 'POST', '/api/v4/leads')

    if contact_status != 200:
        return JSONResponse(status_code=lead_status, content={"error": "Failed to create lead", "details": lead_response})
    
    return JSONResponse(status_code=200, content={"message": "Lead and contact created successfully", "lead_id": lead_response["_embedded"]["leads"][0]["id"], "contact_id": contact_id})