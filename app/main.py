"""Entry point API Pengelolaan Rumah Kos."""
from fastapi import FastAPI

from app import config
from app.core.errors import register_exception_handlers
from app.routers import kamar, penghuni, ringkasan, sewa

app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="API pengelolaan kamar, penghuni, kontrak sewa, dan pembayaran bulanan rumah kos.",
)

register_exception_handlers(app)

for r in (kamar.router, penghuni.router, sewa.router, ringkasan.router):
    app.include_router(r, prefix=config.API_PREFIX)


@app.get("/", tags=["Root"])
async def root():
    return {"service": config.APP_NAME, "version": config.APP_VERSION, "status": "running", "docs": "/docs"}
