from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime
import os

# 創建 Flask 應用實例
app = Flask(__name__)

# 設定資料庫連線
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://voice_order_user:24999441@localhost/voice_order_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化資料庫
db = SQLAlchemy()
db.init_app(app)

# 定義模型
class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    last_login = db.Column(db.DateTime)
    role = db.Column(db.String(50))
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'))

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

class Shop(db.Model):
    __tablename__ = 'shops'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255))
    phone = db.Column(db.String(20))

def init_db():
    with app.app_context():
        # 建立所有表格
        db.create_all()
        
        # 檢查是否已有管理員帳戶
        admin_exists = Admin.query.filter_by(username='admin').first()
        if not admin_exists:
            # 創建默認管理員
            default_admin = Admin(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                name='系統管理員',
                email='admin@example.com'
            )
            db.session.add(default_admin)
            
        # 檢查是否已有產品分類
        categories_exist = Category.query.first()
        if not categories_exist:
            # 創建預設分類
            categories = [
                Category(name='茶類', description='各種茶類飲品'),
                Category(name='奶茶', description='奶茶系列'),
                Category(name='鮮奶', description='鮮奶系列'),
                Category(name='特調', description='特調飲品')
            ]
            db.session.add_all(categories)

        # 建立超級管理員
        super_admin = Admin.query.filter_by(username='superadmin').first()
        if not super_admin:
            super_admin = Admin(
                username='superadmin',
                password_hash=generate_password_hash('adminsuper123'),
                name='系統管理員',
                email='super@example.com',
                role='super_admin'
            )
            db.session.add(super_admin)

        # 建立測試商家和其管理員
        test_shops = [
            {
                'name': '測試飲料店1',
                'address': '台北市測試區1號',
                'phone': '02-1234-5678',
                'admin': {
                    'username': 'shop1admin',
                    'password': 'shop1pass',
                    'name': '店家管理員1',
                    'email': 'shop1@example.com'
                }
            },
            {
                'name': '測試飲料店2',
                'address': '台北市測試區2號',
                'phone': '02-2345-6789',
                'admin': {
                    'username': 'shop2admin',
                    'password': 'shop2pass',
                    'name': '店家管理員2',
                    'email': 'shop2@example.com'
                }
            }
        ]

        for shop_data in test_shops:
            shop = Shop.query.filter_by(name=shop_data['name']).first()
            if not shop:
                shop = Shop(
                    name=shop_data['name'],
                    address=shop_data['address'],
                    phone=shop_data['phone']
                )
                db.session.add(shop)
                db.session.flush()  # 取得shop.id

                # 建立店家管理員
                admin = Admin(
                    username=shop_data['admin']['username'],
                    password_hash=generate_password_hash(shop_data['admin']['password']),
                    name=shop_data['admin']['name'],
                    email=shop_data['admin']['email'],
                    role='shop_admin',
                    shop_id=shop.id
                )
                db.session.add(admin)
            
        db.session.commit()
        print("資料庫初始化完成")

if __name__ == "__main__":
    init_db()
