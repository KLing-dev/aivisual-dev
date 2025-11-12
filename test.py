import time
import torch
import numpy as np
import os
import sys

# 添加对YOLOv12路径的支持
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'yolov12'))

try:
    from ultralytics import YOLO
    print("Successfully imported Ultralytics library from YOLOv12")
except ImportError as e:
    try:
        # 如果失败，尝试使用系统安装的ultralytics
        import sys
        # 移除yolov12路径以避免冲突
        yolov12_path = os.path.join(os.path.dirname(__file__), 'yolov12')
        if yolov12_path in sys.path:
            sys.path.remove(yolov12_path)
        from ultralytics import YOLO
        print("Successfully imported Ultralytics library from system")
    except ImportError as e:
        print("Error importing Ultralytics library:", e)
        print("Please install required dependencies with: pip install ultralytics")
        exit(1)


def benchmark_yolov12(model_path, imgsz=640, num_runs=100):
    # 加载模型
    model = YOLO(model_path)

    # 设置检测类别（示例）
    if hasattr(model, 'set_classes'):
        model.set_classes(["person", "car", "truck"])

    # 创建一个示例图像
    dummy_image = torch.randn(1, 3, imgsz, imgsz)

    # 预热GPU
    for _ in range(10):
        _ = model(dummy_image)

    # 开始计时
    start_time = time.time()

    # 运行多次推理
    for _ in range(num_runs):
        _ = model(dummy_image)

    # 计算平均时间和FPS
    total_time = time.time() - start_time
    avg_time = total_time / num_runs
    fps = 1 / avg_time

    print(f"模型: {model_path}")
    print(f"图像尺寸: {imgsz}")
    print(f"运行次数: {num_runs}")
    print(f"平均推理时间: {avg_time * 1000:.2f} ms")
    print(f"FPS: {fps:.2f}")

    return fps, avg_time


# 运行基准测试
# 修复FutureWarning: In the future `np.object` will be defined as the corresponding NumPy scalar.
# 使用更安全的方法处理NumPy版本兼容性
try:
    np.object
except AttributeError:
    np.object = object

benchmark_yolov12('yolov12/yolov12m.pt')