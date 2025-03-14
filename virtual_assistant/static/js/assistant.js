class AssistantUI {
    constructor() {
        this.model = null;
        this.isListening = false;
        
        this.initLive2D();
        this.initVoiceButton();
    }

    async initLive2D() {
        // 初始化 Live2D 模型
        const modelPath = '/static/model/assistant.model3.json';
        this.model = await Live2DModel.from(modelPath);
        
        // 將模型添加到畫布
        const canvas = document.getElementById('live2d');
        canvas.appendChild(this.model);
    }

    initVoiceButton() {
        const button = document.getElementById('start-voice');
        button.addEventListener('click', () => this.toggleVoiceInput());
    }

    async toggleVoiceInput() {
        if (!this.isListening) {
            this.startListening();
        } else {
            this.stopListening();
        }
    }

    // ... 其他互動方法
}

// 初始化助手
const assistant = new AssistantUI();
