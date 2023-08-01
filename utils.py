from datetime import datetime

def current_time() -> str:
    return datetime.now().strftime("%d/%m/%Y|%H:%M")