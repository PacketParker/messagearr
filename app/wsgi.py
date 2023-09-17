from hypercorn.config import Config
from hypercorn.asyncio import serve
from messagearr import app
import multiprocessing
import asyncio

from db_removal import sched

if __name__ == '__main__':
    multiprocessing.Process(target=sched.start()).start()
    print('Starting server...')
    config = Config()
    config.bind = ["0.0.0.0:4545"]
    asyncio.run(serve(app, config))