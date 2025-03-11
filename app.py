from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import speech_recognition as sr
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import soundfile as sf
import io
import numpy as np
from pydub import AudioSegment
from order_analyzer import OrderAnalyzer
import json  # 新增這行
load_dotenv()

app = Flask(__name__)
# MySQL 資料庫連接設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://voice_order_user:24999441@localhost/voice_order_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.config['UPLOAD_FOLDER'] = 'temp_audio'

# 確保臨時音訊檔案夾存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class VoiceOrder(db.Model):
    __tablename__ = 'voice_orders'
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    drink_name = db.Column(db.String(100), nullable=False)
    ice_type = db.Column(db.String(50), nullable=False)
    suger_type = db.Column(db.String(50), nullable=False)
    order_data = db.Column(db.Text)
    order_time = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    weather_status = db.Column(db.String(100))
    weather_temperature = db.Column(db.DECIMAL(4,1))
    phone_number = db.Column(db.String(20))
@app.route('/')
def index():
    return render_template('index.html')  # 只需要提供檔案名稱

analyzer = OrderAnalyzer()

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    try:
        # 從請求中獲取文字
        data = request.json
        if not data or 'text' not in data:
            return jsonify({
                'status': 'error',
                'message': '未收到訂單文字'
            })
        
        # 使用使用者輸入的文字
        text = data['text']
        print(f"處理訂單文字: {text}")  # 除錯訊息
        
        # 分析訂單
        order_details = analyzer.analyze_order(text)
        print(f"分析結果: {order_details}")  # 除錯訊息

        return jsonify({
            'status': 'success',
            'speech_text': text,
            'order_details': order_details
        })

    except Exception as e:
        print(f"處理訂單時發生錯誤：{str(e)}")  # 除錯訊息
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/menu')
def menu():
    return render_template('menu.html')


@app.route('/confirm_order', methods=['POST'])
def confirm_order():
    try:
        data = request.json
        print(f"收到訂單資料：{data}")  # 除錯訊息
        
        # 處理每一個飲料訂單
        for order_item in data['order_details']:
            new_order = VoiceOrder(
                drink_name=order_item['drink_name'],
                ice_type=order_item['ice'],
                suger_type=order_item['sugar'],
                order_data=json.dumps(data['order_details'])  # 儲存完整訂單資料
            )
            db.session.add(new_order)
        
        db.session.commit()
        print("所有訂單已儲存")  # 除錯訊息

        return jsonify({
            'status': 'success',
            'message': '好的，尊貴的客人請稍候，正在為您製作飲品'
        })

    except Exception as e:
        print(f"儲存訂單時發生錯誤：{str(e)}")  # 除錯訊息
        return jsonify({
            'status': 'error',
            'message': f'儲存訂單時發生錯誤: {str(e)}'
        })

if __name__ == '__main__':
    app.run(debug=True,port="5002")