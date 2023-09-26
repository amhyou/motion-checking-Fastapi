from pydantic import BaseModel, Field
from uuid import uuid4
from utils import current_time
from aioredis import Redis

class SaasModel(BaseModel):
    id: str = Field(default_factory=lambda:str(uuid4()))
    created: str = Field(default_factory=current_time)
    updated: str = Field(default_factory=current_time)

    @classmethod
    async def fetch(cls, redis_db: Redis, id: str):
        value = await redis_db.get(id)
        if value:
            return cls.model_validate_json(value)
        else: 
            raise Exception(f"key not found <{id}>")
    
    async def save(self, redis_db: Redis, key: str = None):
        await redis_db.set(key if key else self.id, self.model_dump_json())
    

class Account(SaasModel):
    email: str
    password: str
    current_task_id: str | None = None


class Piece(SaasModel):
    item: str
    info: str
    valid: bool = False


class Task(SaasModel):
    data: str
    processed: list[ Piece ] = []
    skipped: list[ Piece ] = []
    progression: int = 0
    paused: bool = True
    finished: bool = False