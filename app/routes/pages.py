import os
import re
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from csscompressor import compress as compress_css
from jsmin import jsmin as compress_js

router = APIRouter()
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../pages"))

def minify_html(content: str) -> str:

    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    content = re.sub(r'>\s+<', '><', content)
    content = re.sub(r'\s{2,}', ' ', content)
    return content.strip()

@router.get("/{page_name}")
async def get_page(page_name: str):
    page_dir = os.path.abspath(os.path.join(BASE_DIR, page_name))
    if not page_dir.startswith(os.path.abspath(BASE_DIR)):
        raise HTTPException(status_code=403, detail="Forbidden")

    file_path = os.path.join(page_dir, "index.html")
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Page not found")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = minify_html(content)
    return HTMLResponse(content, media_type="text/html")

@router.get("/static/{page}/{file_name:path}")
async def get_static_file(page: str, file_name: str):
    file_path = os.path.abspath(os.path.join(BASE_DIR, page, "static", file_name))
    if not file_path.startswith(os.path.abspath(BASE_DIR)):
        raise HTTPException(status_code=403, detail="Forbidden")
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    if file_name.endswith(".css"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = compress_css(content)
        return HTMLResponse(content, media_type="text/css")

    if file_name.endswith(".js"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = compress_js(content)
        return HTMLResponse(content, media_type="application/javascript")

    return FileResponse(file_path)
