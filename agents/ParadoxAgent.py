from paradox.agent import ParadoxAgent
import requests import os import load_dotenv
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

load_dotenv()

class ParadoxAnalysis:
    def init(self):
        self.base_url = "https://pro-api.solscan.io/v2.0"
        self.api_key = os.getenv("SOLSCAN_API_KEY")
        self.headers = {"token": self.api_key}

    def get_tokenomics(self, token_address):
        url = f"{self.base_url}/token/meta"
        params = {"address": token_address}
        response = requests.get(url, headers=self.headers, params=params)
        data = response.json()
    return {
        "name": data.get("name"),
        "symbol": data.get("symbol"),
        "market_cap": data.get("market_cap"),
        "price": data.get("price"),
        "holders": data.get("holders"),
    }

def get_token_transfers(self, token_address):
    url = f"{self.base_url}/token/transfer"
    params = {"address": token_address, "page": 1, "page_size": 10, "sort_by": "block_time", "sort_order": "desc"}
    response = requests.get(url, headers=self.headers, params=params)
    data = response.json()
    return data.get("data", [])

def get_token_defi_activities(self, token_address):
    url = f"{self.base_url}/token/defi/activities"
    params = {"address": token_address, "page": 1, "page_size": 10, "sort_by": "block_time", "sort_order": "desc"}
    response = requests.get(url, headers=self.headers, params=params)
    data = response.json()
    return data.get("activities", [])

def get_trending_tokens(self):
    url = f"{self.base_url}/token/trending"
    params = {"limit": 10}
    response = requests.get(url, headers=self.headers, params=params)
    data = response.json()
    return data.get("data", [])

def get_token_price(self, token_address):
    url = f"{self.base_url}/token/price"
    params = {"address": token_address}
    response = requests.get(url, headers=self.headers, params=params)
    data = response.json()
    return data.get("price", "N/A")

def get_top_tokens(self):
    url = f"{self.base_url}/token/top"
    response = requests.get(url, headers=self.headers)
    data = response.json()
    return data.get("data", [])

class ParadoxWalletTracking:
    def init(self):
        self.base_url = "https://pro-api.solscan.io/v2.0"
        self.api_key = os.getenv("SOLSCAN_API_KEY")
        self.headers = {"token": self.api_key}
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

class ParadoxTransactions:
    def init(self):
        self.base_url = "https://pro-api.solscan.io/v2.0"
        self.api_key = os.getenv("SOLSCAN_API_KEY")
        self.headers = {"token": self.api_key}
        
    def get_latest_transactions(self, limit=10, filter_type="exceptVote"):
        url = f"{self.base_url}/transaction/last"
        params = {"limit": limit, "filter": filter_type}
        response = requests.get(url, headers=self.headers, params=params)
        data = response.json()
    return data.get("data", [])

    def get_transaction_detail(self, tx_address):
        url = f"{self.base_url}/transaction/detail"
        params = {"tx": tx_address}
        response = requests.get(url, headers=self.headers, params=params)
        data = response.json()
    return {
        "sol_changes": data.get("sol_changes"),
        "token_balances": data.get("token_balances"),
        "defi_activities": data.get("defi_activities"),
    }

    def get_transaction_actions(self, tx_address):
        url = f"{self.base_url}/transaction/actions"
        params = {"tx": tx_address}
        response = requests.get(url, headers=self.headers, params=params)
        data = response.json()
    return data.get("actions", [])

class ParadoxMarket:
    def init(self):
        self.base_url = "https://pro-api.solscan.io/v2.0"
        self.api_key = os.getenv("SOLSCAN_API_KEY")
        self.headers = {"token": self.api_key}
        
    def get_market_info(self, market_id):
        url = f"{self.base_url}/market/info"
        params = {"address": market_id}
        response = requests.get(url, headers=self.headers, params=params)
        data = response.json()
    return {
        "market_name": data.get("market_name"),
        "current_price": data.get("current_price"),
        "volume_24h": data.get("volume_24h"),
    }

    def get_market_volume(self, market_id, start_date=None, end_date=None):
        url = f"{self.base_url}/market/volume"
        params = {"address": market_id}
    if start_date and end_date:
            params["time[]"] = [start_date, end_date]
        response = requests.get(url, headers=self.headers, params=params)
        data = response.json()
    return data.get("volume_data", [])

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

class ParadoxAgent:
    def init(self):
    self.analysis = ParadoxAnalysis()
    self.wallet_tracking = ParadoxWalletTracking()
    self.transactions = ParadoxTransactions()
    self.market = ParadoxMarket()
    self.admin_id = None
    self.trading_personality = "conservative"
    self.auto_post_enabled = False



def initialize_agent():
    return ParadoxAgent()

def initialize_analysis():
    return ParadoxAnalysis()

def initialize_wallet_tracking():
    return ParadoxWalletTracking()

def initialize_trading(personality="conservative"):
    return ParadoxTrading(personality=personality)

def initialize_posting(auto_post=False):
    return ParadoxPosting(auto_post=auto_post)

def deploy_paradox_agent():
    agent = initialize_agent()
    analysis = initialize_analysis()
    wallet_tracker = initialize_wallet_tracking()
    trading_engine = initialize_trading()
    posting_system = initialize_posting()

    # Example of using the connected functions
    tokenomics_data = analysis.get_tokenomics("TOKEN_ADDRESS")
    wallet_data = wallet_tracker.track_wallet("WALLET_ADDRESS")
    trending_tokens = analysis.get_trending_tokens()

    print(f"Agent Status: {agent.deploy()}")
    print(f"Tokenomics: {tokenomics_data}")
    print(f"Wallet Data: {wallet_data}")
    print(f"Trending Tokens: {trending_tokens}")

