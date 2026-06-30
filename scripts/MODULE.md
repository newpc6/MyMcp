# 自动化脚本模块

## 职责边界

`scripts/` 存放项目级开发、验证和维护脚本。脚本应只编排现有工具链，不在脚本中隐藏业务逻辑或修改运行时行为。

## 当前脚本

- `verify.ps1`：统一执行后端基础编译/import 检查和前端生产构建；前端依赖仍由 yarn 管理，脚本直接调用本地 Vite CLI，避免 yarn 扫描上级目录 package 元数据提示干扰验证输出。

## verify.ps1 使用方式

```powershell
powershell -ExecutionPolicy Bypass -File scripts/verify.ps1
powershell -ExecutionPolicy Bypass -File scripts/verify.ps1 -Scope backend
powershell -ExecutionPolicy Bypass -File scripts/verify.ps1 -Scope frontend
```

参数：

- `-Scope`：`all` / `backend` / `frontend`，默认 `all`。
- `-CondaEnv`：后端 conda 环境名，默认 `mcp`；脚本会优先查找 `conda` 命令和常见安装路径，如果都找不到才退回当前 `python`。

## 依赖关系

- 后端依赖本机 conda 环境 `mcp`。
- 前端依赖 `frontend/` 下 yarn 依赖已安装，且存在 `node_modules/vite/bin/vite.js`。

## 验证方式

修改脚本后运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/verify.ps1
```

## 改动记录

- 2026-06-30：新增 `verify.ps1`，覆盖后端 py_compile/import smoke 和前端 `yarn build`。
- 2026-06-30：后端 Python 执行增加 Conda 路径探测和 fallback，并显式检查外部命令 exit code；前端构建改为调用本地 Vite CLI。
