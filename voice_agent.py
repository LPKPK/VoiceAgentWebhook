import os, json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from retell import Retell

app = FastAPI()
RETELL_API_KEY = os.environ["RETELL_API_KEY"]
retell = Retell(api_key=RETELL_API_KEY)

def decide(age):
    return "PASS" if age is not None and 18 < age < 200 else "FAIL"

@app.post("/webhook")
async def webhook(request: Request):
    try:
        rawBody  = (await request.body()).decode("utf-8")
        if not retell.verify(rawBody , api_key=RETELL_API_KEY,
            signature=request.headers.get("X-Retell-Signature")):
            return JSONResponse(status_code=401, content={"message": "Unauthorized"})
        data = json.loads(rawBody)
        if data.get("event") == "call_analyzed":
            call = data.get("call", {})
            analysis = call.get("call_analysis", {})
            custom = analysis.get("custom_analysis_data", {})

            name = custom.get("caller_name")
            age = custom.get("caller_age")
            result = decide(age)

            print(f"{name} (age {age}) -> {result}") # PASS / FAIL
        return JSONResponse(content={}, status_code=200)
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=500, content={"message": "Invalid JSON"}
        )