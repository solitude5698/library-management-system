import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 使用 Windows 身份验证连接 SQL Server
    # 服务器: localhost\SQLEXPRESS01
    DB_CONFIG = {
        'server': 'localhost\\SQLEXPRESS01',  # 注意双反斜杠
        'database': 'LibraryDB',
        'driver': '{ODBC Driver 17 for SQL Server}',
        'trusted_connection': 'yes',  # Windows 身份验证
    }
    
    # 如果使用 SQL Server 身份验证，取消注释以下配置并注释上面的
    # DB_CONFIG = {
    #     'server': 'localhost\\SQLEXPRESS01',
    #     'database': 'LibraryDB',
    #     'driver': '{ODBC Driver 17 for SQL Server}',
    #     'uid': 'sa',
    #     'pwd': 'your_password',
    #     'TrustServerCertificate': 'yes',
    # }
    
    SECRET_KEY = 'your-secret-key-here-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt_secret_key'
    JWT_EXPIRATION_HOURS = 24

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

current_config = config['default']
