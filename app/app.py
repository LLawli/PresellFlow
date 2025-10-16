from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import pages, api

def create_app() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    app.include_router(api.router)
    app.include_router(pages.router)

    return app