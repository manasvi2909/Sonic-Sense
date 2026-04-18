from fastapi import FastAPI

app = FastAPI()

@app.get("/api/ping")
async def ping():
    return {"pong": True}
