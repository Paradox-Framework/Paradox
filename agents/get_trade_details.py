from framework.agent import post_trade_update

class ParadoxCLI:
    def main_loop(self):
        print("Welcome to Paradox CLI")
        while True:
            command = input("Enter command: ")

            if command.startswith("$post_trade"):
                _, platform, trade_url, message = command.split(" ", 3)
                self.execute_post_trade(platform, trade_url, message)

    def execute_post_trade(self, platform, trade_url, message):
        if platform.lower() == "discord":
            platform_api = DiscordAPI()
        elif platform.lower() == "telegram":
            platform_api = TelegramAPI()
        elif platform.lower() == "twitter":
            platform_api = TwitterAPI()
        else:
            print("Unsupported platform.")
            return

        try:
            post_trade_update(platform_api, trade_url, message)
        except Exception as e:
            print(f"Error posting trade update: {e}")
