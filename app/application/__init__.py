from app.application.dic import DIC
from app.infra.repositories import MemoryUserRepository, MeoryPostRepository, MySQLPostRepository
from app.infra.persistence.mem_db.fake_database import fake_database
from app.infra.persistence.mysql.database import Database
from app.application.post_service import PostService
from app.config.config import config


async def application_startup():
    # load conf and init db
    my_sql_conf = config["databases"]["mysql"]
    mysql_db = Database(
        host=my_sql_conf["host"],
        port=my_sql_conf["port"],
        user=my_sql_conf["user"],
        password=my_sql_conf["password"],
        dbname=my_sql_conf["dbname"],
    )
    await mysql_db.init_connection()

    # mem db
    user_repository = MemoryUserRepository(database=fake_database)
    # post_repository = MeoryPostRepository(database=fake_database)
    post_repository = MySQLPostRepository(database=mysql_db)

    DIC.post_service = PostService(
        post_repository=post_repository,
        user_repository=user_repository,
    )

    DIC.mysql_db = mysql_db


async def application_shutdown():
    if DIC.mysql_db:
        await DIC.mysql_db.close()


async def application_health_check():
    await DIC.mysql_db.check_connection()
