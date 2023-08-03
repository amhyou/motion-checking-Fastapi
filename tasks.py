from aioredis import Redis
from models import Task, Piece
import asyncio
from random import choice

async def AutomateChecking( task: Task, redis_db: Redis ) -> list[ Piece ]:
    already = set([ piece.item for piece in task.processed + task.skipped ])
    pieces = []
    extracted = task.data.strip().split("\n")
    for i,line in enumerate(extracted):
        if line in already: continue
        print("background : "+line)
        piece = Piece(item=line, info="infoinfo", valid=choice([False, True]))
        pieces.append( piece )
        await redis_db.publish(task.id, piece.model_dump_json())
        task.processed.append(piece)
        already.add(line)
        if i == len(extracted) - 1:break
        await task.save(redis_db)
        await asyncio.sleep(5)
    
    task.finished = True
    await task.save(redis_db)
    await redis_db.publish(task.id, b'{"finished": true}')
    
    return pieces