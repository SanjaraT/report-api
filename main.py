from fastapi import FastAPI
from inngest.fast_api import serve
from inngest_client import client
import functions
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Report API")

serve(app, client, [functions.say_hello])

@app.get("/health")
def health():
    return {"status": "ok"}