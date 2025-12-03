"""
算法模块初始化文件
"""

from .loitering import LoiteringDetector
from .leave import LeaveDetector
from .gather import GatherDetector
from .banner import BannerDetector
from .coordinator import VideoProcessingCoordinator

__all__ = [
    "LoiteringDetector",
    "LeaveDetector",
    "GatherDetector",
    "BannerDetector",
    "VideoProcessingCoordinator"
]
