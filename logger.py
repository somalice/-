import logging
import os
from datetime import datetime

def setup_logger(log_dir):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建日志文件
    log_file = os.path.join(log_dir, f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # 配置日志
    logger = logging.getLogger('WSYDownloader')
    logger.setLevel(logging.INFO)
    
    # 清除已有的handler
    logger.handlers.clear()
    
    # 文件handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    
    # 控制台handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)
    
    return logger
