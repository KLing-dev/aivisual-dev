"""
离岗检测视频处理模块
处理离岗检测的视频处理逻辑
"""

from typing import Optional, List, Tuple
import cv2
import numpy as np
from datetime import datetime
from ..video_processing.core import VideoProcessorCore
from ..video_processing.utils import draw_roi, draw_detection_box, put_text
from .detector import LeaveDetector

# 中文显示支持
try:
    from PIL import Image, ImageDraw, ImageFont

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def process_leave_video(
        model_path: str,
        video_path: str,
        output_path: str,
        roi: Optional[List[Tuple[int, int]]] = None,
        absence_threshold: int = 5,
        device: str = 'cuda'
) -> str:
    """
    处理离岗检测视频

    Args:
        model_path: 模型路径
        video_path: 输入视频路径
        output_path: 输出视频路径
        roi: ROI区域 [(x1, y1), (x2, y2), ...]
        absence_threshold: 脱岗判定阈值（秒）
        device: 运行设备

    Returns:
        str: 处理后的视频路径
    """
    # 默认ROI区域
    if roi is None:
        roi = [(600, 100), (1000, 100), (1000, 700), (600, 700)]

    # 初始化检测器
    detector = LeaveDetector(model_path=model_path, device=device)

    # 初始化核心处理器
    core = VideoProcessorCore(model_path)

    # 打开视频文件
    cap = core.open_video_capture(video_path)

    # 获取视频参数
    fps, width, height = core.get_video_properties(cap)

    # 初始化视频写入器
    out = core.create_video_writer(output_path, fps, width, height)

    # 状态变量
    absence_start_time = None
    alert_triggered = False

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        frame_time = frame_count / fps

        # 直接在原始帧上执行离岗检测，不进行缩放
        result = detector.detect_leave(frame, roi, absence_start_time, absence_threshold)
        absence_start_time = result['absence_start_time']

        # 在帧上绘制检测结果
        annotated_frame = draw_leave_detections(
            frame, roi, result['status'], result['roi_person_count'],
            absence_start_time, absence_threshold, result['alert_triggered']
        )

        # 绘制检测到的人员框
        for box in result['person_boxes']:
            annotated_frame = draw_detection_box(annotated_frame, box, (0, 255, 0), 2)

        # 写入处理后的帧
        out.write(annotated_frame)

    # 释放资源
    core.release_resources(cap, out)

    return output_path


def draw_leave_detections(frame, roi, status, person_count,
                          absence_start_time, absence_threshold, alert_triggered):
    """
    在帧上绘制离岗检测结果
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
            font_path = "C:/Windows/Fonts/simhei.ttf"  # 黑体
            font = ImageFont.truetype(font_path, 32)
            small_font = ImageFont.truetype(font_path, 24)
        except:
            try:
                font_path = "C:/Windows/Fonts/msyh.ttc"  # 微软雅黑
                font = ImageFont.truetype(font_path, 32)
                small_font = ImageFont.truetype(font_path, 24)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()

        # 绘制状态信息
        color = (0, 255, 0) if status == "在岗" else (255, 0, 0)
        draw.text((30, 30), f"状态: {status}", font=font, fill=color)

        # 绘制脱岗时长
        if absence_start_time is not None:
            absence_duration = (datetime.now() - absence_start_time).total_seconds()
            draw.text((30, 70), f"脱岗时长: {absence_duration:.1f}秒", font=small_font, fill=(255, 0, 0))

        # 绘制警报
        if alert_triggered:
            draw.text((frame.shape[1] // 2 - 150, 30), "⚠️ 警告：人员脱岗！", font=font, fill=(255, 0, 0))

        # 转换回OpenCV格式
        frame[:] = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    else:
        # 如果PIL不可用，使用英文替代
        color = (0, 255, 0) if status == "在岗" else (0, 0, 255)
        frame = put_text(frame, f"Status: {status}", (30, 50), 1, color, 2)

        if absence_start_time is not None:
            absence_duration = (datetime.now() - absence_start_time).total_seconds()
            frame = put_text(frame, f"Absence: {absence_duration:.1f}s", (30, 100), 1, (0, 0, 255), 2)

        if alert_triggered:
            frame = put_text(frame, "WARNING: Person Left!", (frame.shape[1] // 2 - 150, 50), 1.5, (0, 0, 255), 3)

    return frame
