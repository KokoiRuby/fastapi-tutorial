from dataclasses import dataclass
from app.application.post_service import PostService

# expose
__all__ = ("DIC", )


@dataclass(kw_only=True)
class DependencyInjectionContainer:
    post_service: PostService | None = None


DIC = DependencyInjectionContainer()
