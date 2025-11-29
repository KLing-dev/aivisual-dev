"""
摄像头相关路由
处理实时摄像头流和摄像头管理功能
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from typing import List, Optional
import cv2
from ..services.camera_service import CameraService
from ..algorithms import VideoProcessingCoordinator

router = APIRouter()

# 初始化摄像头服务
camera_service = CameraService()

@router.get("/cameras")
async def get_all_cameras():
    """
    获取所有摄像头列表
    """
    try:
        cameras = camera_service.get_all_cameras()
        return JSONResponse(content=cameras)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cameras/scene/{camera_id}")
async def get_camera_scene(camera_id: str):
    """
    获取指定摄像头的场景类型
    - camera_id: 摄像头ID
    """
    try:
        result = camera_service.get_camera_scene(camera_id)
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cameras/assign_scene")
async def assign_camera_to_scene(camera_id: str, scene_type: str):
    """
    将摄像头分配到指定场景
    - camera_id: 摄像头ID
    - scene_type: 场景类型 (loitering, leave, gather)
    """
    try:
        result = camera_service.assign_camera_to_scene(camera_id, scene_type)
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cameras/bind_device")
async def bind_camera_to_device(camera_id: str, device_source: str):
    """
    将摄像头绑定到设备源
    - camera_id: 摄像头ID
    - device_source: 设备源 (可以是数字如0,1,2或RTSP地址如rtsp://192.168.1.100:554/stream1)
    """
    try:
        result = camera_service.bind_camera_to_device(camera_id, device_source)
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cameras/unbind_device/{camera_id}")
async def unbind_camera_device(camera_id: str):
    """
    解除摄像头与设备的绑定
    - camera_id: 摄像头ID
    """
    try:
        result = camera_service.unbind_camera_device(camera_id)
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cameras/device/{camera_id}")
async def get_camera_device(camera_id: str):
    """
    获取摄像头绑定的设备源
    - camera_id: 摄像头ID
    """
    try:
        result = camera_service.get_camera_device(camera_id)
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cameras")
async def add_camera(camera_id: str, name: str, location: str):
    """
    添加新的摄像头
    - camera_id: 摄像头ID
    - name: 摄像头名称
    - location: 摄像头位置
    """
    try:
        result = camera_service.add_camera(camera_id, name, location)
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cameras/{camera_id}")
async def remove_camera(camera_id: str):
    """
    删除摄像头
    - camera_id: 摄像头ID
    """
    try:
        result = camera_service.remove_camera(camera_id)
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cameras/process_camera/")
async def process_camera(
        camera_id: str = "default",
        detection_type: str = "loitering",
        loitering_time_threshold: int = 20,
        leave_roi: Optional[str] = None,
        leave_threshold: Optional[int] = None,
        gather_roi: Optional[str] = None,
        gather_threshold: Optional[int] = None,
        banner_roi: Optional[str] = None,
        banner_conf_threshold: Optional[float] = None,
        banner_iou_threshold: Optional[float] = None
):
    """
    实时处理摄像头视频流
    """
    # 检查摄像头是否已分配场景
    try:
        camera_scene = camera_service.get_camera_scene(camera_id)
        expected_scene = camera_scene["scene_type"]
        if detection_type != expected_scene:
            # 可以选择是否允许用户覆盖默认场景分配
            pass  # 这里我们允许用户指定不同的检测类型
    except:
        # 摄像头未分配场景，使用默认处理
        pass

    # 解析ROI参数
    parsed_leave_roi = None
    parsed_gather_roi = None
    parsed_banner_roi = None

    if leave_roi:
        try:
            # 解析格式如: "[(600,100),(1000,100),(1000,700),(600,700)]"
            parsed_leave_roi = eval(leave_roi)
        except:
            pass

    if gather_roi:
        try:
            # 解析格式如: "[(220,300),(700,300),(700,700),(200,700)]"
            parsed_gather_roi = eval(gather_roi)
        except:
            pass

    if banner_roi:
        try:
            # 解析格式如: "[(0,0),(1280,0),(1280,720),(0,720)]"
            parsed_banner_roi = eval(banner_roi)
        except:
            pass

    # 根据检测类型选择不同的处理函数
    if detection_type == "leave":
        # 离岗检测
        return StreamingResponse(
            process_camera_leave_stream(camera_id, parsed_leave_roi, leave_threshold),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
    elif detection_type == "gather":
        # 聚集检测
        # 如果没有提供ROI，则使用默认值
        if not parsed_gather_roi:
            parsed_gather_roi = [(220, 300), (700, 300), (700, 700), (200, 700)]

        return StreamingResponse(
            process_camera_gather_stream(camera_id, parsed_gather_roi, gather_threshold),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
    elif detection_type == "banner":
        # 横幅检测
        return StreamingResponse(
            process_camera_banner_stream(camera_id, parsed_banner_roi, banner_conf_threshold, banner_iou_threshold),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
    else:
        # 默认为徘徊检测
        return StreamingResponse(
            process_camera_loitering_stream(camera_id, loitering_time_threshold),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )


def get_camera_source(camera_id: str):
    """
    获取摄像头的视频源
    """
    try:
        return camera_service.get_camera_source(camera_id)
    except:
        # 默认使用系统摄像头0
        return 0


def process_camera_loitering_stream(camera_id: str, loitering_time_threshold: int = 20):
    """处理摄像头徘徊检测视频流"""
    # 初始化视频处理器
    processor = VideoProcessingCoordinator()

    # 获取摄像头源
    camera_source = get_camera_source(camera_id)

    # 打开摄像头
    cap = cv2.VideoCapture(camera_source)
    if not cap.isOpened():
        raise HTTPException(status_code=500, detail=f"无法打开摄像头 {camera_id} (源: {camera_source})")

    try:
        # 初始化检测器
        detector = processor._get_loitering_detector(loitering_time_threshold=loitering_time_threshold)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 执行徘徊检测
            detections, alarms = detector.detect_loitering(frame, 0)  # 时间戳暂时设为0

            # 在帧上绘制检测结果
            annotated_frame = processor._draw_loitering_detections(frame, detections, alarms)

            # 编码帧
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        cap.release()


def process_camera_leave_stream(camera_id: str, roi: Optional[list] = None, threshold: Optional[int] = None):
    """处理摄像头离岗检测视频流"""
    # 初始化视频处理器
    processor = VideoProcessingCoordinator()

    # 获取摄像头源
    camera_source = get_camera_source(camera_id)

    # 打开摄像头
    cap = cv2.VideoCapture(camera_source)
    if not cap.isOpened():
        raise HTTPException(status_code=500, detail=f"无法打开摄像头 {camera_id} (源: {camera_source})")

    try:
        # 初始化检测器
        detector = processor._get_leave_detector()

        # 状态变量
        absence_start_time = None
        alert_triggered = False

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 执行离岗检测
            result = detector.detect_leave(frame, roi, absence_start_time, threshold if threshold is not None else 5)
            absence_start_time = result['absence_start_time']

            # 在帧上绘制检测结果
            annotated_frame = processor._draw_leave_detections(
                frame, roi, result['status'], result['roi_person_count'],
                absence_start_time, threshold if threshold is not None else 5, result['alert_triggered']
            )

            # 绘制检测到的人员框
            for box in result['roi_person_boxes']:  # 只绘制ROI区域内的人员框
                x1, y1, x2, y2 = box.astype(int)
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

            # 编码帧
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        cap.release()


def process_camera_gather_stream(camera_id: str, roi: Optional[list] = None, threshold: Optional[int] = None):
    """处理摄像头聚集检测视频流"""
    # 初始化视频处理器
    processor = VideoProcessingCoordinator()

    # 获取摄像头源
    camera_source = get_camera_source(camera_id)

    # 打开摄像头
    cap = cv2.VideoCapture(camera_source)
    if not cap.isOpened():
        raise HTTPException(status_code=500, detail=f"无法打开摄像头 {camera_id} (源: {camera_source})")

    try:
        # 初始化检测器
        detector = processor._get_gather_detector()

        # 设置默认ROI区域（如果没有通过参数传递）
        if roi is None:
            # 默认ROI区域可以根据您的需要修改
            roi = [(220, 300), (700, 300), (700, 700), (200, 700)]

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 执行聚集检测
            result = detector.detect_gather(frame, roi, threshold if threshold is not None else 5)

            # 在帧上绘制检测结果
            annotated_frame = processor._draw_gather_detections(
                frame, roi, result['roi_person_count'], threshold if threshold is not None else 5, result['alert_triggered']
            )

            # 绘制检测到的人员框
            for box in result['person_boxes']:
                x1, y1, x2, y2 = box.astype(int)
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

            # 编码帧
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        cap.release()


def process_camera_banner_stream(camera_id: str, roi: Optional[list] = None,
                                conf_threshold: Optional[float] = None,
                                iou_threshold: Optional[float] = None):
    """处理摄像头横幅检测视频流"""
    # 初始化视频处理器
    processor = VideoProcessingCoordinator()

    # 获取摄像头源
    camera_source = get_camera_source(camera_id)

    # 打开摄像头
    cap = cv2.VideoCapture(camera_source)
    if not cap.isOpened():
        raise HTTPException(status_code=500, detail=f"无法打开摄像头 {camera_id} (源: {camera_source})")

    try:
        # 初始化检测器
        detector = processor._get_banner_detector(
            conf_threshold=conf_threshold if conf_threshold is not None else 0.5,
            iou_threshold=iou_threshold if iou_threshold is not None else 0.45
        )

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 执行横幅检测
            results, banners = detector.detect_banner(frame)

            # 在帧上绘制检测结果
            annotated_frame = processor._draw_banner_detections(frame, banners)

            # 编码帧
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        cap.release()
