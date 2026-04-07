import os
from dotenv import load_dotenv

load_dotenv()

class Config:       
    # # POSTGRES (LOCAL)
    DATABASE_URL = os.environ.get("DATABASE_URL")
    
    # NALA API
    NALA_API_KEY = os.environ.get("NALA_API_KEY")
    NALA_BASE_URL = os.environ.get("NALA_BASE_URL")

