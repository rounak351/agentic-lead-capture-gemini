
import json
from datetime import datetime
from pathlib import Path

def mock_lead_capture(name, email, platform):
    # Print to stdout so it is clearly visible in logs / demo recordings
    print(f"Lead captured successfully: {name}, {email}, {platform}")

    # Create lead data structure
    lead_data = {
        "name": name,
        "email": email,
        "platform": platform,
        "timestamp": datetime.now().isoformat(),
        "status": "Lead captured successfully"
    }
    
    # Save to leads file
    project_root = Path(__file__).parent.parent
    leads_file = project_root / "data" / "leads.json"
    
    # Ensure data directory exists
    leads_file.parent.mkdir(exist_ok=True)
    
    # Load existing leads or create new list
    if leads_file.exists():
        try:
            with open(leads_file, 'r') as f:
                leads = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            leads = []
    else:
        leads = []
    
    # Append new lead
    leads.append(lead_data)
    
    # Save back to file
    with open(leads_file, 'w') as f:
        json.dump(leads, f, indent=2)
    
    print(f"Lead saved to {leads_file}")

    # Also return a structured payload for programmatic use
    return {
        "name": name,
        "email": email,
        "platform": platform,
        "status": "Lead captured successfully"
    }
