from paradox.transformer import ParadoxTransformer

class ParadoxAgent:
    def __init__(self):
        self.admin_id = None
        self.trading_personality = "conservative"
        self.auto_post_enabled = False
        self.transformer = ParadoxTransformer()  # Load the built-in transformer model

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
        
        self.transformer.initialize()  # Activate the transformer for AI-driven analysis
        return "Agent successfully deployed and ready for trading, tracking, and analysis."

    def shutdown(self):
        return "Agent has been shut down."
