from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Yo"}

@app.get("/test")
async def test():
    return {"status": "working"}