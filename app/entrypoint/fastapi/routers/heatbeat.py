from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

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
    return JSONResponse({
        "status": "alive"
    })
