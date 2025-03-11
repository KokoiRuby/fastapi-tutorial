import aiomysql  # type: ignore


# explose
__all__ = ('Database', )


class Database:

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        dbname: str,
        autocommit: bool = True,
        port: int = 3306,
        pool_minsize=1,
        pool_maxsize=10,
        pool_recycle=60,
        charset='utf-8',
        wait_timeout=30,
    ):
        self._host = host
        self._user = user
        self._password = password
        self._dbname = dbname
        self._autocommit = autocommit
        self._port = port
        self._pool_minsize = pool_minsize
        self._pool_maxsize = pool_maxsize
        self._pool_recycle = pool_recycle
        self._charset = charset
        self._wait_timeout = wait_timeout
        self.pool = None

    async def connect(self):
        self.pool = await aiomysql.create_pool(
            host=self._host,
            user=self._user,
            password=self._password,
            db=self._dbname,
            autocommit=self._autocommit,
            port=self._port,
            minsize=self._pool_minsize,
            maxsize=self._pool_maxsize,
            pool_recycle=self._pool_recycle,
            cursorclass=aiomysql.DictCursor,  # returns rows as dict
            init_command=f"SET wait_timeout={self._wait_timeout}",
        )

    async def check_connection(self):
        async with self.pool.acquire() as conn:
            await conn.ping(reconnect=True)  # reconnect if no pong back

    async def init_connection(self):
        try:
            await self.connect()
            await self.check_connection()
        except Exception:
            raise

    async def close(self):
        if self.pool:
            self.pool.terminate()
            await self.pool.wait_closed()
            self.pool = None
