"""
聚集检测视频处理模块
处理聚集检测的视频处理逻辑
"""

from typing import Optional, List, Tuple
import cv2
import numpy as np
from datetime import datetime
from ..video_processing.core import VideoProcessorCore
from ..video_processing.utils import draw_roi, draw_detection_box, put_text
from .detector import GatherDetector

# 中文显示支持
try:
    from PIL import Image, ImageDraw, ImageFont

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def process_gather_video(
        model_path: str,
        video_path: str,
        output_path: str,
        roi: Optional[List[Tuple[int, int]]] = None,
        gather_threshold: int = 5,
        device: str = 'cuda'
) -> str:
    """
    处理聚集检测视频

    Args:
        model_path: 模型路径
        video_path: 输入视频路径
        output_path: 输出视频路径
        roi: ROI区域 [(x1, y1), (x2, y2), ...]
        gather_threshold: 聚集人数阈值
        device: 运行设备

    Returns:
        str: 处理后的视频路径
    """
    # 默认ROI区域
    if roi is None:
        roi = [(220, 300), (700, 300), (700, 700), (200, 700)]

    # 初始化检测器
    detector = GatherDetector(model_path=model_path, device=device)

    # 初始化核心处理器
    core = VideoProcessorCore(model_path)

    # 打开视频文件
    cap = core.open_video_capture(video_path)

    # 获取视频参数
    fps, width, height = core.get_video_properties(cap)

    # 初始化视频写入器
    out = core.create_video_writer(output_path, fps, width, height)

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        frame_time = frame_count / fps

        # 直接在原始帧上执行聚集检测，不进行缩放
        result = detector.detect_gather(frame, roi, gather_threshold)

        # 在帧上绘制检测结果
        annotated_frame = draw_gather_detections(
            frame, roi, result['roi_person_count'], gather_threshold, result['alert_triggered']
        )

        # 绘制检测到的人员框（仅ROI区域内的人员框）
        for box in result['roi_person_boxes']:
            annotated_frame = draw_detection_box(annotated_frame, box, (0, 0, 255), 2)

        # 写入处理后的帧
        out.write(annotated_frame)

    # 释放资源
    core.release_resources(cap, out)

    return output_path


def draw_gather_detections(frame, roi, person_count, gather_threshold, alert_triggered):
    """
    在帧上绘制聚集检测结果
    """
    # 绘制ROI区域
    frame = draw_roi(frame, roi)

    # 使用PIL绘制中文文字
    if PIL_AVAILABLE:
        # 转换OpenCV图像到PIL格式
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)

        # 尝试使用系统中文字体
        try:
            # Windows系统常用中文字体
            font_path = "C:/Windows/Fonts/simhei.ttf"  # 黑体
            font = ImageFont.truetype(font_path, 32)
        except:
            try:
                # 备用字体
                font_path = "C:/Windows/Fonts/msyh.ttc"  # 微软雅黑
                font = ImageFont.truetype(font_path, 32)
            except:
                # 如果都找不到，使用默认字体
                font = ImageFont.load_default()

        # 绘制人数信息
        draw.text((30, 30), f"ROI内人数: {person_count}", font=font, fill=(255, 0, 0))

        # 绘制警报
        if alert_triggered:
            draw.text((30, 80), "警告：人员聚集！", font=font, fill=(255, 0, 0))

        # 转换回OpenCV格式
        frame[:] = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    else:
        # 如果PIL不可用，使用英文替代
        frame = put_text(frame, f"ROI Persons: {person_count}", (30, 50), 1, (255, 0, 0), 2)

        if alert_triggered:
            frame = put_text(frame, "WARNING: Crowd Detected!", (30, 100), 1.2, (0, 0, 255), 3)

    return frame
