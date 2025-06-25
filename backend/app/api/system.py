"""
系统管理API接口
"""
from starlette.requests import Request
from starlette.routing import Route

from app.services.system.service import system_service
from app.utils.response import success_response, error_response
from app.utils.permissions import get_user_info


async def get_system_info(request: Request):
    """获取系统信息"""
    # 获取用户信息
    user_id, is_admin = get_user_info(request)
    
    # 检查管理员权限
    if not is_admin:
        return error_response(
            "需要管理员权限", 
            code=403, 
            http_status_code=403
        )
    
    try:
        system_info = await system_service.get_system_info()
        return success_response(system_info)
    except Exception as e:
        return error_response(
            f"获取系统信息失败: {str(e)}", 
            code=500, 
            http_status_code=500
        )


async def get_installed_packages(request: Request):
    """获取已安装的Python包列表"""
    # 获取用户信息
    user_id, is_admin = get_user_info(request)
    
    # 检查管理员权限
    if not is_admin:
        return error_response(
            "需要管理员权限", 
            code=403, 
            http_status_code=403
        )
    
    try:
        packages = await system_service.get_installed_packages()
        return success_response(packages)
    except Exception as e:
        return error_response(
            f"获取包列表失败: {str(e)}", 
            code=500, 
            http_status_code=500
        )


async def install_package(request: Request):
    """安装Python包"""
    # 获取用户信息
    user_id, is_admin = get_user_info(request)
    
    # 检查管理员权限
    if not is_admin:
        return error_response("需要管理员权限", code=403, http_status_code=403)
    
    try:
        data = await request.json()
        package_name = data.get("package")
        upgrade = data.get("upgrade", False)
        user_install = data.get("user", False)
        index_url = data.get(
            "index_url", 
            "https://pypi.tuna.tsinghua.edu.cn/simple/"
        )
        
        if not package_name:
            return error_response("缺少包名", code=400, http_status_code=400)
        
        result = await system_service.install_package(
            package_name=package_name,
            upgrade=upgrade,
            user_install=user_install,
            index_url=index_url
        )
        return success_response(result, message="包安装成功")
    except Exception as e:
        return error_response(f"安装包失败: {str(e)}", code=500, http_status_code=500)


async def upgrade_package(request: Request):
    """升级Python包"""
    # 获取用户信息
    user_id, is_admin = get_user_info(request)
    
    # 检查管理员权限
    if not is_admin:
        return error_response("需要管理员权限", code=403, http_status_code=403)
    
    try:
        data = await request.json()
        package_name = data.get("package")
        index_url = data.get("index_url", "https://pypi.tuna.tsinghua.edu.cn/simple/")
        
        if not package_name:
            return error_response("缺少包名", code=400, http_status_code=400)
        
        result = await system_service.upgrade_package(package_name, index_url)
        return success_response(result, message="包升级成功")
    except Exception as e:
        return error_response(f"升级包失败: {str(e)}", code=500, http_status_code=500)


async def uninstall_package(request: Request):
    """卸载Python包"""
    # 获取用户信息
    user_id, is_admin = get_user_info(request)
    
    # 检查管理员权限
    if not is_admin:
        return error_response("需要管理员权限", code=403, http_status_code=403)
    
    try:
        package_name = request.path_params["package_name"]
        
        if not package_name:
            return error_response("缺少包名", code=400, http_status_code=400)
        
        result = await system_service.uninstall_package(package_name)
        return success_response(result, message="包卸载成功")
    except Exception as e:
        return error_response(f"卸载包失败: {str(e)}", code=500, http_status_code=500)


async def get_service_status(request: Request):
    """获取系统服务状态"""
    # 获取用户信息
    user_id, is_admin = get_user_info(request)
    
    # 检查管理员权限
    if not is_admin:
        return error_response("需要管理员权限", code=403, http_status_code=403)
    
    try:
        status = await system_service.get_service_status()
        return success_response(status)
    except Exception as e:
        return error_response(f"获取服务状态失败: {str(e)}", code=500, http_status_code=500)


async def restart_service(request: Request):
    """重启服务"""
    # 获取用户信息
    user_id, is_admin = get_user_info(request)
    
    # 检查管理员权限
    if not is_admin:
        return error_response("需要管理员权限", code=403, http_status_code=403)
    
    try:
        service_name = request.path_params["service_name"]
        result = await system_service.restart_service(service_name)
        return success_response(result, message=f"服务 {service_name} 重启成功")
    except Exception as e:
        return error_response(f"重启服务失败: {str(e)}", code=500, http_status_code=500)


async def stop_service(request: Request):
    """停止服务"""
    # 获取用户信息
    user_id, is_admin = get_user_info(request)
    
    # 检查管理员权限
    if not is_admin:
        return error_response("需要管理员权限", code=403, http_status_code=403)
    
    try:
        service_name = request.path_params["service_name"]
        result = await system_service.stop_service(service_name)
        return success_response(result, message=f"服务 {service_name} 停止成功")
    except Exception as e:
        return error_response(f"停止服务失败: {str(e)}", code=500, http_status_code=500)


async def start_service(request: Request):
    """启动服务"""
    # 获取用户信息
    user_id, is_admin = get_user_info(request)
    
    # 检查管理员权限
    if not is_admin:
        return error_response("需要管理员权限", code=403, http_status_code=403)
    
    try:
        service_name = request.path_params["service_name"]
        result = await system_service.start_service(service_name)
        return success_response(result, message=f"服务 {service_name} 启动成功")
    except Exception as e:
        return error_response(f"启动服务失败: {str(e)}", code=500, http_status_code=500)


async def get_system_logs(request: Request):
    """获取系统日志"""
    # 获取用户信息
    user_id, is_admin = get_user_info(request)
    
    # 检查管理员权限
    if not is_admin:
        return error_response("需要管理员权限", code=403, http_status_code=403)
    
    try:
        level = request.query_params.get("level")
        limit = int(request.query_params.get("limit", 100))
        offset = int(request.query_params.get("offset", 0))
        
        logs = await system_service.get_system_logs(
            level=level,
            limit=limit,
            offset=offset
        )
        return success_response(logs)
    except Exception as e:
        return error_response(f"获取系统日志失败: {str(e)}", code=500, http_status_code=500)


async def clear_system_logs(request: Request):
    """清空系统日志"""
    # 获取用户信息
    user_id, is_admin = get_user_info(request)
    
    # 检查管理员权限
    if not is_admin:
        return error_response("需要管理员权限", code=403, http_status_code=403)
    
    try:
        result = await system_service.clear_system_logs()
        return success_response(result, message="系统日志清空成功")
    except Exception as e:
        return error_response(f"清空系统日志失败: {str(e)}", code=500, http_status_code=500)


def get_router():
    """获取系统管理相关路由"""
    routes = [
        Route("/info", get_system_info, methods=["GET"]),
        Route("/python/packages", get_installed_packages, methods=["GET"]),
        Route("/python/install", install_package, methods=["POST"]),
        Route("/python/upgrade", upgrade_package, methods=["POST"]),
        Route("/python/uninstall/{package_name}", uninstall_package, methods=["DELETE"]),
        Route("/services/status", get_service_status, methods=["GET"]),
        Route("/services/{service_name}/restart", restart_service, methods=["POST"]),
        Route("/services/{service_name}/stop", stop_service, methods=["POST"]),
        Route("/services/{service_name}/start", start_service, methods=["POST"]),
        Route("/logs", get_system_logs, methods=["GET"]),
        Route("/logs", clear_system_logs, methods=["DELETE"]),
    ]
    return routes 