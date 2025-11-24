"""
核心算法模块
包含所有计算机视觉检测算法的统一接口
"""

from ..algorithms.loitering import LoiteringDetector
from ..algorithms.leave import LeaveDetector
from ..algorithms.gather import GatherDetector
from ..algorithms.banner import BannerDetector

__all__ = [
    "LoiteringDetector",
    "LeaveDetector",
    "GatherDetector",
    "BannerDetector"
]
