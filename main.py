from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from inngest.fast_api import serve
from inngest_client import client
import functions
import inngest
from dotenv import load_dotenv
import uuid

load_dotenv()

app = FastAPI(title="Report API")

serve(app, client, [functions.say_hello, functions.make_report, functions.heartbeat])

# in-memory store
reports: dict = {}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reports", status_code=202)
async def create_report(body: dict):
    topic = body.get("topic")

    if not topic or not str(topic).strip():
        raise HTTPException(status_code=400, detail="topic is required")

    report_id = str(uuid.uuid4())[:8]
    reports[report_id] = {
        "id": report_id,
        "topic": topic,
        "status": "pending",
    }

    await client.send(inngest.Event(
        name="report/requested",
        data={"id": report_id, "topic": topic},
    ))

    return JSONResponse(
        status_code=202,
        content={"id": report_id, "status": "pending"}
    )

@app.get("/reports/{report_id}")
def get_report(report_id: str):
    print(f"GET called for {report_id} — dict has: {list(reports.keys())}", flush=True)
    if report_id not in reports:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    return reports[report_id] 

@app.get("/reports")
def list_reports():
    return reports