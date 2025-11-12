#!/usr/bin/env python3
"""
主程序 - 运行徘徊检测系统
"""

import time
import cv2
import argparse
from detector.core import LoiteringDetector
from detector.visualizer import Visualizer
from detector.video_source import VideoSourceManager


def main():
    """
    主函数 - 运行徘徊检测系统
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Loitering Detection System')
    parser.add_argument('--api', action='store_true', help='Run as API server')
    parser.add_argument('--port', type=int, default=8000, help='API server port')
    args = parser.parse_args()
    
    if args.api:
        # 运行 FastAPI 服务器
        run_api_server(args.port)
    else:
        # 运行本地检测系统
        run_local_detection()


def run_local_detection():
    """运行本地检测系统"""
    print("Loitering Detection System Starting...")
    print("Checking dependencies...")
    
    # 初始化视频源管理器，指定视频文件路径
    video_manager = VideoSourceManager([
        "VideoFile/bandicam 2025-10-19 14-21.mp4",
    ])
    
    # 打开视频源
    cap, source_type = video_manager.open_video_source()
    if cap is None:
        return
    
    # 获取视频属性
    fps, width, height = video_manager.get_video_properties()
    print(f"Video source: {width}x{height} @ {fps} FPS")
    
    # 初始化徘徊检测器，尝试启用ByteTrack跟踪
    detector = LoiteringDetector(
        model_path="yolov12/yolov12m.pt",
        loitering_time_threshold=15,  # 徘徊时间阈值（秒）
        target_classes=["person"],    # 检测对象类别（可以添加更多类别，如 ["person", "car", "truck"]）
        conf_threshold=0.5,           # 置信度阈值
        img_size=640,                 # 图像处理尺寸
        device='cuda',                # 使用GPU或CPU
        detection_region=None,        # 设置为 (x, y, width, height) 可指定检测区域
        use_bytetrack=True            # 启用ByteTrack跟踪器
    )
    
    # 初始化可视化器
    visualizer = Visualizer(detector)
    
    frame_count = 0
    
    print("Loitering Detection System Started")
    print("Press 'q' to quit")
    
    # 用于计算处理时间
    prev_time = time.time()
    processing_times = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("End of video or camera error")
            break
            
        frame_count += 1
        frame_time = frame_count / fps
        
        # 记录开始处理时间
        start_process_time = time.time()
        
        # 检测徘徊行为
        detections, alarms = detector.detect_loitering(frame, frame_time)
        
        # 记录处理时间
        process_time = time.time() - start_process_time
        processing_times.append(process_time)
        
        # 绘制检测结果
        annotated_frame = visualizer.draw_detections(frame, detections, alarms)
        
        # 计算并显示实际FPS
        current_time = time.time()
        actual_fps = 1 / (current_time - prev_time) if (current_time - prev_time) > 0 else 0
        prev_time = current_time
        
        # 显示FPS信息
        if processing_times:
            avg_process_time = sum(processing_times[-30:]) / min(len(processing_times), 30)
            annotated_frame = visualizer.draw_fps_info(
                annotated_frame, actual_fps, avg_process_time, 
                "Video File" if source_type == "video_file" else "Camera"
            )
        
        # 显示结果
        cv2.imshow('Loitering Detection with ByteTrack', annotated_frame)
        
        # 检查退出条件
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # 释放资源
    video_manager.release()
    cv2.destroyAllWindows()
    print("Loitering Detection System Stopped")
    
    # 显示性能统计
    if processing_times:
        avg_time = sum(processing_times) / len(processing_times)
        avg_fps = 1 / avg_time if avg_time > 0 else 0
        print(f"Average processing time: {avg_time*1000:.2f}ms")
        print(f"Average FPS: {avg_fps:.2f}")


def run_api_server(port):
    """运行 API 服务器"""
    print(f"Starting FastAPI server on port {port}...")
    try:
        import uvicorn
        from api_server import app
        uvicorn.run(app, host="0.0.0.0", port=port)
    except ImportError:
        print("Error: uvicorn not installed. Please install it with: pip install uvicorn")
    except Exception as e:
        print(f"Error starting API server: {e}")


if __name__ == "__main__":
    main()