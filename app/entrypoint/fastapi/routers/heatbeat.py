from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.application import application_health_check

router = APIRouter(
    prefix="/heartbeat",
    include_in_schema=False,
)


@router.get("/readiness", status_code=status.HTTP_200_OK)
async def readiness() -> JSONResponse:
    return JSONResponse({
        "status": "ready"
    })


@router.get("/liveness", status_code=status.HTTP_200_OK)
async def liveness() -> JSONResponse:
    await application_health_check()
    return JSONResponse({
        "status": "alive"
    })
