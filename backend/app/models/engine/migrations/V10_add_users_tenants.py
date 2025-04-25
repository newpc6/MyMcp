"""
迁移脚本，添加用户表和租户表
"""
from sqlalchemy import text
from app.utils.logging import em_logger


def run(db):
    """执行迁移，创建用户表和租户表"""
    try:
        # 检查tenants表是否存在
        check_tenants_sql = text(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='tenants'"
        )
        result = db.execute(check_tenants_sql).fetchone()
        if not result:
            # 创建租户表
            em_logger.info("创建tenants表")
            db.execute(text("""
                CREATE TABLE tenants (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    code VARCHAR(50) NOT NULL UNIQUE,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """))
            db.commit()
            em_logger.info("tenants表创建完成")
        else:
            em_logger.info("tenants表已存在")

        # 检查users表是否存在
        check_users_sql = text(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='users'"
        )
        result = db.execute(check_users_sql).fetchone()
        if not result:
            # 创建用户表
            em_logger.info("创建users表")
            db.execute(text("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    fullname VARCHAR(100),
                    email VARCHAR(100),
                    is_admin BOOLEAN DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """))
            db.commit()
            em_logger.info("users表创建完成")
        else:
            em_logger.info("users表已存在")

        # 检查user_tenants表是否存在
        check_user_tenants_sql = text(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='user_tenants'"
        )
        result = db.execute(check_user_tenants_sql).fetchone()
        if not result:
            # 创建用户租户关联表
            em_logger.info("创建user_tenants表")
            db.execute(text("""
                CREATE TABLE user_tenants (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    tenant_id INTEGER NOT NULL,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (tenant_id) REFERENCES tenants (id),
                    UNIQUE (user_id, tenant_id)
                )
            """))
            db.commit()
            em_logger.info("user_tenants表创建完成")
        else:
            em_logger.info("user_tenants表已存在")

        # 创建初始管理员用户
        from werkzeug.security import generate_password_hash
        from datetime import datetime
        
        admin_check_sql = text("SELECT id FROM users WHERE username = 'admin'")
        admin_exists = db.execute(admin_check_sql).fetchone()
        
        if not admin_exists:
            em_logger.info("创建默认管理员用户")
            now = datetime.now()
            # 修改默认密码为 eGova@2025
            hashed_password = generate_password_hash("eGova@2025")
            
            db.execute(text("""
                INSERT INTO users (username, password, fullname, is_admin, status, created_at, updated_at)
                VALUES (:username, :password, :fullname, :is_admin, :status, :created_at, :updated_at)
            """), {
                "username": "admin",
                "password": hashed_password,
                "fullname": "系统管理员",
                "is_admin": True,
                "status": "active",
                "created_at": now,
                "updated_at": now
            })
            
            # 创建默认租户
            db.execute(text("""
                INSERT INTO tenants (name, description, code, status, created_at, updated_at)
                VALUES (:name, :description, :code, :status, :created_at, :updated_at)
            """), {
                "name": "默认租户",
                "description": "系统默认租户",
                "code": "default",
                "status": "active",
                "created_at": now,
                "updated_at": now
            })
            
            # 获取用户和租户ID
            admin_id = db.execute(text("SELECT id FROM users WHERE username = 'admin'")).fetchone()[0]
            default_tenant_id = db.execute(text("SELECT id FROM tenants WHERE code = 'default'")).fetchone()[0]
            
            # 关联管理员用户和默认租户
            db.execute(text("""
                INSERT INTO user_tenants (user_id, tenant_id, created_at, updated_at)
                VALUES (:user_id, :tenant_id, :created_at, :updated_at)
            """), {
                "user_id": admin_id,
                "tenant_id": default_tenant_id,
                "created_at": now,
                "updated_at": now
            })
            
            db.commit()
            em_logger.info("默认管理员用户和租户创建完成")
        else:
            em_logger.info("管理员用户已存在")
            
    except Exception as e:
        db.rollback()
        em_logger.error(f"用户和租户表迁移失败: {str(e)}")
        raise 