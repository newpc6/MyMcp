"""
用户和租户服务模块
"""
from typing import List, Dict, Any, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from pytz import timezone

from app.models.engine import get_db
from app.models.modules.users import User, Tenant, UserTenant
from app.utils.logging import em_logger


class UserService:
    """用户服务类"""
    
    @staticmethod
    def create_user(
        username: str, 
        password: str, 
        fullname: Optional[str] = None,
        email: Optional[str] = None,
        is_admin: bool = False,
        tenant_ids: Optional[List[int]] = None
    ) -> Optional[User]:
        """创建新用户"""
        try:
            with get_db() as db:
                # 检查用户名是否已存在
                user_query = select(User).where(User.username == username)
                existing_user = db.execute(user_query).scalar_one_or_none()
                if existing_user:
                    em_logger.warning(f"用户名 {username} 已存在")
                    return None
                
                # 创建新用户
                now = datetime.now(timezone('Asia/Shanghai'))
                new_user = User(
                    username=username,
                    fullname=fullname,
                    email=email,
                    is_admin=is_admin,
                    created_at=now,
                    updated_at=now
                )
                new_user.set_password(password)
                db.add(new_user)
                db.flush()  # 刷新以获取ID
                
                # 关联租户
                if tenant_ids:
                    for tenant_id in tenant_ids:
                        tenant = db.execute(
                            select(Tenant).where(Tenant.id == tenant_id)
                        ).scalar_one_or_none()
                        
                        if tenant:
                            user_tenant = UserTenant(
                                user_id=new_user.id,
                                tenant_id=tenant_id,
                                created_at=now,
                                updated_at=now
                            )
                            db.add(user_tenant)
                
                db.commit()
                db.refresh(new_user)
                em_logger.info(f"创建用户成功: {username}")
                return new_user
                
        except Exception as e:
            em_logger.error(f"创建用户失败: {str(e)}")
            return None
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        try:
            with get_db() as db:
                query = select(User).where(User.id == user_id)
                return db.execute(query).scalar_one_or_none()
        except Exception as e:
            em_logger.error(f"获取用户失败: {str(e)}")
            return None
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """根据用户名获取用户"""
        try:
            with get_db() as db:
                query = select(User).where(User.username == username)
                return db.execute(query).scalar_one_or_none()
        except Exception as e:
            em_logger.error(f"获取用户失败: {str(e)}")
            return None
    
    @staticmethod
    def update_user(
        user_id: int,
        username: Optional[str] = None,
        fullname: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        is_admin: Optional[bool] = None,
        status: Optional[str] = None
    ) -> bool:
        """更新用户信息"""
        try:
            with get_db() as db:
                # 获取现有用户
                user = db.execute(
                    select(User).where(User.id == user_id)
                ).scalar_one_or_none()
                
                if not user:
                    em_logger.warning(f"用户ID {user_id} 不存在")
                    return False
                
                # 准备更新值
                update_values = {}
                if username is not None:
                    update_values["username"] = username
                if fullname is not None:
                    update_values["fullname"] = fullname
                if email is not None:
                    update_values["email"] = email
                if is_admin is not None:
                    update_values["is_admin"] = is_admin
                if status is not None:
                    update_values["status"] = status
                
                # 更新密码
                if password is not None:
                    user.set_password(password)
                    db.add(user)
                
                # 如果有其他字段需要更新
                if update_values:
                    update_values["updated_at"] = datetime.now(timezone('Asia/Shanghai'))
                    db.execute(
                        update(User)
                        .where(User.id == user_id)
                        .values(**update_values)
                    )
                
                db.commit()
                em_logger.info(f"更新用户成功: {user_id}")
                return True
                
        except IntegrityError:
            em_logger.error(f"更新用户失败: 用户名 {username} 已存在")
            return False
        except Exception as e:
            em_logger.error(f"更新用户失败: {str(e)}")
            return False
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """删除用户"""
        try:
            with get_db() as db:
                # 检查用户是否存在
                user = db.execute(
                    select(User).where(User.id == user_id)
                ).scalar_one_or_none()
                
                if not user:
                    em_logger.warning(f"用户ID {user_id} 不存在")
                    return False
                
                # 删除用户与租户的关联
                db.execute(
                    delete(UserTenant).where(UserTenant.user_id == user_id)
                )
                
                # 删除用户
                db.execute(
                    delete(User).where(User.id == user_id)
                )
                
                db.commit()
                em_logger.info(f"删除用户成功: {user_id}")
                return True
                
        except Exception as e:
            em_logger.error(f"删除用户失败: {str(e)}")
            return False
    
    @staticmethod
    def get_all_users() -> List[User]:
        """获取所有用户"""
        try:
            with get_db() as db:
                query = select(User)
                return db.execute(query).scalars().all()
        except Exception as e:
            em_logger.error(f"获取所有用户失败: {str(e)}")
            return []
    
    @staticmethod
    def update_user_tenants(user_id: int, tenant_ids: List[int]) -> bool:
        """更新用户与租户的关联"""
        try:
            with get_db() as db:
                # 检查用户是否存在
                user = db.execute(
                    select(User).where(User.id == user_id)
                ).scalar_one_or_none()
                
                if not user:
                    em_logger.warning(f"用户ID {user_id} 不存在")
                    return False
                
                # 删除现有关联
                db.execute(
                    delete(UserTenant).where(UserTenant.user_id == user_id)
                )
                
                # 创建新关联
                now = datetime.now(timezone('Asia/Shanghai'))
                for tenant_id in tenant_ids:
                    # 检查租户是否存在
                    tenant = db.execute(
                        select(Tenant).where(Tenant.id == tenant_id)
                    ).scalar_one_or_none()
                    
                    if tenant:
                        user_tenant = UserTenant(
                            user_id=user_id,
                            tenant_id=tenant_id,
                            created_at=now,
                            updated_at=now
                        )
                        db.add(user_tenant)
                
                db.commit()
                em_logger.info(f"更新用户租户关联成功: {user_id}")
                return True
                
        except Exception as e:
            em_logger.error(f"更新用户租户关联失败: {str(e)}")
            return False

    @staticmethod
    def validate_login(username: str, password: str) -> Optional[User]:
        """验证用户登录"""
        try:
            with get_db() as db:
                query = select(User).where(User.username == username)
                user = db.execute(query).scalar_one_or_none()
                
                if user and user.check_password(password) and user.status == 'active':
                    return user
                
                return None
        except Exception as e:
            em_logger.error(f"用户登录验证失败: {str(e)}")
            return None


