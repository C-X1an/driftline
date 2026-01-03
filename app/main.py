from fastapi import FastAPI
from app.api.routers import sources, status, incidents


app = FastAPI(
    title="Driftline",
    description="Operational risk intelligence for configuration drift",
    version="0.1.0",
)

app.include_router(sources.router)
app.include_router(status.router)
app.include_router(incidents.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
