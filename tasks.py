from aioredis import Redis
from models import Task, Piece, Account
import asyncio
from random import choice
from math import ceil

async def AutomateChecking( task: Task, redis_db: Redis ) -> list[ Piece ]:
    already = set([ piece.item for piece in task.processed + task.skipped ])
    pieces = []
    extracted = task.data.strip().split("\n")
    for i,line in enumerate(extracted):
        # if line in already: continue   for mvp
        print("background : "+line)
        print(i, len(extracted))
        progression = int( ( i / len(extracted) ) * 100 )
        piece = Piece(item=line, info="infoinfo", progression=progression,  valid=choice([False, True]))
        pieces.append( piece )
        await redis_db.publish(task.id, piece.model_dump_json())
        task.processed.append(piece)
        task.progression = progression
        already.add(line)
        if i == len(extracted) - 1:break
        await task.save(redis_db)
        await asyncio.sleep(5)
    
    task.finished = True
    await task.save(redis_db)
    await redis_db.publish(task.id, b'{"finished": true}')

    try:
        account: Account = await Account.fetch(redis_db, "current_account")
        account.current_task_id = None
        await account.save(redis_db, "current_account")
    except Exception as ex:
        print(ex)
    
    return pieces