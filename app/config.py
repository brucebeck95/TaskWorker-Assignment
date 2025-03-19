import os
from fastapi.security import OAuth2PasswordBearer
import logging

import logging
import sys
from fastapi.logger import logger

gunicorn_logger = logging.getLogger("uvicorn")
logger.handlers = gunicorn_logger.handlers
logger.setLevel(logging.INFO)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)

logger.addHandler(stdout_handler)

TASK_FREQUENCY_IN_SECONDS = int(os.getenv("TASK_FREQUENCY_IN_SECONDS", "60"))


# This is only because there is no proper OAuth client.
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_secret_key")
OAUTH2_SCHEMA = OAuth2PasswordBearer(tokenUrl="token")
