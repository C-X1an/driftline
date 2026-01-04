from fastapi import FastAPI
from app.api.routers import sources, status, incidents, metrics
from app.api.incidents import router as incidents_router


app = FastAPI(
    title="Driftline",
    description="Operational risk intelligence for configuration drift",
    version="0.1.0",
)

app.include_router(sources.router)
app.include_router(status.router)
app.include_router(incidents.router)
app.include_router(incidents_router)
app.include_router(metrics.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
