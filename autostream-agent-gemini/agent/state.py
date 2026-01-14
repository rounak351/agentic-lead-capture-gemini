
from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class AgentState:
    intent: str = None
    name: str = None
    email: str = None
    platform: str = None
    lead_captured: bool = False
    conversation_history: List[Tuple[str, str]] = field(default_factory=list)  
