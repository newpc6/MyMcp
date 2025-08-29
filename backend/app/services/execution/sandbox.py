"""
代码执行沙箱实现 - 增强版
"""
import sys
import builtins
import threading
from functools import wraps
from typing import Any, Callable, Dict, Set, Optional

# 尝试导入 resource 模块，在 Windows 上可能不可用
try:
    import resource
    HAS_RESOURCE = True
except ImportError:
    HAS_RESOURCE = False

from app.utils.logging import get_logger

# 获取日志记录器
sandbox_logger = get_logger("sandbox")


class SandboxConfig:
    """沙箱配置类"""

    def __init__(self):
        # 允许的模块列表
        self.allowed_modules: Set[str] = {
            'math', 'random', 'datetime', 'json',
            're', 'string', 'collections', 'itertools',
            'decimal', 'fractions', 'statistics',
            'uuid', 'hashlib', 'base64', 'urllib.parse'
        }

        # 禁止的模块列表
        self.forbidden_modules: Set[str] = {
            'os', 'sys', 'subprocess', 'socket', 'urllib.request',
            'urllib.urlopen', 'httplib', 'ftplib', 'telnetlib',
            'smtplib', 'poplib', 'imaplib', 'nntplib',
            'ssl', 'threading', 'multiprocessing', 'asyncio',
            'ctypes', 'marshal', 'pickle', 'shelve', 'dbm',
            'sqlite3', 'tempfile', 'shutil', 'glob', 'fnmatch',
            'linecache', 'fileinput', 'platform', 'getpass',
            'pwd', 'grp', 'termios', 'tty', 'pty', 'fcntl',
            'pipes', 'posix', 'resource', 'nis', 'syslog',
            'commands', 'imp', 'importlib', 'runpy',
            'pathlib', 'zipfile', 'tarfile', 'gzip', 'bz2', 'lzma',
            'zipimport', 'mmap', 'signal', 'select', 'selectors'
        }

        # 禁止的内置函数
        self.forbidden_builtins: Set[str] = {
            'open', 'exec', 'eval', 'compile', 'input',
            'raw_input', '__import__', 'reload', 'exit', 'quit',
            'help', 'license', 'copyright', 'credits',
            'dir', 'vars', 'locals', 'globals', 'breakpoint',
            'memoryview', 'bytearray', 'bytes', 'super'
        }

        # 执行超时时间（秒）
        self.timeout: int = 30

        # 内存限制（字节）
        self.memory_limit: int = 100 * 1024 * 1024  # 100MB

        # 是否记录安全事件
        self.log_security_events: bool = True


class SandboxViolationError(Exception):
    """沙箱违规异常"""
    pass


class SandboxTimeoutError(Exception):
    """沙箱超时异常"""
    pass


