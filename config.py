import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = "sentence-transformers/distiluse-base-multilingual-cased"
FAISS_INDEX_PATH = "template_index.faiss"
TEMPLATE_DATA_PATH = "template_data.json"