from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class TradePostRequest(BaseModel):
    platform: str
    trade_url: str
    message: str

@app.post("/post_trade_update")
async def post_trade_update_api(request: TradePostRequest):
    try:
        platform_api = None
        if request.platform.lower() == "discord":
            platform_api = DiscordAPI()
        elif request.platform.lower() == "telegram":
            platform_api = TelegramAPI()
        elif request.platform.lower() == "twitter":
            platform_api = TwitterAPI()
        else:
            raise HTTPException(status_code=400, detail="Unsupported platform")

        await post_trade_update(platform_api, request.trade_url, request.message)
        return {"status": "success", "message": "Trade update posted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
