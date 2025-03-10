# Note

## Project Initiliaztion

```bash
python -m venv .venv
```

```bash
source .venv/bin/activate
```

```python
touch requirements.txt
```

```python
# requirements.txt
fastapi==0.115.11
uvicorn==0.34.0
dynaconf==3.2.10
```

```python
pip install -r requirements.txt
```

```bash
.
├── app
│   ├── __init__.py
│   └── factory.py # 👈
└── requirements.txt
```

### Lifespan

Add [lifespan](https://fastapi.tiangolo.com/advanced/events/?h=lifespan#alternative-events-deprecated) on application.

```python
# ./app/factory.py

from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager


def create_app() -> FastAPI:

    async def on_startup(app: FastAPI) -> None:
        print("Starting up")

    async def on_shutdown(app: FastAPI) -> None:
        print("Shutting down")

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator:
        await on_startup(app)
        try:
            yield
        finally:
            await on_shutdown(app)

    app = FastAPI(
        title="Post Management Service API",
        description="API to manage posts",
        version="0.0.1",
        lifespan=lifespan,
    )

    return app
```

Main entry. Using [uvicorn](https://www.uvicorn.org/) to run FastAPI instance.

```python
 # ./app/__main__.py

import uvicorn


if __name__ == "__main__":
    # Uvicorn is a lightning-fast ASGI server
    # https://www.uvicorn.org/settings/
    uvicorn.run(
        # pkg.module:app_factory_funcName
        "app.factory:create_app",
        host="0.0.0.0",
        port=8000,
        access_log=False,    # disable access log
        reload=True,         # hot reload
        reload_dirs=["app"],  # dir to watch for changes
        factory=True,        # indicates the app is created using a factory function
    )

```

Start the FastAPI app.

```python
python -m app
```

Verify by [httpie](https://httpie.io/cli).

```python
http get http://localhost:8000
```

### Heartbeat

Define **routers** used to group path operations. 

```bash
.
├── app
│   ├── __init__.py
│   ├── __main__.py
│   ├── factory.py
│   └── routers         # 👈
│       ├── __init__.py
│       └── heartbeat.py 
└── requirements.txt
```

```python
# ./app/routers/heartbeat.py
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
async def readiness() -> JSONResponse:
    return JSONResponse({
        "status": "alive"
    })

```

Include in `__init__.py` so that it can be imported into app.

```python
# ./app/routers/__init__.py
from .heatbeat import router as heartbeat_router

__all__ = ("heartbeat_router", )

routers = (heartbeat_router, )
```

Include routers in app.

```python
# ./app/factory.py

from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from .routers import routers


def create_app() -> FastAPI:

    ...

    app = FastAPI(
        title="Post Management Service API",
        description="API to manage posts",
        version="0.0.1",
        lifespan=lifespan,
    )
    
    for router in routers:
        app.include_router(router)

    return app
```

Verify.

```python
http get localhost:8000/heartbeat/readiness
http get localhost:8000/heartbeat/liveness
```

## Configuration

Use [Dynaconf](https://www.dynaconf.com/) for API app.

```bash
➜  Fastapi tree
.
├── Note.md
├── app
│   ├── __init__.py
│   ├── __main__.py
│   ├── config         # 👈
│   │   ├── config.py
│   │   └── default
│   │       ├── default.toml
│   │       └── default.yaml
│   ├── factory.py
│   └── routers
│       ├── __init__.py
│       ├── heatbeat.py
│       └── posts.py
└── requirements.txt
```

```toml
# ./app/config/default/default.toml

[app]
title = "Post Management Service API"
description = "API to manage posts"
version = "0.0.1"
reload = true
```

```yaml
# ./app/config/default/default.yaml

app:
  title: "Post Management Service API"
  description: "API to manage posts"
  version: "0.0.1"
  reload: true
```

```python
# ./app/config/config.py

import glob
from dynaconf import Dynaconf  # type: ignore
from pathlib import Path

# root dir is /app/config
ROOT_DIR = Path(__file__).parent

# controls which symbols should be exported when from 'module import *' is used
__all__ = ("config", )


# find all files given a filepath pattern
def read_files(filepath: str) -> list:
    return glob.glob(filepath, root_dir=ROOT_DIR)


# read all yaml files in the default dir
# confs = read_files("default/*.yaml")
confs = read_files("default/*.toml")

config = Dynaconf(
    settings_files=confs,
    # core_loaders=["YAML"],  # yaml as the config file format
    core_loaders=["TOML"],  # toml as the config file format
    load_dotenv=True,  # enable loading .env file
    root_path=ROOT_DIR,  # /app/config
)
```

Modify factory to use config.

```python
# ./app/factory.py

from app.config.config import config


def create_app() -> FastAPI:

    ...

    app = FastAPI(
        title=config.app.title,
        description=config.app.description,
        version=config.app.version,
        lifespan=lifespan,
    )

    for router in routers:
        app.include_router(router)

    return app

```

Modify `__main__.py` to use config.

```python
# ./app/__main__.py

from app.config.config import config


if __name__ == "__main__":
    # Uvicorn is a lightning-fast ASGI server
    # https://www.uvicorn.org/settings/
    uvicorn.run(
        ...
        reload=config.app.reload,  # hot reload
        ...
    )
```

Verify [doc](http://localhost:8000/docs) page in browser.

### Docker

```bash
.
├── Makefile # 👈
├── app   
│   ├── __init__.py
│   ├── __main__.py
│   ├── config
│   │   ├── config.py
│   │   └── default
│   │       ├── default.toml
│   │       └── default.yaml
│   ├── factory.py
│   └── routers
│       ├── __init__.py
│       ├── heatbeat.py
│       └── posts.py
├── docker # 👈
│   ├── Dockerfile
│   └── docker-compose.yml
```

### `Dockerfile`

```dockerfile
# Build stage - dep
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
# disable cache to save docker image size
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# security practice using non-root user
RUN useradd -m app

# Copy only the installed packages from builder stage
COPY --from=builder /usr/local /usr/local
# Copy the rest of the application code to container
COPY --chown=app:app . .

# Make sure scripts in /usr/local/bin are usable
ENV PATH=/usr/local/bin:$PATH

# Change to non-root user
USER app

# Command to run the application
CMD ["python", "-m", "app"]
```

### `docker-compose.yml`

```yaml
services:
  # service name
  app:
    build:
      context: ./..
      dockerfile: ./docker/Dockerfile
    ports:
      - "8000:8000"
    # map src to container, so that any changes on local will be reflected in real-time
    volumes:
      - ./../:/app
    environment:
      - APP_ENV=local
    healthcheck:
      test: "curl -f http://localhost:8000/heartbeat/readiness || exit 1"
      interval: 20s
      timeout: 3s
      retries: 10
    networks:
      - fastapi-network

networks:
  fastapi-network:
    driver: bridge
```

### `.dockerignore`

```bash
# Python
__pycache__/
*.py[cod]
*.pyd
*.so

# Docker
Dockerfile
docker-compose.yml
docker/

# Git
.git
.gitignore

# ENV
.env
.venv
env/
.venv/

# PEP 582
__pypackages__/

# Misc
Makefile
```

### `Makefile`

```makefile
DOCKER_COMPOSE = docker compose -f ./docker/docker-compose.yml -p project # set project name to 'project'

# .PHONY tells Make that 'build' is not a file target
.PHONY: build
build:
	$(DOCKER_COMPOSE) build app

# .PHONY tells Make that 'up' is not a file target
.PHONY: up
# Up and attach to 'app' service logs
up: build
	$(DOCKER_COMPOSE) up --attach app

# .PHONY tells Make that 'down' is not a file target
.PHONY: down
# Remove volumes and locally built images
down:
	$(DOCKER_COMPOSE) down --volumes --rmi=local
```

Up and Down.

```bash
make up
make down
```

## CRUD

### Fake Database

Use `@dataclass` to simulate database.

```bash
.
├── Makefile
├── app   
│   ├── __init__.py
│   ├── __main__.py
│   ├── config
│   │   ├── config.py
│   │   └── default
│   │       ├── default.toml
│   │       └── default.yaml
│   ├── factory.py
│   ├── fake_database.py  # 👈
│   └── routers
│       ├── __init__.py
│       ├── heatbeat.py
│       └── posts.py
├── docker
│   ├── Dockerfile
│   └── docker-compose.yml
```

```python
# ./app/fake_database.py

from dataclasses import dataclass, field
from datetime import datetime
import random

# expose
__all__ = ("fake_database",)


# simulate database
@dataclass
class FakeDatabase:
    posts: dict = field(default_factory=dict)  # each filed is a table
    users: dict = field(default_factory=dict)

    # called after __init__ to populate the tables
    def __post_init__(self):
        self.users = {
            # dict comprehension
            user_id: {
                "user_id": user_id,
                "email": f"user_{user_id}@example.com",
                "created": datetime.utcnow(),
            }
            for user_id in range(1, 4)
        }
        self.posts = {
            post_id: {
                "post_id": post_id,
                "title": f"FastAPI tutorial {post_id}",
                "craeted": datetime.utcnow(),
                "owner_id": random.choice(list(self.users.keys())),
            }
            for post_id in range(1, 6)
        }


fake_database = FakeDatabase()
```

```python
# ./app/posts.py

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.fake_database import fake_database

# expose
__all__ = ("router", )

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    description="Get all posts"
)
async def list_posts() -> JSONResponse:  # type: ignore
    return fake_database.posts  # type: ignore

```

Verify.

```bash
make up
```

```bash
http get localhost:8000/posts
```

### Schema

```bash
.
├── Makefile
├── app
│   ├── __init__.py
│   ├── __main__.py
│   ├── config
│   │   ├── config.py
│   │   └── default
│   │       ├── default.toml
│   │       └── default.yaml
│   ├── factory.py
│   ├── fake_database.py
│   ├── routers
│   │   ├── __init__.py
│   │   ├── heatbeat.py
│   │   └── posts.py
│   └── schema  # 👈
│       ├── __init__.py
│       ├── post.py
│       └── user.py
├── docker
│   ├── Dockerfile
│   └── docker-compose.yml
└── requirements.txt
```

```python
# ./app/schema/user.py

from pydantic import BaseModel, Field
from datetime import datetime, UTC


class User(BaseModel):
    user_id: int
    email: str
    created: datetime = Field(default_factory=lambda: datetime.now(UTC))
```

```python
# ./app/schema/post.py

from pydantic import BaseModel, Field
from datetime import datetime, UTC
from .user import User


class Post(BaseModel):
    post_id: int
    title: str
    created: datetime = Field(default_factory=lambda: datetime.now(UTC))
    user: User
```

### List all posts

```python
# ./app/routers/posts.py

...


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    description="Get all posts",
    response_model=list[Post]
)
async def list_posts() -> list[Post]:
    return [
        Post(
            post_id=post["post_id"],
            title=post["title"],
            created=post["created"],
            user=User(
                user_id=post["user_id"],
                # get user by user_id in post
                email=fake_database.users[post["user_id"]]["email"],
                created=fake_database.users[post["user_id"]]["created"]
            )
        )
        for post in fake_database.posts.values()
    ]
```

Verify.

```bash
http get localhost:8000/posts
```

### Create a post

Input model

```python
# ./app/schema/post.py

...


class PostCreateInput(BaseModel):
    title: str
    user_id: int
```

```python
# ./app/routers/posts.py

...


@router.post(
    "",
    description="Create a post",
    response_model=Post,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(input_post: PostCreateInput) -> Post:
    print(input_post)

    if input_post.user_id not in fake_database.users:
        raise HTTPException(
            detail="User not found",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    # create post based on input
    post = Post(
        # increment
        post_id=len(fake_database.posts) + 1,
        title=input_post.title,
        user=User(
            user_id=input_post.user_id,
            email=fake_database.users[input_post.user_id]["email"],
            created=fake_database.users[input_post.user_id]["created"]
        ),
    )

    # add post to database
    fake_database.posts[post.post_id] = {
        "post_id": post.post_id,
        "title": post.title,
        "created": post.created,
        "user_id": post.user.user_id,
    }

    return post
```

Verify.

```bash
http get localhost:8000/posts title="My New Post" user_id=1
```

```bash
http get localhost:8000/posts
```

### Update a post

Update model.

```python
# ./app/schema/post.py

...


class PostUpdateInput(BaseModel):
    title: str
```

```python
# ./app/routers/posts.py

...


@router.patch(
    "/{post_id}",
    description="Update a post",
    response_model=Post,
    status_code=status.HTTP_200_OK,
)
async def update_post(post_id: int, update_post: PostUpdateInput) -> Post:
    if post_id not in fake_database.posts:
        raise HTTPException(
            detail="Post not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # update in db
    post = fake_database.posts[post_id]
    post["title"] = update_post.title

    # you cannot return `post` as it's dict
    return Post(
        post_id=post["post_id"],
        title=post["title"],
        created=post["created"],
        user=User(
            user_id=post["user_id"],
            email=fake_database.users[post["user_id"]]["email"],
            created=fake_database.users[post["user_id"]]["created"]
        )
    )
```

Verify.

```bash
http patch localhost:8000/posts title="My New Post Title"
```

```bash
http get localhost:8000/posts/1
```

### Delete a post

```python
# ./app/routers/posts.py

...


@router.delete(
    "/{post_id}",
    description="Delete a post",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(post_id: int) -> None:
    if post_id not in fake_database.posts:
        raise HTTPException(
            detail="Post not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # delete in db
    del fake_database.posts[post_id]
    return None
```

Verify.

```bash
http patch localhost:8000/posts post_id="1"
```

```bash
http get localhost:8000/posts
```

```bash
http get localhost:8000/posts/1
```

## [Hexagonal Architecture](https://medium.com/ssense-tech/hexagonal-architecture-there-are-always-two-sides-to-every-story-bc0780ed7d9c)

Hexagonal Architecture, also known as **Ports and Adapters** Architecture, is a system design approach aimed at decoupling a software's core business logic from its external interactions. 

Core components:

1. **Entities** are <u>Domain models</u> and <u>Business Logics</u>.
2. **Ports** are the <u>interfaces</u> that define how external systems communicate with the core logic.
   - **Inbound Ports**: Define how the external world (such as a user interface, API, or message queue) can interact with the core system.
   - **Outbound Ports**: Define how the core system interacts with external systems (such as databases or external APIs) to send or receive data.
3. **Adapters** are the <u>implementation</u> of the ports. <u>Adapters use ports to interact with the application.</u>
4. **Application Services**, also known as <u>Interactors</u> or <u>Use Cases</u>, act as the <u>intermediary</u> between the entities and the external layers
5. **Repositories** as <u>persistence</u> layer are used to manage the persistence of data.
6. **Transport Layer** handles the communication between <u>external users</u> or systems and the application.
7. **External systems** include databases, APIs, message queues, and other <u>infrastructure</u> components

![img](https://miro.medium.com/v2/resize:fit:1563/1*90nuqeg3RNdK9S-KhFlIag.png)

### Refractor

```bash
.
├── Makefile
├── app
│   ├── __init__.py
│   ├── application # 👈 Application Service
│   │   └── __init__.py
│   ├── config
│   │   ├── config.py
│   │   └── default
│   │       ├── default.toml
│   │       └── default.yaml
│   ├── domain # 👈 Domain
│   │   └── __init__.py
│   ├── entrypoint # 👈 Inbound Ports
│   │   ├── __init__.py
│   │   └── fastapi
│   │       ├── __init__.py
│   │       ├── __main__.py
│   │       ├── factory.py
│   │       ├── routers
│   │       │   ├── __init__.py
│   │       │   ├── heatbeat.py
│   │       │   └── posts.py
│   │       └── schema
│   │           ├── __init__.py
│   │           ├── post.py
│   │           └── user.py
│   └── infra # 👈 Outbound Ports
│       ├── __init__.py
│       └── persistence
│           ├── __init__.py
│           └── mem_db
│               ├── __init__.py
│               └── fake_database.py
├── docker
│   ├── Dockerfile
│   └── docker-compose.yml
└── requirements.txt
```

```python
# ./app/entrypoint/fastapi/factory.py

from app.entrypoint.fastapi.routers import routers

...
```

```python
# ./app/entrypoint/fastapi/__main__.py

...

if __name__ == "__main__":
    # Uvicorn is a lightning-fast ASGI server
    # https://www.uvicorn.org/settings/
    uvicorn.run(
        # pkg.module:app_factory_funcName
        "app.entrypoint.fastapi.factory:create_app",
        ...
    )
```

```python
# ./app/entrypoint/fastapi/schema/user.py

...

from app.entrypoint.fastapi.schema.user import User

...
```

```python
# ./app/entrypoint/fastapi/routers/posts.py

...

from app.infra.persistence.mem_db.fake_database import fake_database
from app.entrypoint.fastapi.schema.post import Post, PostCreateInput, PostUpdateInput
from app.entrypoint.fastapi.schema.user import User

...
```

```dockerfile
# ./docker/Dockerfile

...

# Command to run the application
CMD ["python", "-m", "app.entrypoint.fastapi"]

...
```

Verify.

```bash
make up
```

```bash
http get localhost:8000/heartbeat/readiness
http get localhost:8000/heartbeat/liveness
http get localhost:8000/posts
```

### Domain 

#### Models

Use builtin `@dataclass` to avoid dependency on 3PP.

```python
# ./app/domain/models/post.py

from dataclasses import dataclass, field
from datetime import datetime, UTC


# kw_only=True means that all fields in the dataclass
# must be passed as keyword arguments when creating an instance.
@dataclass(kw_only=True)
class Post:
    post_id: int
    title: str
    created: datetime = field(default_factory=lambda: datetime.now(UTC))
    update: datetime = field(default_factory=lambda: datetime.now(UTC))
```

```python
# ./app/domain/models/user.py

from dataclasses import dataclass, field
from datetime import datetime, UTC


# kw_only=True means that all fields in the dataclass
# must be passed as keyword arguments when creating an instance.
@dataclass(kw_only=True)
class User:
    user_id: int
    email: str
    created: datetime = field(default_factory=lambda: datetime.now(UTC))
    update: datetime = field(default_factory=lambda: datetime.now(UTC))
```

#### vs.

- **Domain Models**
  - Represent core <u>business logic</u> and rules
  - Used internally in the application
  - More efficient for internal operations
  - <u>Can include business methods and behaviors</u>
  - Independent of API/presentation concerns
- **View Models** (Pydantic Schema)
  - Handle <u>API input/output</u> validation
  - Manage data serialization/deserialization
  - Document API endpoints (OpenAPI/Swagger)
  - Handle request/response data transformation
  - Focus on data validation and API contracts

#### BaseModel

Create base class and use [Psygnal](https://psygnal.readthedocs.io/en/latest/) notify fields changes on dataclasses by [observer pattern](https://en.wikipedia.org/wiki/Observer_pattern). When a field is changed:
- The `SignalGroupDescriptor` detects the change
- The observer (`_events`) emits a signal
- The observer calls the callback (`_on_event`)

```python
class User(BaseModel):
    name: str

user = User(name="John")
user.name = "Jane"  # Field change happens

# Flow:
# 1. Field change detected by SignalGroupDescriptor
# 2. _events (observer) emits signal
# 3. _events calls _on_event(info)
# 4. Changes are tracked in _modified_fields (dict)
```

```bash
# ./requirements.txt

dynaconf==3.2.10
fastapi==0.115.11
uvicorn==0.34.0
psygnal==0.12.0 # 👈
```

```python
# ./app/domain/models/base.py
from dataclasses import dataclass
from typing import ClassVar, Any, Self
from psygnal import EmissionInfo, SignalGroupDescriptor


# BaseModel as observer to nofitfy dataclasses whenever there is a change / are changes on the dataclass fields
# https://psygnal.readthedocs.io/en/latest/dataclasses/?h=signalgroupdescriptor#evented-dataclasses
@dataclass
class BaseModel:

    # cls var shared across all instance
    # Uses Psygnal's SignalGroupDescriptor to emit signals when fields change
    _events: ClassVar[SignalGroupDescriptor] = SignalGroupDescriptor()

    # connects the event
    def __post_init__(self):
        # connect observer to callback
        self._events.connect(self._on_event)
        # a dict to keep modified fields
        self._modified_fields = {}

    # callback
    def _on_event(self, info: EmissionInfo):
        # unpack EmissionInfo
        # EmissionInfo.args is tuple(new, old)
        # new_value, original_value = list(info.args)
        new_value, original_value = info.args
        # return if no fields changed
        if new_value == original_value:
            return
        # get touched field name
        field_name = info.signal.name

        # add to dict if not in dict
        if field_name not in self._modified_fields:
            self._modified_fields[field_name] = {
                "original_value": original_value,
                "new_value": new_value,
            }
        # update if field in dict
        else:
            self._modified_fields[field_name].update(
                {"new_value": new_value}
            )

    # called when setting attribute
    # and call corresponding validate_<field_name> method
    def __setattr__(self, key: str, value: Any) -> None:
        if method := getattr(self, f"validate_{key}", None):
            value = method(value)
        # avoid infinite recursion
        super().__setattr__(key, value)

    # Accessible by instance.modified_fields
    @property
    def modified_fields(self) -> dict:
        return self._modified_fields

    # rollback changes
    def rollback(self) -> Self:
        for _field, _value in self.modified_fields.items():
            # will call __setattr__
            setattr(self, _field, _value["original_value"])
        return self
```

```python
# ./app/domain/models/post.py

from app.domain.models.base import BaseModel
from app.domain.models.user import User


@dataclass(kw_only=True)
class Post(BaseModel):
    ...
    user: User | None = field(default=None)

    @staticmethod
    def validate_title(title: str) -> str:
        if len(title.strip()) == 0:
            raise ValueError("Title cannot be empty")
        return title.strip()
```

Verify.

```python
post = Post(post_id=1, title="origin title")

# validation required, raise Exception
# post.title = ""

# aware of modified fields
post.title = "new title"
assert post.modified_fields == {
    "title": {
        "original_value": "origin title",
        "new_value": "new title"
    }
}

# support rollback
post.rollback()
assert post.modified_fields == {}
assert post.title == "origin title"
```

```python
# ./app/domain/models/user.py

...

from app.domain.models.base import BaseModel
import re

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)


@dataclass(kw_only=True)
class User(BaseModel):
    ...

    @staticmethod
    def validate_email(email: str) -> str:
        if not EMAIL_REGEX.match(email):
            raise ValueError("Invalid email")
        return email
```

#### Repositories

Expose outbound ports to perform data model persistence.

```bash
.
├── Makefile
├── app
│   ├── __init__.py
│   ├── application
│   │   └── __init__.py
│   ├── config
│   │   ├── config.py
│   │   └── default
│   │       ├── default.toml
│   │       └── default.yaml
│   ├── domain
│   │   ├── __init__.py
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── post.py
│   │   │   └── user.py
│   │   └── repositories # 👈
│   │       └── __init__.py
│   ├── entrypoint
│   │   ├── __init__.py
│   │   └── fastapi
│   │       ├── __init__.py
│   │       ├── __main__.py
│   │       ├── factory.py
│   │       ├── routers
│   │       │   ├── __init__.py
│   │       │   ├── heatbeat.py
│   │       │   └── posts.py
│   │       └── schema
│   │           ├── __init__.py
│   │           ├── post.py
│   │           └── user.py
│   └── infra
│       ├── __init__.py
│       └── persistence
│           ├── __init__.py
│           └── mem_db
│               ├── __init__.py
│               └── fake_database.py
├── docker
│   ├── Dockerfile
│   └── docker-compose.yml
└── requirements.txt
```

Use `@abstractmethod` to define interfaces.

```python
# ./app/domain/repositories/post.py

from abc import ABC, abstractmethod
from app.domain.models.post import Post


class PostRepository(ABC):
    @abstractmethod
    async def create(self, post: Post) -> Post: ...

    @abstractmethod
    async def get_by_id(self, post_id: int) -> Post: ...

    @abstractmethod
    async def get_posts(self) -> list[Post]: ...

    @abstractmethod
    async def update(self, post: Post) -> Post: ...

    @abstractmethod
    async def delete(self, post_id: int) -> None: ...
```

```python
# ./app/domain/repositories/user.py

from abc import ABC, abstractmethod
from app.domain.models.user import User


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> User: ...
```

Import repository inside `__init__.py`.

```python
# ./app/domain/repositories/__init__.py

from app.domain.repositories.post import PostRepository
from app.domain.repositories.user import UserRepository
```

#### Application Services

Business logics for use cases which invoke Ports.

```bash
.
├── Makefile
├── app
│   ├── __init__.py
│   ├── application  # 👈
│   │   └── __init__.py
│   ├── config
│   │   ├── config.py
│   │   └── default
│   │       ├── default.toml
│   │       └── default.yaml
│   ├── domain
│   │   ├── __init__.py
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── post.py
│   │   │   └── user.py
│   │   └── repositories
│   │       ├── __init__.py
│   │       ├── post.py
│   │       └── user.py
│   ├── entrypoint
│   │   ├── __init__.py
│   │   └── fastapi
│   │       ├── __init__.py
│   │       ├── __main__.py
│   │       ├── factory.py
│   │       ├── routers
│   │       │   ├── __init__.py
│   │       │   ├── heatbeat.py
│   │       │   └── posts.py
│   │       └── schema
│   │           ├── __init__.py
│   │           ├── post.py
│   │           └── user.py
│   └── infra
│       ├── __init__.py
│       └── persistence
│           ├── __init__.py
│           └── mem_db
│               ├── __init__.py
│               └── fake_database.py
├── docker
│   ├── Dockerfile
│   └── docker-compose.yml
└── requirements.txt
```

Modify models.

```python
# ./app/domain/models/post.py

...

@dataclass(kw_only=True)
class Post(BaseModel):
    post_id: int | None = None
    ...
```

```python
# ./app/domain/models/user.py

@dataclass(kw_only=True)
class User(BaseModel):
    ...
    email: str | None = None
    ...

    @staticmethod
    def validate_email(email: str) -> str:
        if not None and not EMAIL_REGEX.match(email):
            ...
```

Service.

```python
# ./app/application/post_service.py

from app.domain.models.post import Post
from app.domain.repositories import PostRepository, UserRepository


class PostService:
    def __init__(self, post_repository: PostRepository, user_repository: UserRepository):
        self.post_repository = post_repository
        self.user_repository = user_repository

    async def create_post(self, user_id: int, title: str) -> Post:
        if not (user := await self.user_repository.get_by_id(user_id)):
            raise Exception("User not found")

        post = Post(title=title, user=user)
        return await self.post_repository.create(post)

    async def get_post(self, post_id: int) -> Post:
        if not (post := await self.post_repository.get_by_id(post_id)):
            raise Exception("Post not found")

        # https://mypy.readthedocs.io/en/latest/error_code_list.html#code-union-attr
        assert post.user
        if not (user := await self.user_repository.get_by_id(post.user.user_id)):
            raise Exception("User not found")

        post.user = user

        return post

    # TODO: pagination
    async def list_posts(self) -> list[Post]:
        posts = await self.post_repository.get_posts()

        for post in posts:
            # https://mypy.readthedocs.io/en/latest/error_code_list.html#code-union-attr
            assert post.user
            post.user = await self.user_repository.get_by_id(post.user.user_id)

        return posts

    async def update_post(self, post_id: int, title: str, user_id: int) -> Post:
        if not (post := await self.post_repository.get_by_id(post_id)):
            raise Exception("Post not found")

        # AuthZ
        # https://mypy.readthedocs.io/en/latest/error_code_list.html#code-union-attr
        assert post.user
        if post.user.user_id != user_id:
            raise Exception("User not authorized")

        # https://mypy.readthedocs.io/en/latest/error_code_list.html#code-union-attr
        assert post.user
        if not (user := await self.user_repository.get_by_id(post.user.user_id)):
            raise Exception("User not found")

        post.title = title
        post = await self.post_repository.update(post)
        post.user = user
        return post

    async def delete_post(self, post_id: int) -> None:
        await self.post_repository.delete(post_id)

```

#### TODO: CQRS :confused:

### Infra

#### Repostiroies

The application does not care about how data is persisted in what kind format, as long as adapter returns a domain model that fits in the application layer. **Infra repositories implements interfaces defined in domain.**

```bash
➜  Fastapi git:(dev) ✗ tree
.
├── Makefile
├── app
│   ├── __init__.py
│   ├── application
│   │   ├── __init__.py
│   │   └── post_service.py
│   ├── config
│   │   ├── config.py
│   │   └── default
│   │       ├── default.toml
│   │       └── default.yaml
│   ├── domain
│   │   ├── __init__.py
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── post.py
│   │   │   └── user.py
│   │   └── repositories
│   │       ├── __init__.py
│   │       ├── post.py
│   │       └── user.py
│   ├── entrypoint
│   │   ├── __init__.py
│   │   └── fastapi
│   │       ├── __init__.py
│   │       ├── __main__.py
│   │       ├── factory.py
│   │       ├── routers
│   │       │   ├── __init__.py
│   │       │   ├── heatbeat.py
│   │       │   └── posts.py
│   │       └── schema
│   │           ├── __init__.py
│   │           ├── post.py
│   │           └── user.py
│   └── infra
│       ├── __init__.py
│       ├── persistence
│       │   ├── __init__.py
│       │   └── mem_db
│       │       ├── __init__.py
│       │       └── fake_database.py
│       └── repositories # 👈
│           ├── __init__.py
│           ├── post
│           │   ├── MemoryPostRepository.py
│           │   └── __init__.py
│           └── user
│               ├── MemoryUserRepository.py
│               └── __init__.py
├── docker
│   ├── Dockerfile
│   └── docker-compose.yml
├── note.md
└── requirements.txt
```

```bash
# ./app/infra/repositories/post/MemoryPostRepository.py

from app.infra.persistence.mem_db.fake_database import FakeDatabase
from app.domain.repositories import PostRepository
from app.domain.models.post import Post
from app.domain.models.user import User


# subclassing PostRepository
class MeoryPostRepository(PostRepository):
    def __init__(self, database: FakeDatabase) -> None:
        self.database = database

    async def create(self, post: Post) -> Post:
        # serialize (from domain model to dict)
        post_data = self._serialize(post)
        # persist
        self.database.posts[post_data["post_id"]] = post_data
        # update id and return
        post.post_id = post_data["post_id"]
        return post

    async def get_by_id(self, post_id: int) -> Post | None:
        if not (post_data := self.database.posts.get(post_id)):
            return None

        # deserialize (from dict to domain model) and return
        return self._build_post_model(post_data)

    async def get_posts(self) -> list[Post]:
        # iter + deserialize (from dict to domain model) and return
        return [self._build_post_model(post_data) for post_data in self.database.posts.values()]

    async def update(self, post: Post) -> Post:
        # return if nothing to update
        if not post.modified_fields:
            return post
        # otherwise partial update
        self.database.posts[post.post_id].update(
            self._serialize(post, partial=True))
        return post

    async def delete(self, post_id: int) -> None:
        try:
            self.database.posts.pop(post_id)
        except KeyError:
            return None

    def _serialize(self, post: Post, partial: bool = False) -> dict:
        # https://mypy.readthedocs.io/en/latest/error_code_list.html#code-union-attr
        assert post.user
        if not partial:
            return {
                "post_id": post.post_id or self._generate_id(),
                "title": post.title,
                "created": post.created,
                "update": post.update,
                "user_id": post.user.user_id,
            }
        else:
            data = {}
            modified_fields = post.modified_fields
            for field in modified_fields:
                match field:
                    case "title":
                        data["title"] = post.title
                    case _:
                        ...

            return data

    def _generate_id(self) -> int:
        return len(self.database.posts) + 1

    def _build_post_model(self, post_data: dict) -> Post:
        return Post(
            post_id=post_data["post_id"],
            title=post_data["title"],
            created=post_data["created"],
            update=post_data["update"],
            user=User(
                user_id=post_data["user_id"],
            )
        )
```

```python
# ./app/infra/repositories/post/MemoryUserRepository.py

from app.infra.persistence.mem_db.fake_database import FakeDatabase
from app.domain.repositories import UserRepository
from app.domain.models.user import User


# subclassing UserRepository
class MemoryUserRepository(UserRepository):
    def __init__(self, database: FakeDatabase):
        self.database = database

    async def get_by_id(self, user_id: int) -> User | None:
        # get user from db
        if not (user_data := self.database.users.get(user_id)):
            return None

        # deserialize user (to domain model)
        return self._to_user_model(user_data)

    def _to_user_model(self, user_data: dict) -> User:
        return User(**user_data)
```

### DIC

Dependency Injection Container for orchestration (groups services) as **Inbound Adatpter**.

```python
# ./app/application/dic.py

from dataclasses import dataclass
from app.application.post_service import PostService

# expose
__all__ = ("DIC", )


@dataclass(kw_only=True)
class DependencyInjectionContainer:
    post_service: PostService | None = None

DIC = DependencyInjectionContainer()
```

Startup in `__init__.py`. Injection flow: Databse 👉 Repositories 👉 Service.

```python
# ./app/application/__init__.py

from app.application.dic import DIC
from app.infra.repositories import MemoryUserRepository, MeoryPostRepository
from app.infra.persistence.mem_db.fake_database import fake_database
from app.application.post_service import PostService


async def application_startup():
    user_repository = MemoryUserRepository(database=fake_database)
    post_repository = MeoryPostRepository(database=fake_database)

    DIC.post_service = PostService(
        post_repository=post_repository,
        user_repository=user_repository,
    )
```

++ to application lifespan.

```python
# ./app/entrypoint/fastapi/factory.py

...

from app.application import application_startup

...

def create_app() -> FastAPI:

    async def on_startup(app: FastAPI) -> None:
        print("Starting up")
        await application_startup()
        
    ...
```

#### Exception

Inbound adapter is responsible for capturing domain exceptions raised from application services.

Base domain exception.

```python
# ./app/domain/exceptions.py
from typing import ParamSpec

P = ParamSpec("P")


class DomainException(Exception):

    TYPE = "internal_server_error"
    MESSAGE = "Internal Server Error"

    def __init__(self, message: str | None = None, *args: P.args, **kwargs: P.kwargs):
        self._message = message
        self._kwargs = kwargs
        super().__init__(message)

    @property
    def message(self) -> str:
        return self._message or self.MESSAGE.format(**self._kwargs)

    def __str__(self):
        return self.message
    
    
class InvalidFieldValue(DomainException):
    TYPE = "invalid_field_value"
    MESSAGE = "Invalid value {field_value} for field {field_name}"
    
    
class UserNotFound(DomainException):
    TYPE = "user_not_found"
    MESSAGE = "User {user_id} not found"


class PostNotFound(DomainException):
    TYPE = "post_not_found"
    MESSAGE = "Post {post_id} not found"
    
    
class Forbiden(DomainException):
    TYPE = "forbidden"
    MESSAGE = "Access Forbidden"
```

Update the exception in domain model.

```python
# ./app/domain/models/post.py

...
from app.domain.exceptions import InvalidFieldValue


@dataclass(kw_only=True)
class Post(BaseModel):
    ...

    @staticmethod
    def validate_title(title: str) -> str:
        if len(title.strip()) == 0:
            raise InvalidFieldValue(field_name="title", field_value=title)
        return title.strip()
```

```python
# ./app/domain/models/user.py

...
from app.domain.exceptions import InvalidFieldValue


@dataclass(kw_only=True)
class User(BaseModel):
    ...

    @staticmethod
    def validate_email(email: str) -> str:
        if not None and not EMAIL_REGEX.match(email):
            raise InvalidFieldValue(field_name="email", field_value=email)
        return email
```

Update the exceptions in application service.

```python
# ./app/application/post_service.py

...

from app.domain.exceptions import UserNotFound, PageNotFound, Forbiden

class PostService:
    ...

    async def create_post(self, user_id: int, title: str) -> Post:
        if not (user := await self.user_repository.get_by_id(user_id)):
            raise UserNotFound(user_id=user_id)
    
    ...
```

Expose API by injecting DIC in FastAPI router. Injection flow: Databse 👉 Repositories 👉 Service 👉 API Router.

Capture domain exceptions in FastAPI router.

```python
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
# from app.infra.persistence.mem_db.fake_database import fake_database
from app.entrypoint.fastapi.schema.post import Post, PostCreateInput, PostUpdateInput
from app.entrypoint.fastapi.schema.user import User
from starlette.exceptions import HTTPException
from app.application.dic import DIC
from app.domain.models.post import Post as PostModel
from app.domain.models.user import User as UserModel
from app.domain.exceptions import UserNotFound, PostNotFound, InvalidFieldValue, Forbiden

# expose
__all__ = ("router", )

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)


@router.get(
    "",
    description="Get all posts",
    response_model=list[Post],
    status_code=status.HTTP_200_OK,
)
async def list_posts() -> list[Post]:
    assert DIC.post_service
    posts: list[PostModel] = await DIC.post_service.list_posts()
    return [to_post_view_model(post) for post in posts]


@router.get(
    "/{post_id}",
    description="Get a post",
    response_model=Post,
    status_code=status.HTTP_200_OK,
)
async def get_post(post_id: int) -> Post:
    try:
        assert DIC.post_service
        post: PostModel = await DIC.post_service.get_post(post_id)
        return to_post_view_model(post)
    except (PostNotFound, UserNotFound) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )


@router.post(
    "",
    description="Create a post",
    response_model=Post,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(input_post: PostCreateInput) -> Post:
    try:
        assert DIC.post_service
        post: PostModel = await DIC.post_service.create_post(
            user_id=input_post.user_id,
            title=input_post.title
        )
        return to_post_view_model(post)
    except (UserNotFound, InvalidFieldValue) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )


@router.patch(
    "/{post_id}",
    description="Update a post",
    response_model=Post,
    status_code=status.HTTP_200_OK,
)
async def update_post(post_id: int, update_post: PostUpdateInput) -> Post:
    try:
        assert DIC.post_service
        post: PostModel = await DIC.post_service.update_post(
            post_id=post_id,
            title=update_post.title,
            user_id=update_post.user_id
        )
        return to_post_view_model(post)
    except Forbiden as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except (PostNotFound, UserNotFound) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )


@router.delete(
    "/{post_id}",
    description="Delete a post",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(post_id: int) -> None:
    assert DIC.post_service
    await DIC.post_service.delete_post(post_id)


def to_post_view_model(post: PostModel) -> Post:
    assert post.user
    return Post(
        post_id=post.post_id,
        title=post.title,
        created=post.created,
        user=to_user_view_model(post.user)
    )


def to_user_view_model(user: UserModel) -> User:
    return User(
        user_id=user.user_id,
        email=user.email,
        created=user.created
    )

```

### MySQL

```bash
.
├── Makefile
...
├── docker
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── mysql # 👈
│   │   ├── Dockerfile
│   │   └── fixtures
│   │       └── schema.sql
│   └── postgres
...
```

```dockerfile
# ./docker/mysql/Dockerfile

FROM mysql:9.2.0

ENV MYSQL_HOST mysql
ENV MYSQL_USER test
ENV MYSQL_PASSWORD test
ENV MYSQL_ROOT_PASSWORD root
ENV MYSQL_DATABASE fastapi
```

```sql
# ./docker/mysql/fixtures/schema.sql
CREATE DATABASE IF NOT EXISTS fastapi;

USE fastapi;

CREATE TABLE IF NOT EXISTS posts (
    -- Auto-incrementing primary key
    post_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    
    -- Foreign key to users table
    user_id INT UNSIGNED NOT NULL,
    
    -- Post title
    title VARCHAR(254) NOT NULL,
    
    -- Timestamps
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,                              -- Set when record is created
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,  -- Auto-updates when record changes
    
    -- Indexes
    PRIMARY KEY (post_id),    -- Primary key for fast lookups
    KEY (user_id)             -- Index on user_id for faster joins/lookups
) 
ENGINE=InnoDB                 -- Transactional storage engine
DEFAULT CHARSET=utf8mb4       -- Unicode character set
AUTO_INCREMENT=1;             -- Start auto-increment from 1

-- Samples

INSERT IGNORE INTO posts (post_id, user_id, title) 
VALUES 
(1, 5, "Post 1"),
(3, 3, "Post 2"),
(4, 2, "Post 3"),
(2, 4, "Post 4"),
(5, 1, "Post 5");
```

```yaml
# ./docker/docker-compose.yml

services:
  # service name
  app:
    ...
    
    # depends on mysql
    depends_on:
      mysql:
        condition: service_healthy

  mysql:
    build:
      context: ./..
      dockerfile: ./docker/mysql/Dockerfile
    # MySQL automatically executes all .sql files in this directory during initialization
    volumes:
      - ./../docker/mysql/fixtures:/docker-entrypoint-initdb.d
    healthcheck:
      # `SELECT 1` is a simple query to verify database is responsive
      # mysql -utest -ptest fastapi -e 'select 1'
      # mysql -utest -ptest fastapi -e 'show tables'
      test: "mysql -u$${MYSQL_USER} -p$${MYSQL_PASSWORD} $${MYSQL_DATABASE} -e 'SELECT 1'"
      interval: 2s
      timeout: 15s
      retries: 15
    networks:
      - fastapi-network
      
...
```

Add mysql config into app config. 

```yml
# ./app/config/default/default.toml

...

# TODO: expose in a secure way
[databases.mysql]
host = "mysql"
port = 3306
user = "test"
password = "test"
dbname = "fastapi"
```

++ `aiomysql` dep.

```bash
# ./requirements.txt

...

aiomysql==0.2.0
```



### Postgres (TODO)

### SQLite (TODO)

## Git :package:

1. First, create your initial commit if you haven't already:
```bash
git add .
git commit -m "Initial commit"
```

2. Create and switch to the main branch:
```bash
git branch -M main
```

3. Now you can create your development branch:
```bash
git checkout -b dev
```

If you're connecting to a remote repository, you can then:

```bash
git push -u origin main
```

5. Switch and continue to farm on dev branch:

```bash
git add .
git commit -m "your commit message"
```

6. To merge to main:

```bash
git checkout main
git merge dev
git push origin main
```

7. Back to dev:

```bash
git checkout dev
```

If you need to update remote dev branch:

```bash
git push origin dev
```
