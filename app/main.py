from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

# ------------- CRITICAL FIX ---------------
# Import all models so SQLAlchemy registers them
from app.db import models
# ------------------------------------------

from app.db.session import Base, engine
from app.db.models import *

from app.api import (
    routes_agents,
    routes_evals,
    routes_results,
    routes_testcases,
)

app = FastAPI()

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.on_event("startup")
def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)



# Routers
app.include_router(routes_agents.router, prefix="/agents", tags=["agents"])
app.include_router(routes_evals.router, prefix="/evals", tags=["evals"])
app.include_router(routes_results.router, prefix="/results", tags=["results"])
app.include_router(routes_testcases.router, prefix="/testcases", tags=["testcases"])



@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/dashboard")
def dashboard():
    filepath = STATIC_DIR / "dashboard.html"
    return FileResponse(str(filepath), media_type="text/html")

