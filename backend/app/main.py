from fastapi import FastAPI

app = FastAPI(title="Car Data Warehouse API")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "car-data-warehouse-api"
    }
