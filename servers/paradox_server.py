import uvicorn
from .paradox_app import create_app

def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the Paradox server"""
    app = create_app()
    uvicorn.run(app, host=host, port=port)
