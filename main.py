from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import random
from fastapi.responses import JSONResponse
from pdf_parser import BookSummaryParser
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# --------------------------------------------------------------------------
# Simple demo data – replace with real PDF parsing later
summaries = [
    "Atomic Habits – small habits compound into massive change.",
    "Deep Work – focused work is the new super‑power.",
    "Man’s Search for Meaning – freedom lies in choosing your attitude.",
]

@app.get("/random_summary", tags=["mcp"])
def get_random_summary():
    """
    Return one random book‑note snippet.
    This endpoint powers the `get_random_summary` action in the MCP manifest.
    """
    return JSONResponse({"summary": random.choice(summaries)})
# --------------------------------------------------------------------------

@app.get("/")
def root():
    """Simple health-check endpoint"""
    return {"status": "ok", "message": "MCP server is running"}