class Sandbox:
    """
    增强版代码执行沙箱环境
    """

    def __init__(self, config: Optional[SandboxConfig] = None):
        self.config = config or SandboxConfig()
        self._original_builtins: Dict[str, Any] = {}
        self._original_modules: Dict[str, Any] = {}
        self._timeout_timer: Optional[threading.Timer] = None

    def __enter__(self):
        """进入沙箱环境"""
        try:
            self._setup_security_restrictions()
            self._setup_resource_limits()
            self._setup_timeout()

            if self.config.log_security_events:
                sandbox_logger.info("沙箱环境已激活")

            return self

        except Exception as e:
            sandbox_logger.error(f"沙箱环境初始化失败: {str(e)}")
            self._cleanup()
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出沙箱环境"""
        try:
            self._cleanup()

            if self.config.log_security_events:
                if exc_type is None:
                    sandbox_logger.info("沙箱环境正常退出")
                else:
                    sandbox_logger.warning(
                        f"沙箱环境异常退出: {exc_type.__name__}: {exc_val}")

        except Exception as e:
            sandbox_logger.error(f"沙箱环境清理失败: {str(e)}")

    def _setup_security_restrictions(self):
        """设置安全限制"""
        # 备份并替换危险的内置函数
        for builtin_name in self.config.forbidden_builtins:
            if hasattr(builtins, builtin_name):
                self._original_builtins[builtin_name] = getattr(
                    builtins, builtin_name)
                setattr(builtins, builtin_name,
                        self._create_forbidden_function(builtin_name))

        # 特殊处理 __import__
        if '__import__' in self.config.forbidden_builtins:
            self._original_builtins['__import__'] = builtins.__import__
            builtins.__import__ = self._safe_import

        # 备份并禁用危险模块
        for module_name in self.config.forbidden_modules:
            if module_name in sys.modules:
                self._original_modules[module_name] = sys.modules[module_name]
            sys.modules[module_name] = None

    def _setup_resource_limits(self):
        """设置资源限制"""
        if not HAS_RESOURCE:
            # Windows 系统不支持 resource 模块，跳过资源限制设置
            if self.config.log_security_events:
                sandbox_logger.info("当前系统不支持资源限制设置（Windows系统）")
            return
            
        try:
            # 设置内存限制（仅在支持的系统上）
            if hasattr(resource, 'RLIMIT_AS'):
                resource.setrlimit(
                    resource.RLIMIT_AS,
                    (self.config.memory_limit, self.config.memory_limit)
                )
        except (ImportError, OSError) as e:
            # 在不支持resource模块的系统上忽略
            if self.config.log_security_events:
                sandbox_logger.warning(f"资源限制设置失败: {str(e)}")
            pass

    def _setup_timeout(self):
        """设置执行超时"""
        if self.config.timeout > 0:
            self._timeout_timer = threading.Timer(
                self.config.timeout,
                self._timeout_handler
            )
            self._timeout_timer.start()

    def _timeout_handler(self):
        """超时处理器"""
        if self.config.log_security_events:
            sandbox_logger.warning(f"沙箱执行超时 ({self.config.timeout}秒)")
        raise SandboxTimeoutError(f"执行超时 ({self.config.timeout}秒)")

    def _cleanup(self):
        """清理沙箱环境"""
        # 停止超时计时器
        if self._timeout_timer:
            self._timeout_timer.cancel()
            self._timeout_timer = None

        # 恢复内置函数
        for builtin_name, original_func in self._original_builtins.items():
            setattr(builtins, builtin_name, original_func)
        self._original_builtins.clear()

        # 恢复模块
        for module_name, original_module in self._original_modules.items():
            if original_module is not None:
                sys.modules[module_name] = original_module
            elif module_name in sys.modules:
                del sys.modules[module_name]
        self._original_modules.clear()

    def _create_forbidden_function(self, func_name: str) -> Callable:
        """创建禁止访问的函数"""
        def forbidden_func(*args, **kwargs):
            error_msg = f"函数 {func_name} 在沙箱环境中被禁止使用"
            if self.config.log_security_events:
                sandbox_logger.warning(f"安全违规: 尝试调用禁止函数 {func_name}")
            raise SandboxViolationError(error_msg)
        return forbidden_func

    def _safe_import(
            self, name, globals=None, locals=None,
            fromlist=(), level=0):
        """安全的模块导入"""
        # 检查是否为禁止模块
        if name in self.config.forbidden_modules:
            error_msg = f"模块 {name} 在沙箱环境中被禁止导入"
            if self.config.log_security_events:
                sandbox_logger.warning(f"安全违规: 尝试导入禁止模块 {name}")
            raise SandboxViolationError(error_msg)

        # 检查是否为允许模块
        if name not in self.config.allowed_modules:
            error_msg = f"模块 {name} 不在允许的模块列表中"
            if self.config.log_security_events:
                sandbox_logger.warning(f"安全违规: 尝试导入未授权模块 {name}")
            raise SandboxViolationError(error_msg)

        # 使用原始导入函数
        return self._original_builtins['__import__'](
            name,
            globals,
            locals,
            fromlist,
            level
        )


def sandboxed(func: Callable = None, *, config: Optional[SandboxConfig] = None) -> Callable:
    """
    沙箱执行装饰器 - 增强版

    Args:
        func: 要包装的函数
        config: 自定义沙箱配置

    Returns:
        包装后的安全函数

    Usage:
        @sandboxed
        def my_function():
            pass

        @sandboxed(config=custom_config)
        def my_function():
            pass
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs) -> Any:
            sandbox_config = config or SandboxConfig()

            try:
                with Sandbox(sandbox_config):
                    return f(*args, **kwargs)
            except SandboxViolationError as e:
                sandbox_logger.error(f"沙箱安全违规: {str(e)}")
                raise
            except SandboxTimeoutError as e:
                sandbox_logger.error(f"沙箱执行超时: {str(e)}")
                raise
            except Exception as e:
                sandbox_logger.error(f"沙箱执行异常: {str(e)}")
                raise

        return wrapper

    # 支持带参数和不带参数的装饰器用法
    if func is None:
        return decorator
    else:
        return decorator(func)


def create_restricted_sandbox(
        allowed_modules: Optional[Set[str]] = None,
        timeout: int = 30,
        memory_limit: int = 100 * 1024 * 1024) -> SandboxConfig:
    """
    创建受限制的沙箱配置

    Args:
        allowed_modules: 允许的模块列表
        timeout: 超时时间（秒）
        memory_limit: 内存限制（字节）

    Returns:
        配置好的沙箱配置对象
    """
    config = SandboxConfig()

    if allowed_modules is not None:
        config.allowed_modules = allowed_modules

    config.timeout = timeout
    config.memory_limit = memory_limit

    return config


def create_permissive_sandbox(
        additional_modules: Optional[Set[str]] = None,
        timeout: int = 60) -> SandboxConfig:
    """
    创建宽松的沙箱配置（用于可信代码）

    Args:
        additional_modules: 额外允许的模块
        timeout: 超时时间（秒）

    Returns:
        配置好的沙箱配置对象
    """
    config = SandboxConfig()

    # 添加更多允许的模块
    config.allowed_modules.update({
        'csv', 'xml', 'html', 'email', 'mimetypes',
        'calendar', 'locale', 'gettext', 'unicodedata',
        'codecs', 'encodings', 'io', 'struct', 'array',
        'bisect', 'heapq', 'weakref', 'copy', 'pprint'
    })

    if additional_modules:
        config.allowed_modules.update(additional_modules)

    config.timeout = timeout

    return config