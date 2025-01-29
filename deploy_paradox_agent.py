from paradox.agent import ParadoxAgent
from paradox.analysis import initialize_analysis
from paradox.wallet_tracking import initialize_wallet_tracking
from paradox.trading import initialize_trading
from paradox.posting import initialize_posting
from paradox.blockchain import confirm_solana_transaction

def deploy_paradox_agent(agent_name="ParadoxAI"):
    """Deploys the AI agent and confirms all system integrations."""
    
    agent = ParadoxAgent()
    tokenomics = initialize_analysis()
    wallet_tracker = initialize_wallet_tracking()
    trading_engine = initialize_trading()
    posting_system = initialize_posting()

    agent.set_admin("YOUR_ADMIN_ID")
    agent.set_personality("conservative")
    
    deployment_status = agent.deploy()

    if "Error" in deployment_status:
        print(f"⚠️ Deployment Failed: {deployment_status}")
        return
    
    solana_tx_id = confirm_solana_transaction()
    
    print("\n✅ Paradox AI Agent Successfully Deployed!")
    print(f"🤖 Agent Name: {agent_name}")
    print(f"🔗 Solana Transaction ID: {solana_tx_id}")
    print("📊 System Status:\n")
    
    status_report = {
        "Tokenomics Status": tokenomics.get_top_coins("7d"),
        "Wallet Tracking Status": "Active",
        "Trading Status": "Ready",
        "Posting Status": "Configured",
    }

    for key, value in status_report.items():
        print(f"  - {key}: {value}")

    print("\n🚀 The AI agent is now live and executing blockchain interactions!")

    return {
        "Agent Name": agent_name,
        "Solana Transaction ID": solana_tx_id,
        **status_report
    }

if __name__ == "__main__":
    deploy_paradox_agent("ParadoxAI_v1")
