from paradox.agent import ParadoxAgent
from paradox.analysis import initialize_analysis
from paradox.wallet_tracking import initialize_wallet_tracking
from paradox.trading import initialize_trading
from paradox.posting import initialize_posting

def deploy_paradox_agent():
    agent = ParadoxAgent()
    tokenomics = initialize_analysis()
    wallet_tracker = initialize_wallet_tracking()
    trading_engine = initialize_trading()
    posting_system = initialize_posting()

    agent.set_admin("YOUR_ADMIN_ID")
    agent.set_personality("conservative")
    agent.deploy()

    return {
        "agent_status": "Deployed",
        "tokenomics_status": tokenomics.get_top_coins("7d"),
        "wallet_tracking_status": "Active",
        "trading_status": "Ready",
        "posting_status": "Configured"
    }

if __name__ == "__main__":
    deploy_paradox_agent()
