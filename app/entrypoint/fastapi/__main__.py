import uvicorn
from app.config.config import config

if __name__ == "__main__":
    # Uvicorn is a lightning-fast ASGI server
    # https://www.uvicorn.org/settings/
    uvicorn.run(
        # pkg.module:app_factory_funcName
        "app.entrypoint.fastapi.factory:create_app",
        host="0.0.0.0",
        port=8000,
        access_log=False,  # disable access log
        reload=config.app.reload,  # hot reload
        reload_dirs=["app"],  # dir to watch for changes
        factory=True,  # indicates the app is created using a factory function
    )
