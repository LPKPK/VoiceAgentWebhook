import os, json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from retell import Retell
app = FastAPI()
retell = Retell(api_key=os.environ["RETELL_API_KEY"])

def decide(age):
    return "PASS" if age is not None and age > 18 else "FAIL"

@app.post("/webhook")
async def webhook(request: Request):
    raw = (await request.body()).decode("utf-8")
    if not retell.verify(raw, api_key=os.environ["RETELL_API_KEY"],
        signature=request.headers.get("X-Retell-Signature")):
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})
    data = json.loads(raw)
    if data["event"] == "call_analyzed":
        analysis = data["call"].get("call_analysis", {})
        custom = analysis.get("custom_analysis_data", {})
        name = custom.get("caller_name")
        age = custom.get("caller_age")
        result = decide(age)
        print(f"{name} (age {age}) -> {result}") # PASS / FAIL
    return JSONResponse(content={}, status_code=200)