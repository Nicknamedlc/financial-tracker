import http
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from loguru import logger

from app.models.schemas import Message
from app.routes import auth, tasks, users

app = FastAPI(title='CRUD TASK API')

if __name__ == '__main__':
    uvicorn.run(
        app,  # Your FastAPI app
        host='0.0.0.0',
        port=8000,
        log_config=None,
        log_level=None,
    )

# Remove existing handlers to loguru works
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)


class InterceptHandler(logging.Handler):
    @classmethod
    def emit(cls, record):
        """

        :param record:
        """
        # Get corresponding Loguru level
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller to get correct stack depth
        frame, depth = logging.currentframe(), 2
        while frame.f_back and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


# Intercept standard logging
logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)

loggers = (
    'uvicorn',
    'uvicorn.access',
    'uvicorn.error',
    'fastapi',
    'asyncio',
    'starlette',
)

for logger_name in loggers:
    logging_logger = logging.getLogger(logger_name)
    logging_logger.handlers = []
    logging_logger.propagate = True

logger.add(
    'logs/application.log',
    rotation='500 MB',
    compression='zip',
    level='INFO',
    backtrace=True,
    diagnose=True,
)


app.include_router(users.router)
app.include_router(auth.router)
app.include_router(tasks.router)


@app.get('/', status_code=http.HTTPStatus.OK, response_model=Message)
async def read_root():
    return {'message': 'Olá Mundo'}


@app.get('/olamundo/', response_class=HTMLResponse)
def say_hello():
    return """
    <html>
      <head>
        <title>Olá mundo!</title>
      </head>
      <body>
        <h1> Olá Mundo </h1>
        <h2> Hoje é um novo dia</h2>
      </body>
    </html>"""
