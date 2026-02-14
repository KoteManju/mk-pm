from fastapi import FastAPI

app = FastAPI(
    title="Project Management API - Test",
    version="1.0.0",
)

@app.get("/")
async def root():
    return {"message": "API is working", "version": "1.0.0"}

@app.get("/test")
async def test():
    return {"status": "success", "test": True}