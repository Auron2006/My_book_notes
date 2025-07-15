from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# CORS (keeps your old behaviour)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- NEW: serve .well-known for MCP manifest ------------------------------
well_known_dir = ".well-known"
if not os.path.isdir(well_known_dir):
    raise RuntimeError(
        "'.well-known' folder not found at project root – "
        "make sure it exists and contains mcp.json"
    )

app.mount(
    "/.well-known",
    StaticFiles(directory=well_known_dir, html=False),
    name="well-known",
)
# --------------------------------------------------------------------------

@app.get("/")
def root():
    """Simple health-check endpoint"""
    return {"status": "ok", "message": "MCP server is running"}