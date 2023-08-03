from fastapi import FastAPI, Depends, WebSocket, BackgroundTasks
import uvicorn, json, subprocess, asyncio
from fastapi.middleware.cors import CORSMiddleware
from aioredis import Redis, from_url
from config import settings
from tasks import AutomateChecking
from schemas import TaskInput, TaskOutput, AccountInput, AccountOutput
from models import Task, Account

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    app.state.redis_db = from_url(settings.redis_url)

def get_redis_db() -> Redis:
    return app.state.redis_db


# account management

@app.post("/check_account")
async def check_account(redis_db: Redis = Depends(get_redis_db)) -> AccountOutput:
    try:
        current_account: Account = await Account.fetch(redis_db, "current_account")
        return AccountOutput(email=current_account.email, task_id=current_account.current_task_id)
    except Exception as e:
        print(e)
        return AccountOutput


@app.post("/register_account")
async def register_account(account: AccountInput, redis_db: Redis = Depends(get_redis_db)) -> AccountOutput:
    cli_command = f'gmsaas auth login {account.email} {account.password}'
    try:
        result = subprocess.run(cli_command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
            current_account = Account(email=account.email, password=account.password)
            await current_account.save(redis_db, "current_account")
            # await redis_db.linsert("accounts", current_account.model_dump_json())  ## post mvp
            return AccountOutput(email=current_account.email)
        else:
            print(result.stderr)
            return AccountOutput
    except Exception as e:
        print(e)
        return AccountOutput

@app.post("/discard_account")
async def discard_account(redis_db: Redis = Depends(get_redis_db)) -> AccountOutput:
    try:
        result = await redis_db.delete("current_account")
        return AccountOutput
    except Exception as e:
        print(e)
        return AccountOutput


# data management

@app.post("/process_data")
async def set_redis_key(task: TaskInput, background_tasks: BackgroundTasks, redis_db: Redis = Depends(get_redis_db)):
    # verify all tasks have already finished
    """
    curr_task = await redis_db.get("current_task")
    if curr_task:
        curr_task = Task.model_validate_json(curr_task)
        if not curr_task.finished:
            raise Exception("already running task")
    """
    current_task = Task(data=task.data)
    await current_task.save(redis_db)
    await redis_db.lpush("tasks", current_task.id)
    await redis_db.set("current_task", current_task.model_dump_json())
    background_tasks.add_task(AutomateChecking, current_task, redis_db)
    return TaskOutput(task_id=current_task.id)


@app.post("/getall_data")
async def get_redis_key(redis_db: Redis = Depends(get_redis_db)) -> list[ Task ]:
    results = await redis_db.lrange("tasks", 0, -1)
    tasks = []
    for result in results:
        try:
            task: Task = await Task.fetch(redis_db, result)
        except Exception as ex:
            print(ex)
        tasks.append(task)
    return tasks



# task management

@app.websocket("/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str, redis_db: Redis = Depends(get_redis_db)):
    
    task: Task = await Task.fetch(redis_db, task_id)
    await websocket.accept()
    await websocket.send_json([ piece.model_dump() for piece in task.processed ])

    pubsub = redis_db.pubsub()
    await pubsub.subscribe(task_id)
    while True:
        message = await pubsub.get_message()
        if message and message.get("data") != 1:
            data = json.loads(message.get("data").decode('utf-8'))
            print(data)
            if data.get("finished", False): await websocket.close(); return
            await websocket.send_json(data)
        
        await asyncio.sleep(5)


@app.on_event("shutdown")
async def shutdown():
    await app.state.redis_db.close()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)