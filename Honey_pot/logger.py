import json
from datetime import datetime


def generate_event(
    category,
    event_type,
    session_id=None,
    source_ip=None,
    username=None,
    password=None,
    command=None,
    working_directory=None,
    message=None,
    severity="INFO",
    source="honeypot"
):

    event = {
        
        
        "severity": severity,
        
        "source": source,

        "timestamp": datetime.now().isoformat(),

        "category": category,

        "event_type": event_type,

        "session_id": session_id,

        "source_ip": source_ip,

        "username": username,

        "password": password,

        "command": command,

        "working_directory": working_directory,

        "message": message,
        
   
    }

    return event
# Print the event in JSON format for AWS CloudWatch Logs
def print_event(event):
  
    print(
        json.dumps(event)
    )