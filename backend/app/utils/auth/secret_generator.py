"""
MCP服务密钥生成工具

提供安全的密钥生成和验证功能
"""

import uuid
import secrets
import string
import hashlib
from datetime import datetime, timedelta
from typing import Optional


class SecretGenerator:
    """密钥生成器"""
    
    @staticmethod
    def generate_secret_key(length: int = 32) -> str:
        """生成安全的密钥
        
        Args:
            length: 密钥长度，默认32位
            
        Returns:
            str: 生成的密钥字符串
        """
        # 使用UUID + 时间戳 + 随机字符串的组合
        uuid_part = str(uuid.uuid4()).replace('-', '')
        timestamp_part = str(int(datetime.now().timestamp() * 1000))
        
        # 生成随机字符串
        alphabet = string.ascii_letters + string.digits
        random_part = ''.join(secrets.choice(alphabet) for _ in range(8))
        
        # 组合并取指定长度
        combined = f"{uuid_part}{timestamp_part}{random_part}"
        
        # 使用SHA256哈希确保长度一致性和安全性
        hash_object = hashlib.sha256(combined.encode())
        hex_dig = hash_object.hexdigest()
        
        # 返回指定长度的密钥
        return hex_dig[:length]
    
    @staticmethod
    def generate_api_key(prefix: str = "mcp", length: int = 32) -> str:
        """生成带前缀的API密钥
        
        Args:
            prefix: 密钥前缀
            length: 密钥主体长度
            
        Returns:
            str: 格式为 prefix_主体密钥 的密钥字符串
        """
        secret = SecretGenerator.generate_secret_key(length)
        return f"{prefix}_{secret}"
    
    @staticmethod
    def is_valid_secret_format(secret: str) -> bool:
        """验证密钥格式是否有效
        
        Args:
            secret: 待验证的密钥
            
        Returns:
            bool: 密钥格式是否有效
        """
        if not secret or not isinstance(secret, str):
            return False
        
        # 检查长度（至少16位）
        if len(secret) < 16:
            return False
        
        # 检查字符（只允许字母数字和下划线）
        allowed_chars = string.ascii_letters + string.digits + '_'
        return all(c in allowed_chars for c in secret)
    
    @staticmethod
    def mask_secret(secret: str) -> str:
        """脱敏显示密钥
        
        Args:
            secret: 原始密钥
            
        Returns:
            str: 脱敏后的密钥
        """
        if not secret or len(secret) < 8:
            return "****"
        
        return f"{secret[:4]}****{secret[-4:]}"
    
    @staticmethod
    def calculate_expiry_date(days: int) -> Optional[datetime]:
        """计算过期时间
        
        Args:
            days: 有效天数，0表示永不过期
            
        Returns:
            Optional[datetime]: 过期时间，None表示永不过期
        """
        if days <= 0:
            return None
        
        return datetime.now() + timedelta(days=days)
    
    @staticmethod
    def is_secret_expired(expires_at: Optional[datetime]) -> bool:
        """检查密钥是否已过期
        
        Args:
            expires_at: 过期时间
            
        Returns:
            bool: 是否已过期
        """
        if not expires_at:
            return False
        
        return datetime.now() > expires_at
    
    @staticmethod
    def generate_secure_token(length: int = 16) -> str:
        """生成安全令牌（用于临时访问）
        
        Args:
            length: 令牌长度
            
        Returns:
            str: 安全令牌
        """
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_secret(secret: str, salt: Optional[str] = None) -> str:
        """对密钥进行哈希处理（用于存储）
        
        Args:
            secret: 原始密钥
            salt: 盐值，如果为None则自动生成
            
        Returns:
            str: 哈希后的密钥（包含盐值）
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        combined = f"{salt}{secret}"
        hash_object = hashlib.sha256(combined.encode())
        
        return f"{salt}:{hash_object.hexdigest()}"
    
    @staticmethod
    def verify_secret(secret: str, hashed: str) -> bool:
        """验证密钥是否匹配哈希值
        
        Args:
            secret: 原始密钥
            hashed: 哈希后的密钥（包含盐值）
            
        Returns:
            bool: 是否匹配
        """
        try:
            salt, hash_part = hashed.split(':', 1)
            combined = f"{salt}{secret}"
            hash_object = hashlib.sha256(combined.encode())
            
            return hash_object.hexdigest() == hash_part
        except ValueError:
            return False 