class TenantService:
    """租户服务类"""
    
    @staticmethod
    def create_tenant(
        name: str,
        code: str,
        description: Optional[str] = None
    ) -> Optional[Tenant]:
        """创建新租户"""
        try:
            with get_db() as db:
                # 检查租户代码是否已存在
                tenant_query = select(Tenant).where(Tenant.code == code)
                existing_tenant = db.execute(tenant_query).scalar_one_or_none()
                if existing_tenant:
                    em_logger.warning(f"租户代码 {code} 已存在")
                    return None
                
                # 创建新租户
                now = datetime.now(timezone('Asia/Shanghai'))
                new_tenant = Tenant(
                    name=name,
                    code=code,
                    description=description,
                    created_at=now,
                    updated_at=now
                )
                db.add(new_tenant)
                db.commit()
                db.refresh(new_tenant)
                em_logger.info(f"创建租户成功: {name}")
                return new_tenant
                
        except Exception as e:
            em_logger.error(f"创建租户失败: {str(e)}")
            return None
    
    @staticmethod
    def get_tenant_by_id(tenant_id: int) -> Optional[Tenant]:
        """根据ID获取租户"""
        try:
            with get_db() as db:
                query = select(Tenant).where(Tenant.id == tenant_id)
                return db.execute(query).scalar_one_or_none()
        except Exception as e:
            em_logger.error(f"获取租户失败: {str(e)}")
            return None
    
    @staticmethod
    def get_tenant_by_code(code: str) -> Optional[Tenant]:
        """根据代码获取租户"""
        try:
            with get_db() as db:
                query = select(Tenant).where(Tenant.code == code)
                return db.execute(query).scalar_one_or_none()
        except Exception as e:
            em_logger.error(f"获取租户失败: {str(e)}")
            return None
    
    @staticmethod
    def update_tenant(
        tenant_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None
    ) -> bool:
        """更新租户信息"""
        try:
            with get_db() as db:
                # 获取现有租户
                tenant = db.execute(
                    select(Tenant).where(Tenant.id == tenant_id)
                ).scalar_one_or_none()
                
                if not tenant:
                    em_logger.warning(f"租户ID {tenant_id} 不存在")
                    return False
                
                # 准备更新值
                update_values = {}
                if name is not None:
                    update_values["name"] = name
                if description is not None:
                    update_values["description"] = description
                if status is not None:
                    update_values["status"] = status
                
                # 如果有字段需要更新
                if update_values:
                    update_values["updated_at"] = datetime.now(timezone('Asia/Shanghai'))
                    db.execute(
                        update(Tenant)
                        .where(Tenant.id == tenant_id)
                        .values(**update_values)
                    )
                
                db.commit()
                em_logger.info(f"更新租户成功: {tenant_id}")
                return True
                
        except Exception as e:
            em_logger.error(f"更新租户失败: {str(e)}")
            return False
    
    @staticmethod
    def delete_tenant(tenant_id: int) -> bool:
        """删除租户"""
        try:
            with get_db() as db:
                # 检查租户是否存在
                tenant = db.execute(
                    select(Tenant).where(Tenant.id == tenant_id)
                ).scalar_one_or_none()
                
                if not tenant:
                    em_logger.warning(f"租户ID {tenant_id} 不存在")
                    return False
                
                # 删除用户与租户的关联
                db.execute(
                    delete(UserTenant).where(UserTenant.tenant_id == tenant_id)
                )
                
                # 删除租户
                db.execute(
                    delete(Tenant).where(Tenant.id == tenant_id)
                )
                
                db.commit()
                em_logger.info(f"删除租户成功: {tenant_id}")
                return True
                
        except Exception as e:
            em_logger.error(f"删除租户失败: {str(e)}")
            return False
    
    @staticmethod
    def get_all_tenants() -> List[Tenant]:
        """获取所有租户"""
        try:
            with get_db() as db:
                query = select(Tenant)
                return db.execute(query).scalars().all()
        except Exception as e:
            em_logger.error(f"获取所有租户失败: {str(e)}")
            return []
    
    @staticmethod
    def get_user_tenants(user_id: int) -> List[Tenant]:
        """获取用户关联的所有租户"""
        try:
            with get_db() as db:
                # 检查用户是否存在
                user = db.execute(
                    select(User).where(User.id == user_id)
                ).scalar_one_or_none()
                
                if not user:
                    em_logger.warning(f"用户ID {user_id} 不存在")
                    return []
                
                # 获取用户关联的租户
                query = (
                    select(Tenant)
                    .join(UserTenant)
                    .where(UserTenant.user_id == user_id)
                )
                return db.execute(query).scalars().all()
                
        except Exception as e:
            em_logger.error(f"获取用户租户失败: {str(e)}")
            return [] 