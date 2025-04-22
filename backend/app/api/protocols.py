from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.requests import Request

from ..models.protocols.schemas import ProtocolCreate, ProtocolUpdate
from ..services.protocols.service import ProtocolService

protocol_service = ProtocolService()


async def get_all_protocols(request: Request):
    """
    获取所有MCP协议文件信息
    """
    result = protocol_service.get_all_protocols()
    return JSONResponse(result)


async def get_protocol_content(request: Request):
    """
    获取指定MCP协议文件的内容
    """
    path = request.path_params["path"]
    try:
        result = protocol_service.get_protocol_content(path)
        return JSONResponse(result)
    except FileNotFoundError:
        return JSONResponse({"detail": f"协议文件 {path} 不存在"}, status_code=404)
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


async def create_protocol(request: Request):
    """
    创建新的MCP协议文件
    """
    try:
        data = await request.json()
        protocol = ProtocolCreate(**data)
        result = protocol_service.create_protocol(protocol)
        return JSONResponse(result)
    except FileExistsError:
        return JSONResponse(
            {"detail": f"协议文件 {protocol.path} 已存在"}, 
            status_code=409
        )
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


async def update_protocol(request: Request):
    """
    更新MCP协议文件内容
    """
    path = request.path_params["path"]
    try:
        data = await request.json()
        protocol_update = ProtocolUpdate(**data)
        result = protocol_service.update_protocol(path, protocol_update)
        return JSONResponse(result)
    except FileNotFoundError:
        return JSONResponse({"detail": f"协议文件 {path} 不存在"}, status_code=404)
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


async def delete_protocol(request: Request):
    """
    删除MCP协议文件
    """
    path = request.path_params["path"]
    try:
        protocol_service.delete_protocol(path)
        return JSONResponse({"message": f"协议文件 {path} 已成功删除"})
    except FileNotFoundError:
        return JSONResponse({"detail": f"协议文件 {path} 不存在"}, status_code=404)
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


def get_router():
    """获取协议路由"""
    routes = [
        Route("/", endpoint=get_all_protocols, methods=["GET"]),
        Route("/{path:path}", endpoint=get_protocol_content, methods=["GET"]),
        Route("/", endpoint=create_protocol, methods=["POST"]),
        Route("/{path:path}", endpoint=update_protocol, methods=["PUT"]),
        Route("/{path:path}", endpoint=delete_protocol, methods=["DELETE"])
    ]
    
    return routes 