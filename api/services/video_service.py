"""
视频处理服务层
处理视频相关的业务逻辑
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from api.config.settings import UPLOAD_DIR, PROCESSED_DIR
from api.algorithms import VideoProcessingCoordinator


class VideoService:
    """视频处理服务类"""

    def __init__(self):
        """初始化视频处理服务"""
        self.processing_tasks = {}

    def upload_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        上传文件（图像或视频）

        Args:
            file_content: 文件内容
            filename: 文件名

        Returns:
            Dict[str, Any]: 上传结果
        """
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{filename}")

        # 保存文件
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)

        return {"file_id": file_id, "filename": filename, "saved_path": file_path}

    def process_video(self,
                      file_id: str,
                      detection_type: str = "loitering",
                      camera_id: str = "default",
                      loitering_time_threshold: int = 20,
                      leave_roi: Optional[List] = None,
                      leave_threshold: Optional[int] = None,
                      gather_roi: Optional[List] = None,
                      gather_threshold: Optional[int] = None,
                      banner_roi: Optional[List] = None,
                      banner_conf_threshold: Optional[float] = None,
                      banner_iou_threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        处理视频文件

        Args:
            file_id: 文件ID
            detection_type: 检测类型
            camera_id: 摄像头ID
            loitering_time_threshold: 徘徊检测时间阈值
            leave_roi: 离岗检测ROI区域
            leave_threshold: 离岗检测阈值
            gather_roi: 聚集检测ROI区域
            gather_threshold: 聚集检测阈值
            banner_roi: 横幅检测ROI区域
            banner_conf_threshold: 横幅检测置信度阈值
            banner_iou_threshold: 横幅检测IoU阈值

        Returns:
            Dict[str, Any]: 处理结果
        """
        # 查找文件
        file_path = None
        for filename in os.listdir(UPLOAD_DIR):
            if filename.startswith(file_id):
                file_path = os.path.join(UPLOAD_DIR, filename)
                break

        if not file_path or not os.path.exists(file_path):
            raise ValueError("文件未找到")

        # 添加后台任务处理视频
        task_id = str(uuid.uuid4())
        self.processing_tasks[task_id] = {
            "status": "processing",
            "progress": 0,
            "result_path": None,
            "camera_id": camera_id,
            "detection_type": detection_type
        }

        # 根据检测类型选择不同的处理函数
        if detection_type == "leave":
            # 离岗检测
            self._process_leave_detection_task(
                file_path,
                task_id,
                leave_roi,
                leave_threshold,
                camera_id
            )
        elif detection_type == "gather":
            # 聚集检测
            self._process_gather_detection_task(
                file_path,
                task_id,
                gather_roi,
                gather_threshold,
                camera_id
            )
        elif detection_type == "banner":
            # 横幅检测
            self._process_banner_detection_task(
                file_path,
                task_id,
                banner_roi,
                banner_conf_threshold,
                banner_iou_threshold,
                camera_id
            )
        else:
            # 默认为徘徊检测
            self._process_video_task(
                file_path,
                task_id,
                True,  # detect_loitering
                loitering_time_threshold,
                camera_id
            )

        return {"task_id": task_id, "message": f"{detection_type}视频处理已启动"}

    def _process_video_task(self,
                            video_path: str,
                            task_id: str,
                            detect_loitering: bool = True,
                            loitering_time_threshold: int = 20,
                            camera_id: str = "default"):
        """后台处理视频任务"""
        try:
            # 初始化视频处理器
            processor = VideoProcessingCoordinator()

            # 设置输出视频路径
            output_filename = f"processed_{uuid.uuid4()}.mp4"
            output_path = os.path.join(PROCESSED_DIR, output_filename)

            # 处理视频
            result_path = processor.process_loitering_video(
                video_path=video_path,
                output_path=output_path,
                loitering_time_threshold=loitering_time_threshold
            )

            # 标记为完成
            self.processing_tasks[task_id]["status"] = "completed"
            self.processing_tasks[task_id]["result_path"] = result_path
            self.processing_tasks[task_id]["camera_id"] = camera_id

            # 保存报警信息（示例）
            # 在实际应用中，这里会根据检测结果生成报警信息并保存到数据库

        except Exception as e:
            self.processing_tasks[task_id]["status"] = "failed"
            self.processing_tasks[task_id]["error"] = str(e)

    def _process_leave_detection_task(self,
                                      video_path: str,
                                      task_id: str,
                                      roi: Optional[list] = None,
                                      threshold: Optional[int] = None,
                                      camera_id: str = "default"):
        """离岗检测处理任务"""
        try:
            # 初始化视频处理器
            processor = VideoProcessingCoordinator()

            # 设置输出视频路径
            output_filename = f"leave_processed_{uuid.uuid4()}.mp4"
            output_path = os.path.join(PROCESSED_DIR, output_filename)

            # 处理视频
            result_path = processor.process_leave_video(
                video_path=video_path,
                output_path=output_path,
                roi=roi,
                absence_threshold=threshold if threshold is not None else 5
            )

            # 标记为完成
            self.processing_tasks[task_id]["status"] = "completed"
            self.processing_tasks[task_id]["result_path"] = result_path
            self.processing_tasks[task_id]["camera_id"] = camera_id

        except Exception as e:
            self.processing_tasks[task_id]["status"] = "failed"
            self.processing_tasks[task_id]["error"] = str(e)

    def _process_gather_detection_task(self,
                                       video_path: str,
                                       task_id: str,
                                       roi: Optional[list] = None,
                                       threshold: Optional[int] = None,
                                       camera_id: str = "default"):
        """聚集检测处理任务"""
        try:
            # 初始化视频处理器
            processor = VideoProcessingCoordinator()

            # 设置输出视频路径
            output_filename = f"gather_processed_{uuid.uuid4()}.mp4"
            output_path = os.path.join(PROCESSED_DIR, output_filename)

            # 处理视频
            result_path = processor.process_gather_video(
                video_path=video_path,
                output_path=output_path,
                roi=roi,
                gather_threshold=threshold if threshold is not None else 5
            )

            # 标记为完成
            self.processing_tasks[task_id]["status"] = "completed"
            self.processing_tasks[task_id]["result_path"] = result_path
            self.processing_tasks[task_id]["camera_id"] = camera_id

        except Exception as e:
            self.processing_tasks[task_id]["status"] = "failed"
            self.processing_tasks[task_id]["error"] = str(e)

    def _process_banner_detection_task(self,
                                       video_path: str,
                                       task_id: str,
                                       roi: Optional[list] = None,
                                       conf_threshold: Optional[float] = None,
                                       iou_threshold: Optional[float] = None,
                                       camera_id: str = "default"):
        """横幅检测处理任务"""
        try:
            # 初始化视频处理器
            processor = VideoProcessingCoordinator()

            # 设置输出视频路径
            output_filename = f"banner_processed_{uuid.uuid4()}.mp4"
            output_path = os.path.join(PROCESSED_DIR, output_filename)

            # 处理视频
            result_path = processor.process_banner_video(
                video_path=video_path,
                output_path=output_path,
                roi=roi,
                conf_threshold=conf_threshold if conf_threshold is not None else 0.5,
                iou_threshold=iou_threshold if iou_threshold is not None else 0.45
            )

            # 标记为完成
            self.processing_tasks[task_id]["status"] = "completed"
            self.processing_tasks[task_id]["result_path"] = result_path
            self.processing_tasks[task_id]["camera_id"] = camera_id

        except Exception as e:
            self.processing_tasks[task_id]["status"] = "failed"
            self.processing_tasks[task_id]["error"] = str(e)
            print(f"横幅检测处理失败: {e}")

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            Dict[str, Any]: 任务状态
        """
        if task_id not in self.processing_tasks:
            raise ValueError("任务未找到")

        return self.processing_tasks[task_id]
