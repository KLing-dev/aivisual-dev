"""
横幅检测算法模块
"""

from .detector import BannerDetector
from .processor import process_banner_video

__all__ = ["BannerDetector", "process_banner_video"]
