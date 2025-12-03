"""
视频处理核心模块
提供视频处理的基础功能
"""

import cv2
from typing import Tuple, Optional
from ...models.yolo_models import YOLOModelManager


class VideoProcessorCore:
    """视频处理核心类"""

    def __init__(self, model_name: str = "yolov12n.pt"):
        """
        初始化视频处理核心

        Args:
            model_name: 模型文件名
        """
        self.model_name = model_name
        self.model_manager = YOLOModelManager()

    def open_video_capture(self, source):
        """
        打开视频捕获源

        Args:
            source: 视频源（文件路径、摄像头索引或RTSP流地址）

        Returns:
            cv2.VideoCapture: 视频捕获对象
        """
        cap = cv2.VideoCapture(source)
        return cap

    def get_video_properties(self, cap) -> Tuple[float, int, int]:
        """
        获取视频属性

        Args:
            cap: 视频捕获对象

        Returns:
            Tuple: (fps, width, height)
        """
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return fps, width, height

    def create_video_writer(self, output_path: str, fps: float, width: int, height: int):
        """
        创建视频写入器

        Args:
            output_path: 输出视频路径
            fps: 帧率
            width: 视频宽度
            height: 视频高度

        Returns:
            cv2.VideoWriter: 视频写入器对象
        """
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        return out

    def release_resources(self, cap, out=None):
        """
        释放资源

        Args:
            cap: 视频捕获对象
            out: 视频写入器对象（可选）
        """
        if cap and cap.isOpened():
            cap.release()
        if out:
            out.release()
