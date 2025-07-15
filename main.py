import random
import fitz  # PyMuPDF
from fastapi import FastAPI, Request
from jsonrpcserver import method, async_dispatch

app = FastAPI()

# Load and split PDF content
with fitz.open("book_summaries_for_mcp.pdf") as doc:
    all_text = "\n".join([page.get_text() for page in doc])
    chunks = [p.strip() for p in all_text.split("\n\n") if len(p.strip()) > 40]

@method
async def get_random_book_fact() -> str:
    return random.choice(chunks)

@app.post("/")
async def rpc_handler(request: Request):
    request_text = await request.body()
    response = await async_dispatch(request_text.decode())
    return response