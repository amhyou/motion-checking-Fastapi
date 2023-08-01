from aioredis import Redis
from models import Task, Piece
import asyncio
from random import choice

async def AutomateChecking( task: Task, redis_db: Redis ) -> list[ Piece ]:
    pieces = []
    extracted = task.data.strip().split("\n")
    for i,line in enumerate(extracted):
        print("background : "+line)
        piece = Piece(item=line, info="infoinfo", valid=choice([False, True]))
        pieces.append( piece )
        #redis_db.set(line, piece.model_dump_json() )
        await redis_db.publish(task.task_id, piece.model_dump_json())
        task.extracted.append(piece)
        task.processed.append(piece)
        if i == len(extracted) - 1:break
        await redis_db.set(task.task_id, task.model_dump_json())
        await asyncio.sleep(10)
    
    task.finished = True
    await redis_db.set(task.task_id, task.model_dump_json())

    
    return pieces