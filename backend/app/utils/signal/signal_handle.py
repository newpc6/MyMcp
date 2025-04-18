import signal
from app.server.mcp_server import stop_mcp_server
from app.utils.logging import em_logger


def signal_handler(sig, frame):
    em_logger.info("接收到终止信号，正在关闭MCP服务器...")
    stop_mcp_server()
    # sys.exit(0)


def keyboard_handle():
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)