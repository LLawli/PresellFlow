import os
import re
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, Response
from csscompressor import compress as compress_css
from jsmin import jsmin as compress_js

router = APIRouter()
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../pages"))


def minify_html(content: str) -> str:

    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    content = re.sub(r'>\s+<', '><', content)
    content = re.sub(r'\s{2,}', ' ', content)
    return content.strip()

def get_best_image(base_dir: str, file_name: str, accept_header: str) -> FileResponse:
    file_path = os.path.join(base_dir, file_name)
    if not os.path.isfile(file_path):
        return None

    name, ext = os.path.splitext(file_name)
    avif_path = os.path.join(base_dir, f"{name}.avif")
    webp_path = os.path.join(base_dir, f"{name}.webp")

    if "image/webp" in accept_header and os.path.exists(webp_path):
        return FileResponse(webp_path, media_type="image/webp", headers={"Cache-Control": "public, max-age=31536000"})
    if "image/avif" in accept_header and os.path.exists(avif_path):
        return FileResponse(avif_path, media_type="image/avif", headers={"Cache-Control": "public, max-age=31536000"})

    mime_type = "image/png" if ext.lower() == ".png" else "image/jpeg"
    return FileResponse(file_path, media_type=mime_type, headers={"Cache-Control": "public, max-age=31536000"})

@router.get("/{page_name}")
async def get_page(page_name: str, request: Request):
    page_dir = os.path.abspath(os.path.join(BASE_DIR, page_name))
    if not page_dir.startswith(os.path.abspath(BASE_DIR)):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    accept_encoding = request.headers.get("accept-encoding", "")

    if "br" in accept_encoding and os.path.isfile(os.path.join(page_dir, "index.min.html.br")):
        file_path = os.path.join(page_dir, "index.min.html.br")
        headers = {"Content-Encoding": "br"}
        print("Serving Brotli compressed file")
    elif "gzip" in accept_encoding and os.path.isfile(os.path.join(page_dir, "index.min.html.gz")):
        file_path = os.path.join(page_dir, "index.min.html.gz")
        headers = {"Content-Encoding": "gzip"}
    else:
        file_path = os.path.join(page_dir, "index.min.html")

        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="Page not found")
        headers = {}

    headers["Cache-Control"] = "public, max-age=86400"
    return FileResponse(file_path, media_type="text/html", headers=headers)

@router.get("/static/{page}/{file_name:path}")
async def get_static_file(page: str, file_name: str, request: Request):
    accept_encoding = request.headers.get("accept-encoding", "")
    file_path = os.path.abspath(os.path.join(BASE_DIR, page, "static", file_name))
    if not file_path.startswith(os.path.abspath(BASE_DIR)):
        raise HTTPException(status_code=403, detail="Forbidden")
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    headers = {"Cache-Control": "public, max-age=31536000"}

    if file_name.endswith(".css"):
        if "br" in accept_encoding and os.path.isfile(file_path + ".br"):
            file_path = file_path + ".br"
            headers["Content-Encoding"] = "br"
        elif "gzip" in accept_encoding and os.path.isfile(file_path + ".gz"):
            file_path = file_path + ".gz"
            headers["Content-Encoding"] = "gzip"
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            content = compress_css(content)
            return Response(content, media_type="text/css", headers=headers)
        return FileResponse(file_path, media_type="text/css", headers=headers)
    
    if file_name.endswith(".html"):
        if "br" in accept_encoding and os.path.isfile(file_path + ".br"):
            file_path = file_path + ".br"
            headers["Content-Encoding"] = "br"
        elif "gzip" in accept_encoding and os.path.isfile(file_path + ".gz"):
            file_path = file_path + ".gz"
            headers["Content-Encoding"] = "gzip"
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            content = minify_html(content)
            return Response(content, media_type="text/html", headers=headers)
        return FileResponse(file_path, media_type="text/html", headers=headers)


    if file_name.endswith(".js"):
        if "br" in accept_encoding and os.path.isfile(file_path + ".br"):
            file_path = file_path + ".br"
            headers["Content-Encoding"] = "br"
        elif "gzip" in accept_encoding and os.path.isfile(file_path + ".gz"):
            file_path = file_path + ".gz"
            headers["Content-Encoding"] = "gzip"
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            content = compress_js(content)
            return Response(content, media_type="application/javascript", headers=headers)
        return FileResponse(file_path, media_type="application/javascript", headers=headers)
    
    if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
        accept_header = request.headers.get("accept", "")
        response = get_best_image(os.path.join(BASE_DIR, page, "static"), file_name, accept_header)
        if response is None:
            raise HTTPException(status_code=404, detail="File not found")
        return response
    
    if "br" in accept_encoding and os.path.isfile(file_path + ".br"):
        file_path = file_path + ".br"
        type = "application/javascript"
        headers["Content-Encoding"] = "br"
    elif "gzip" in accept_encoding and os.path.isfile(file_path + ".gz"):
        file_path = file_path + ".gz"
        headers["Content-Encoding"] = "gzip"
        type = "application/javascript"
    else:
        type = None

    return FileResponse(file_path, headers=headers, media_type=type)
