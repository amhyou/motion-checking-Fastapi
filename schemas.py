from pydantic import BaseModel, EmailStr

    
class AccountInput(BaseModel):
    email: EmailStr
    password: str

class AccountOutput(BaseModel):
    email: EmailStr = None
    task_id: str = None


class TaskInput(BaseModel):
    data: str

class TaskOutput(BaseModel):
    task_id: str = None