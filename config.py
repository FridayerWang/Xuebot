import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

# OpenAI API Configuration
# You should set your API key through environment variables or update it here
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# LLM Configuration
LLM_TEMPERATURE = 0.0  # Higher values make the output more random
LLM_MODEL = "gpt-3.5-turbo"  # Model to use

# Agent Configuration
DEFAULT_DIFFICULTY_LEVELS = ["easy", "medium", "hard"]
DEFAULT_KNOWLEDGE_LEVELS = ["beginner", "intermediate", "advanced"]

# Maximum questions to generate or retrieve
MAX_QUESTIONS = 3

# Vector Store Configuration
USE_VECTOR_STORE = os.environ.get("USE_VECTOR_STORE", "true").lower() == "true"
VECTOR_STORE_DIR = os.environ.get("VECTOR_STORE_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db"))
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")  # HuggingFace embedding model to use

# Logging Configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")  # DEBUG, INFO, WARNING, ERROR, CRITICAL
CONSOLE_LOG_LEVEL = os.environ.get("CONSOLE_LOG_LEVEL", "INFO")
FILE_LOG_LEVEL = os.environ.get("FILE_LOG_LEVEL", "DEBUG")
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
LOG_DIR = "logs" 