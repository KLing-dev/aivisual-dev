"""
视频处理核心模块
提供统一的视频处理接口和协调各类检测算法执行
"""

import cv2
import numpy as np
import os
from typing import Optional, List, Tuple
from datetime import datetime


class VideoProcessorCore:
    """
    视频处理核心类，负责协调各种检测任务的执行流程
    """

    def __init__(self, model_path: str = "yolov12/yolov12n.pt"):
        """
        初始化视频处理器核心

        Args:
            model_path: 模型路径
        """
        self.model_path = model_path

    def open_video_capture(self, video_path: str):
        """
        打开视频文件

        Args:
            video_path: 视频文件路径

        Returns:
            cv2.VideoCapture: 视频捕获对象

        Raises:
            Exception: 无法打开视频文件时抛出异常
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception(f"无法打开视频文件: {video_path}")
        return cap

    def get_video_properties(self, cap: cv2.VideoCapture) -> Tuple[int, int, int]:
        """
        获取视频属性

        Args:
            cap: 视频捕获对象

        Returns:
            Tuple[int, int, int]: (fps, width, height)
        """
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return fps, width, height

    def create_video_writer(self, output_path: str, fps: int, width: int, height: int):
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
        return cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    def release_resources(self, cap: cv2.VideoCapture, out: Optional[cv2.VideoWriter] = None):
        """
        释放资源

        Args:
            cap: 视频捕获对象
            out: 视频写入器对象（可选）
        """
        if cap:
            cap.release()
        if out:
            out.release()
