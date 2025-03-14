from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
import os
from functools import wraps

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://voice_order_user:24999441@localhost/voice_order_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化資料庫
db = SQLAlchemy()
db.init_app(app)

# 定義模型類
class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

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

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.DECIMAL(10, 2), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

# 登入要求裝飾器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('請先登入', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 登入頁面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session['admin_id'] = admin.id
            session['admin_name'] = admin.username
            flash('登入成功！', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('帳號或密碼錯誤', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('已成功登出', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    # 取得今日訂單數量
    today = datetime.now().date()
    today_orders_count = VoiceOrder.query.filter(
        func.date(VoiceOrder.order_time) == today
    ).count()
    
    # 取得本月熱門飲品
    current_month = datetime.now().month
    current_year = datetime.now().year
    popular_drinks = db.session.query(
        VoiceOrder.drink_name,
        func.count(VoiceOrder.drink_name).label('count')
    ).filter(
        extract('month', VoiceOrder.order_time) == current_month,
        extract('year', VoiceOrder.order_time) == current_year
    ).group_by(
        VoiceOrder.drink_name
    ).order_by(
        func.count(VoiceOrder.drink_name).desc()
    ).limit(5).all()
    
    # 最近訂單
    recent_orders = VoiceOrder.query.order_by(
        VoiceOrder.order_time.desc()
    ).limit(10).all()
    
    return render_template('dashboard.html', 
                          today_orders=today_orders_count,
                          popular_drinks=popular_drinks,
                          recent_orders=recent_orders)

# 訂單管理
@app.route('/orders')
@login_required
def orders():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    orders = VoiceOrder.query.order_by(VoiceOrder.order_time.desc()).paginate(page=page, per_page=per_page)
    return render_template('orders.html', orders=orders)

@app.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    order = VoiceOrder.query.get_or_404(order_id)
    return render_template('order_detail.html', order=order)

# 產品管理
@app.route('/products')
@login_required
def products():
    products = Product.query.all()
    categories = Category.query.all()
    return render_template('products.html', products=products, categories=categories)

@app.route('/products/add', methods=['POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        category_id = request.form.get('category_id')
        description = request.form.get('description', '')
        
        product = Product(name=name, price=price, category_id=category_id, description=description)
        db.session.add(product)
        db.session.commit()
        
        flash('產品新增成功', 'success')
        return redirect(url_for('products'))

# 數據分析
@app.route('/analytics')
@login_required
def analytics():
    # 銷售趨勢（最近30天）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # 每日訂單數量
    daily_orders = db.session.query(
        func.date(VoiceOrder.order_time).label('date'),
        func.count().label('count')
    ).filter(
        VoiceOrder.order_time.between(start_date, end_date)
    ).group_by(
        func.date(VoiceOrder.order_time)
    ).all()
    
    # 轉換為圖表數據格式
    dates = [str(result.date) for result in daily_orders]
    counts = [result.count for result in daily_orders]
    
    return render_template('analytics.html', 
                          dates=dates, 
                          counts=counts)

@app.route('/api/sales_data')
@login_required
def sales_data():
    # 獲取最近30天的銷售數據
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    daily_orders = db.session.query(
        func.date(VoiceOrder.order_time).label('date'),
        func.count().label('count')
    ).filter(
        VoiceOrder.order_time.between(start_date, end_date)
    ).group_by(
        func.date(VoiceOrder.order_time)
    ).all()
    
    data = {
        'labels': [str(result.date) for result in daily_orders],
        'data': [result.count for result in daily_orders]
    }
    
    return jsonify(data)

# 管理員設置
@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('新密碼與確認密碼不符', 'danger')
            return redirect(url_for('settings'))
        
        admin = Admin.query.get(session['admin_id'])
        if not check_password_hash(admin.password_hash, current_password):
            flash('目前密碼不正確', 'danger')
            return redirect(url_for('settings'))
        
        admin.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        flash('密碼已成功更改', 'success')
        return redirect(url_for('settings'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 確保所有表格都存在
    app.run(debug=True, port=5003)
