"""
离岗检测算法模块
"""

from .detector import LeaveDetector
from .processor import process_leave_video

__all__ = ["LeaveDetector", "process_leave_video"]
