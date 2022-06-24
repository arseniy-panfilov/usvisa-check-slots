import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

ACCOUNT_ID = os.getenv('ACCOUNT_ID')
COOKIE_PATH = os.path.join(os.getcwd(), os.getenv('USVISA_COOKIE_PATH'))
USER = os.getenv('USVISA_USER', default='')
PASSWORD = os.getenv('USVISA_PASSWORD', default='')
TARGET_DATE = datetime.strptime(os.getenv('USVISA_CURRENT_DATE'), '%Y-%m-%d').date()
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
AUTO_REFRESH_AUTH = int(os.getenv("AUTO_REFRESH_AUTH", default="0"))

SESSION_COOKIE = '_yatri_session'
