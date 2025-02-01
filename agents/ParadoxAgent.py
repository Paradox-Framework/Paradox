from paradox.agent import ParadoxAgent
import requests
class ParadoxAgent:
    def __init__(self):
        self.admin_id = None
        self.trading_personality = "conservative"
        self.auto_post_enabled = False

    def set_admin(self, admin_id):
        self.admin_id = admin_id
        return f"Admin set to {admin_id}"

    def set_personality(self, personality):
        allowed_personalities = ["aggressive", "conservative", "scalper", "meme-trader"]
        if personality not in allowed_personalities:
            return "Invalid personality type."
        self.trading_personality = personality
        return f"Trading personality set to {personality}"

    def deploy(self):
        if not self.admin_id:
            return "Error: Admin must be set before deploying the agent."
        return "Agent successfully deployed and ready for trading, tracking, and analysis."

    def shutdown(self):
        return "Agent has been shut down."


class ParadoxAnalysis:
    def __init__(self, solscan_api_key):
        self.base_url = "https://pro-api.solscan.io/v2.0"
        self.headers = {"token": solscan_api_key}

    def get_tokenomics(self, token_address):
        url = f"{self.base_url}/account/detail"
        params = {"address": token_address}
        response = requests.get(url, headers=self.headers, params=params)
        data = response.json()
        return {
            "volume": data.get("volume"),
            "market_cap": data.get("market_cap"),
            "top_holders": data.get("holders"),
            "recent_trends": data.get("trends"),
        }

    def get_top_coins(self):
        url = f"{self.base_url}/account/token-accounts"
        params = {"type": "token", "page": 1, "page_size": 10}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()


class ParadoxWalletTracking:
    def __init__(self, solscan_api_key):
        self.base_url = "https://pro-api.solscan.io/v2.0"
        self.headers = {"token": solscan_api_key}

    def track_wallet(self, wallet_address):
        url = f"{self.base_url}/account/transfer"
        params = {
            "address": wallet_address,
            "page": 1,
            "page_size": 10,
            "sort_by": "block_time",
            "sort_order": "desc"
        }
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_wallet_activity(self, wallet_address):
        url = f"{self.base_url}/account/defi/activities"
        params = {
            "address": wallet_address,
            "page": 1,
            "page_size": 10,
            "sort_by": "block_time",
            "sort_order": "desc"
        }
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

class ParadoxTrading:
    def __init__(self, defi_api, personality="conservative"):
        self.defi_api = defi_api
        self.personality = personality

    def execute_trade(self, from_token, to_token, amount):
        slippage = {
            "aggressive": 0.05,
            "conservative": 0.01,
            "scalper": 0.02,
            "meme-trader": 0.03
        }.get(self.personality, 0.01)
        return self.defi_api.trade(from_token, to_token, amount, slippage)

    def adjust_trading_strategy(self, personality):
        self.personality = personality
        return f"Trading strategy updated to {personality}"


class ParadoxPosting:
    def __init__(self, platform_api, auto_post=False):
        self.platform_api = platform_api
        self.auto_post = auto_post
        self.post_channel = None

    def set_post_channel(self, channel_id):
        self.post_channel = channel_id
        return f"Post channel set to {channel_id}"

    def send_post(self, message):
        if not self.post_channel:
            return "Error: No post channel has been set."
        return self.platform_api.post_message(self.post_channel, message)

    def toggle_auto_post(self, status):
        self.auto_post = status
        return f"Auto-posting {'enabled' if status else 'disabled'}"


def initialize_agent():
    return ParadoxAgent()


def initialize_analysis(solscan_api):
    return ParadoxAnalysis(solscan_api)


def initialize_wallet_tracking(solscan_api):
    return ParadoxWalletTracking(solscan_api)


def initialize_trading(defi_api, personality="conservative"):
    return ParadoxTrading(defi_api, personality)


def initialize_posting(platform_api, auto_post=False):
    return ParadoxPosting(platform_api, auto_post)


def deploy_paradox_agent():
    agent = initialize_agent()
    tokenomics = initialize_analysis(solscan_api)
    wallet_tracker = initialize_wallet_tracking(solscan_api)
    trading_engine = initialize_trading(defi_api)
    posting_system = initialize_posting(platform_api)

    agent.deploy()

    return {
        "agent_status": "Deployed",
        "tokenomics_status": tokenomics.get_top_coins("7d"),
        "wallet_tracking_status": "Active",
        "trading_status": "Ready",
        "posting_status": "Configured"
    }
