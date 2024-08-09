import logging
import os

# 获取当前文件的目录
current_directory = os.path.dirname(os.path.abspath(__file__))

# 创建 log 文件夹（如果不存在）
log_directory = os.path.join(current_directory, "../log")
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(f"{log_directory}/app.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def create_log(msg: str):
    logger.info(msg)
