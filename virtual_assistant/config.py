AZURE_SPEECH_KEY = "your_azure_key"
AZURE_SPEECH_REGION = "eastasia"

# 虛擬助手設定
ASSISTANT_CONFIG = {
    "name": "小茶",
    "voice": "zh-TW-HsiaoChenNeural",  # Azure 的台灣中文女聲
    "character_model": "model/assistant.model3.json",  # Live2D 模型檔案
    "greeting": "歡迎光臨，請問需要什麼飲料呢？"
}

# 對話流程設定
CONVERSATION_FLOW = {
    "welcome": ["歡迎光臨", "請問需要什麼飲料呢？"],
    "confirm_order": ["您點的是 {drink_name}，確認一下："],
    "ask_ice": ["請問要什麼冰塊？"],
    "ask_sugar": ["請問甜度要幾分？"],
    "order_complete": ["您的訂單已經完成，請稍候"]
}
