from dataclasses import dataclass
from app.application.post_service import PostService
from app.infra.persistence.mysql.database import Database

# expose
__all__ = ("DIC", )


@dataclass(kw_only=True)
class DependencyInjectionContainer:
    post_service: PostService | None = None
    mysql_db: Database | None = None


DIC = DependencyInjectionContainer()
