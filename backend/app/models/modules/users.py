"""
用户和租户模型模块
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from datetime import datetime
from app.models.engine import Base
from werkzeug.security import generate_password_hash, check_password_hash
from pytz import timezone


class Tenant(Base):
    """租户模型"""
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    code = Column(String(50), nullable=False, unique=True)
    status = Column(String(20), default="active")
    parent_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone('Asia/Shanghai')))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone('Asia/Shanghai')), 
                        onupdate=lambda: datetime.now(timezone('Asia/Shanghai')))
    
    # 关系
    users = relationship("User", secondary="user_tenants", back_populates="tenants")
    children = relationship(
        "Tenant", 
        backref=backref("parent", remote_side=[id]),
        cascade="all, delete-orphan"
    )


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    fullname = Column(String(100))
    email = Column(String(100))
    is_admin = Column(Boolean, default=False)
    status = Column(String(20), default="active")
    external_id = Column(String(100))
    platform_type = Column(String(50))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone('Asia/Shanghai')))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone('Asia/Shanghai')), 
                        onupdate=lambda: datetime.now(timezone('Asia/Shanghai')))
    
    # 关系
    tenants = relationship("Tenant", secondary="user_tenants", back_populates="users")
    
    def set_password(self, password):
        """设置密码，加密存储"""
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        """检查密码是否正确"""
        return check_password_hash(self.password, password)


class UserTenant(Base):
    """用户租户关系模型"""
    __tablename__ = "user_tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone('Asia/Shanghai')))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone('Asia/Shanghai')), 
                        onupdate=lambda: datetime.now(timezone('Asia/Shanghai'))) 