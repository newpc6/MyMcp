// types/modules.ts
export interface ModuleInfo {
  path: string; // 模块的相对路径
  name: string;
  description: string;
  lastModified: string;
  // size?: number; // 可以根据后端返回情况添加
}

export interface ModuleContent {
  content: string;
}

export interface ModuleCreate {
  path: string; // 新模块的相对路径，例如 my_module.py
  content: string;
}

export interface ModuleUpdate {
  content: string;
} 