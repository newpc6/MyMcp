import os
import json
from datetime import datetime
from typing import List
import shutil

from ...models.protocols.schemas import (
    ProtocolInfo, 
    ProtocolContent, 
    ProtocolCreate, 
    ProtocolUpdate
)
from ...config import settings


class ProtocolService:
    """MCP协议管理服务"""

    def __init__(self):
        # 协议文件根目录
        self.protocols_dir = settings.PROTOCOLS_DIR
        os.makedirs(self.protocols_dir, exist_ok=True)

    def get_all_protocols(self) -> List[ProtocolInfo]:
        """获取所有协议文件信息"""
        protocols = []
        
        for root, _, files in os.walk(self.protocols_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.protocols_dir)
                    
                    # 获取文件状态
                    stat = os.stat(file_path)
                    # 添加8小时时区调整
                    timestamp = datetime.fromtimestamp(stat.st_mtime)
                    last_modified = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # 提取名称和描述
                    name = os.path.splitext(os.path.basename(file))[0]
                    description = self._extract_description(file_path)
                    
                    protocols.append(ProtocolInfo(
                        path=rel_path,
                        name=name,
                        description=description,
                        lastModified=last_modified
                    ))
        
        return protocols

    def get_protocol_content(self, path: str) -> ProtocolContent:
        """获取协议文件内容"""
        full_path = os.path.join(self.protocols_dir, path)
        
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"协议文件 {path} 不存在")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return ProtocolContent(content=content)

    def create_protocol(self, protocol: ProtocolCreate) -> ProtocolInfo:
        """创建新的协议文件"""
        full_path = os.path.join(self.protocols_dir, protocol.path)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        if os.path.exists(full_path):
            raise FileExistsError(f"协议文件 {protocol.path} 已存在")
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(protocol.content)
        
        # 获取文件状态
        stat = os.stat(full_path)
        # 添加8小时时区调整
        timestamp = datetime.fromtimestamp(stat.st_mtime)
        last_modified = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        # 提取名称和描述
        name = os.path.splitext(os.path.basename(full_path))[0]
        description = self._extract_description(full_path)
        
        return ProtocolInfo(
            path=protocol.path,
            name=name,
            description=description,
            lastModified=last_modified
        )

    def update_protocol(self, path: str, protocol_update: ProtocolUpdate) -> ProtocolContent:
        """更新协议文件内容"""
        full_path = os.path.join(self.protocols_dir, path)
        
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"协议文件 {path} 不存在")
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(protocol_update.content)
        
        return ProtocolContent(content=protocol_update.content)

    def delete_protocol(self, path: str) -> None:
        """删除协议文件"""
        full_path = os.path.join(self.protocols_dir, path)
        
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"协议文件 {path} 不存在")
        
        if os.path.isfile(full_path):
            os.remove(full_path)
        else:
            shutil.rmtree(full_path)

    def _extract_description(self, file_path: str) -> str:
        """从文件内容中提取描述信息"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # 只读取前1000个字符来提取描述
            
            description = ""
            
            # 尝试从文件注释中提取描述
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if i == 0 and line.startswith('#'):
                    description = line[1:].strip()
                    break
                elif line.startswith('"""') or line.startswith("'''"):
                    # 查找多行注释
                    end_quote = line[0:3]
                    if end_quote in line[3:]:
                        # 单行多行注释
                        description = line[3:line.find(end_quote, 3)].strip()
                    else:
                        # 多行注释
                        doc = []
                        for j in range(i+1, len(lines)):
                            if end_quote in lines[j]:
                                doc.append(lines[j][:lines[j].find(end_quote)])
                                break
                            doc.append(lines[j])
                        if doc:
                            description = ' '.join([d.strip() for d in doc if d.strip()])
                    break
            
            return description
        except Exception:
            # 如果提取失败，返回空字符串
            return "" 