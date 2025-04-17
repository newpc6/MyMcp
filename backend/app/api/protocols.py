from fastapi import APIRouter, HTTPException
from typing import List

from ..models.protocols.schemas import ProtocolInfo, ProtocolContent, ProtocolCreate, ProtocolUpdate
from ..services.protocols.service import ProtocolService

router = APIRouter()
protocol_service = ProtocolService()

@router.get("/", response_model=List[ProtocolInfo])
async def get_all_protocols():
    """
    获取所有MCP协议文件信息
    """
    return protocol_service.get_all_protocols()

@router.get("/{path:path}", response_model=ProtocolContent)
async def get_protocol_content(path: str):
    """
    获取指定MCP协议文件的内容
    """
    try:
        return protocol_service.get_protocol_content(path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"协议文件 {path} 不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=ProtocolInfo)
async def create_protocol(protocol: ProtocolCreate):
    """
    创建新的MCP协议文件
    """
    try:
        return protocol_service.create_protocol(protocol)
    except FileExistsError:
        raise HTTPException(status_code=409, detail=f"协议文件 {protocol.path} 已存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{path:path}", response_model=ProtocolContent)
async def update_protocol(path: str, protocol_update: ProtocolUpdate):
    """
    更新MCP协议文件内容
    """
    try:
        return protocol_service.update_protocol(path, protocol_update)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"协议文件 {path} 不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{path:path}")
async def delete_protocol(path: str):
    """
    删除MCP协议文件
    """
    try:
        protocol_service.delete_protocol(path)
        return {"message": f"协议文件 {path} 已成功删除"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"协议文件 {path} 不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 