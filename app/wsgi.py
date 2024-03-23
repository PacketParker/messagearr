from hypercorn.config import Config
from hypercorn.asyncio import serve
from messagearr import app
import multiprocessing
import asyncio

from db_removal import sched
import initialize_variables
import validate_config
import db_setup

if __name__ == '__main__':
    initialize_variables.init()
    db_setup.setup_db()
    validate_config.make_config()
    multiprocessing.Process(target=sched.start()).start()
    print('Starting server...')
    config = Config()
    config.bind = ["0.0.0.0:4545"]
    asyncio.run(serve(app, config))