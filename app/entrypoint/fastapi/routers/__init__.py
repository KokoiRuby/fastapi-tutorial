from .heatbeat import router as heartbeat_router
from .posts import router as posts_router

# controls which symbols should be exported when from 'module import *' is used
__all__ = ("heartbeat_router", "posts_router")

# router lists included all imported routers
routers = (heartbeat_router, posts_router)
