from pydantic import BaseModel, Field
from uuid import uuid4
from utils import current_time

class SaasModel(BaseModel):
    created: str = Field(default_factory=current_time)
    updated: str = Field(default_factory=current_time)


class Account(SaasModel):
    email: str
    password: str
    current_task_id: str = None

class Piece(SaasModel):
    item: str
    info: str
    valid: bool = False


class Task(SaasModel):
    task_id: str = Field(default_factory=lambda:str(uuid4()))
    data: str
    extracted: list[ Piece ] = []
    processed: list[ Piece ] = []
    finished: bool = False