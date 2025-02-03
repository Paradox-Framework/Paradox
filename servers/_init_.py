import argparse
from framework.cli import ParadoxCLI

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Paradox - Blockchain AI Agent Framework')
    parser.add_argument('--server', action='store_true', help='Run in server mode')
    parser.add_argument('--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000, help='Server port (default: 8000)')
    args = parser.parse_args()

    if args.server:
        try:
            from framework.server import start_server
            start_server(host=args.host, port=args.port)
        except ImportError:
            print("Server dependencies not installed. Run: pip install -r requirements.txt")
            exit(1)
    else:
        cli = ParadoxCLI()
        cli.main_loop()
