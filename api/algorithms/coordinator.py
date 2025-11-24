"""
视频处理协调器
协调各种检测算法的执行流程
"""

from typing import Optional, List, Tuple
from .loitering.processor import process_loitering_video
from .leave.processor import process_leave_video
from .gather.processor import process_gather_video
from .banner.processor import process_banner_video


class VideoProcessingCoordinator:
    """
    视频处理协调器，负责协调各种检测任务的执行流程
    """

    def __init__(self, model_path: str = "yolov12/yolov12n.pt"):
        """
        初始化视频处理协调器

        Args:
            model_path: 模型路径
        """
        self.model_path = model_path

    def process_loitering_video(self,
                                video_path: str,
                                output_path: str,
                                loitering_time_threshold: int = 20,
                                device: str = 'cuda') -> str:
        """
        处理徘徊检测视频

        Args:
            video_path: 输入视频路径
            output_path: 输出视频路径
            loitering_time_threshold: 徘徊时间阈值（秒）
            device: 运行设备

        Returns:
            str: 处理后的视频路径
        """
        return process_loitering_video(
            self.model_path,
            video_path,
            output_path,
            loitering_time_threshold,
            device
        )

    def process_leave_video(self,
                            video_path: str,
                            output_path: str,
                            roi: Optional[List[Tuple[int, int]]] = None,
                            absence_threshold: int = 5,
                            device: str = 'cuda') -> str:
        """
        处理离岗检测视频

        Args:
            video_path: 输入视频路径
            output_path: 输出视频路径
            roi: ROI区域 [(x1, y1), (x2, y2), ...]
            absence_threshold: 脱岗判定阈值（秒）
            device: 运行设备

        Returns:
            str: 处理后的视频路径
        """
        return process_leave_video(
            self.model_path,
            video_path,
            output_path,
            roi,
            absence_threshold,
            device
        )

    def process_gather_video(self,
                             video_path: str,
                             output_path: str,
                             roi: Optional[List[Tuple[int, int]]] = None,
                             gather_threshold: int = 5,
                             device: str = 'cuda') -> str:
        """
        处理聚集检测视频

        Args:
            video_path: 输入视频路径
            output_path: 输出视频路径
            roi: ROI区域 [(x1, y1), (x2, y2), ...]
            gather_threshold: 聚集人数阈值
            device: 运行设备

        Returns:
            str: 处理后的视频路径
        """
        return process_gather_video(
            self.model_path,
            video_path,
            output_path,
            roi,
            gather_threshold,
            device
        )

    def process_banner_video(self,
                             video_path: str,
                             output_path: str,
                             roi: Optional[List[Tuple[int, int]]] = None,
                             conf_threshold: float = 0.3,
                             iou_threshold: float = 0.45,
                             device: str = 'cuda') -> str:
        """
        处理横幅检测视频

        Args:
            video_path: 输入视频路径
            output_path: 输出视频路径
            roi: ROI区域 [(x1, y1), (x2, y2), ...]
            conf_threshold: 置信度阈值
            iou_threshold: NMS IoU阈值
            device: 运行设备

        Returns:
            str: 处理后的视频路径
        """
        return process_banner_video(
            self.model_path,
            video_path,
            output_path,
            roi,
            conf_threshold,
            iou_threshold,
            device
        )
