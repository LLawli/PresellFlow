from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter()
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../pages"))

@router.get("/static/{page}/{file_name:path}")
async def get_static_file(page: str, file_name: str):
    file_name = os.path.join(BASE_DIR, page, "static", file_name)

    if file_name.startswith(BASE_DIR) and os.path.isfile(file_name):
        return FileResponse(file_name)
    elif not file_name.startswith(BASE_DIR):
        raise HTTPException(status_code=403, detail="Forbidden")
    else:
        raise HTTPException(status_code=404, detail="File not found")

@router.get("/{page_name}")
async def get_page(page_name: str):
    file_path = os.path.join(BASE_DIR, f"{page_name}/index.html")
    
    if file_path.startswith(BASE_DIR) and os.path.isfile(file_path):
        return FileResponse(file_path, media_type="text/html")
    elif not file_path.startswith(BASE_DIR):
        raise HTTPException(status_code=403, detail="Forbidden")
    else:
        raise HTTPException(status_code=404, detail="Page not found")
    
