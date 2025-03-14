from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app import app, db

migrate = Migrate(app, db)

# 執行方式：
# 初始化：flask db init
# 創建遷移：flask db migrate -m "變更說明"
# 執行遷移：flask db upgrade
