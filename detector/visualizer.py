import cv2
import numpy as np


class Visualizer:
    def __init__(self, detector):
        """
        初始化可视化器
        
        Args:
            detector: LoiteringDetector实例
        """
        self.detector = detector

    def draw_detections(self, frame, detections, alarms):
        """
        在帧上绘制检测结果和警报
        
        Args:
            frame: 视频帧
            detections: 检测结果
            alarms: 徘徊警报
            
        Returns:
            annotated_frame: 带注释的帧
        """
        annotated_frame = frame.copy()
        
        # 绘制检测区域
        if self.detector.detection_region is not None:
            x, y, w, h = self.detector.detection_region
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
            cv2.putText(annotated_frame, "Detection Region", (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 绘制检测框
        for detection in detections:
            x1, y1, x2, y2 = map(int, detection[:4])
            confidence = detection[4]
            class_name = detection[5]
            # 获取目标ID（如果存在）
            object_id = detection[6] if len(detection) > 6 else None
            
            # 获取类别颜色
            color = self.detector.get_class_color(class_name)
            
            # 绘制边界框
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            
            # 绘制类别、置信度和ID
            if object_id is not None:
                label = f'{class_name}: {confidence:.2f} [ID: {object_id}]'
            else:
                label = f'{class_name}: {confidence:.2f}'
            
            # 获取文本尺寸以绘制背景
            (text_width, text_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(annotated_frame, (x1, y1 - text_height - baseline - 2), 
                         (x1 + text_width, y1), color, -1)
            cv2.putText(annotated_frame, label, 
                       (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # 绘制徘徊警报 - 显示所有当前有效的警报
        for obj_id, alarm in alarms.items():
            x1, y1, x2, y2 = map(int, alarm['position'][:4])
            duration = alarm['duration']
            class_name = alarm.get('class', 'person')
            
            # 绘制警报框（加粗）- 改为红色
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
            
            # 绘制警报标签
            alarm_label = f'LOITER: {duration:.1f}s [ID: {obj_id}]'
            (text_width, text_height), baseline = cv2.getTextSize(alarm_label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(annotated_frame, (x1, y1 - text_height - baseline - 2), 
                         (x1 + text_width, y1), (0, 0, 255), -1)
            cv2.putText(annotated_frame, alarm_label, 
                       (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return annotated_frame

    def draw_fps_info(self, frame, actual_fps, avg_process_time, frame_source):
        """
        在帧上绘制FPS和处理时间信息
        
        Args:
            frame: 视频帧
            actual_fps: 实际FPS
            avg_process_time: 平均处理时间
            frame_source: 帧来源（视频文件或摄像头）
            
        Returns:
            annotated_frame: 带注释的帧
        """
        annotated_frame = frame.copy()
        
        # 显示FPS信息
        cv2.putText(annotated_frame, f"Actual FPS: {actual_fps:.1f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        
        # 显示平均处理时间
        cv2.putText(annotated_frame, f"Process Time: {avg_process_time*1000:.1f}ms", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        # 显示设备信息
        cv2.putText(annotated_frame, f"Device: {self.detector.device.upper()}", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 显示检测的类别
        classes_text = "Detecting: " + ", ".join(self.detector.target_classes)
        cv2.putText(annotated_frame, classes_text, (10, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 显示当前输入源信息
        cv2.putText(annotated_frame, f"Source: {frame_source}", (10, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 显示跟踪器状态 - 修复显示逻辑
        tracker_status = "ByteTrack: ON" if self.detector.use_bytetrack and hasattr(self.detector, 'tracker') else "ByteTrack: OFF"
        cv2.putText(annotated_frame, tracker_status, (10, 180), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return annotated_frame