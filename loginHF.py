from huggingface_hub import login
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Login using token from environment variable
login(token=os.getenv("HUGGINGFACE_TOKEN"))