import os
import warnings
from dotenv import load_dotenv
from state import AgentState
from graph import agent_step

# Suppress SSL warnings from gRPC
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'
warnings.filterwarnings('ignore', category=UserWarning)

# Load environment variables from .env file (override system env vars)
load_dotenv(override=True)

state = AgentState()

print("AutoStream Agent (CLI Mode). Type exit to quit.")

while True:
    user = input("User: ")
    if user.lower() == "exit":
        break

    reply = agent_step(state, user)
    print("Agent:", reply)
