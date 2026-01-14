import os
import warnings
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

# Suppress SSL warnings from gRPC (these are often false positives on macOS)
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'
warnings.filterwarnings('ignore', category=UserWarning)

# Load environment variables from .env file (override system env vars)
# Get the project root directory (parent of 'agent' folder)
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# Get API key from environment
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY must be set in .env file or environment")

# Configure genai to use REST transport instead of gRPC to avoid SSL certificate issues
genai.configure(api_key=api_key, transport="rest")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    api_key=api_key,
    transport="rest"
)

def detect_intent(message: str) -> str:
    prompt = (
        "You are an intent classification engine for AutoStream, a video editing SaaS product.\n"
        "Classify the user message into exactly ONE intent from this list:\n"
        "- greeting: Casual greetings like 'hi', 'hello', 'hey'\n"
        "- product_inquiry: Questions about pricing, features, plans, refunds, support, or general product information\n"
        "- high_intent: Expressions of strong interest in signing up, purchasing, or getting started, such as 'I want to sign up', 'I'm interested', 'let me try', 'I'd like to buy', 'sign me up'\n\n"
        "User message: {message}\n\n"
        "Respond with ONLY the intent word (greeting, product_inquiry, or high_intent)."
    ).format(message=message)

    response = llm.invoke(prompt)
    intent = response.content.strip().lower()

    # Clean up the response in case LLM adds extra text
    if "greeting" in intent:
        intent = "greeting"
    elif "high_intent" in intent or "high" in intent:
        intent = "high_intent"
    elif "product" in intent or "inquiry" in intent:
        intent = "product_inquiry"
    else:
        # Default to product_inquiry for unclear intents
        intent = "product_inquiry"

    return intent
