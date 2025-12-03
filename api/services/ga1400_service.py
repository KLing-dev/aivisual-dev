"""
GA/T 1400 公安视频图像信息应用系统标准接口实现
"""

from typing import List, Dict, Any, Optional
import json
import uuid
from datetime import datetime
from .camera_service import CameraService
from .video_service import VideoService


class GA1400Service:
    """
    GA/T 1400标准服务实现类
    实现公安视频图像信息应用系统的标准接口
    """

    def __init__(self):
        """初始化GA1400服务"""
        self.camera_service = CameraService()
        self.video_service = VideoService()

    def register_device(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        设备注册接口 (GA/T 1400 标准接口)

        Args:
            device_info: 设备信息

        Returns:
            Dict[str, Any]: 注册结果
        """
        try:
            # 提取设备信息
            device_id = device_info.get("device_id", str(uuid.uuid4()))
            device_name = device_info.get("device_name", "")
            device_type = device_info.get("device_type", "camera")
            location = device_info.get("location", "")

            # 添加摄像头到系统中
            result = self.camera_service.add_camera(device_id, device_name, location)

            return {
                "status": "success",
                "device_id": device_id,
                "message": "设备注册成功",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"设备注册失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def unregister_device(self, device_id: str) -> Dict[str, Any]:
        """
        设备注销接口 (GA/T 1400 标准接口)

        Args:
            device_id: 设备ID

        Returns:
            Dict[str, Any]: 注销结果
        """
        try:
            # 从系统中删除摄像头
            result = self.camera_service.remove_camera(device_id)

            return {
                "status": "success",
                "device_id": device_id,
                "message": "设备注销成功",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "device_id": device_id,
                "message": f"设备注销失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def keepalive_device(self, device_id: str) -> Dict[str, Any]:
        """
        设备保活接口 (GA/T 1400 标准接口)

        Args:
            device_id: 设备ID

        Returns:
            Dict[str, Any]: 保活结果
        """
        try:
            # 检查设备是否存在
            cameras = self.camera_service.get_all_cameras()
            device_exists = any(cam["id"] == device_id for cam in cameras)

            if not device_exists:
                raise ValueError("设备不存在")

            return {
                "status": "success",
                "device_id": device_id,
                "message": "设备保活成功",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "device_id": device_id,
                "message": f"设备保活失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def sync_device_time(self, device_id: str, time_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        时间同步接口 (GA/T 1400 标准接口)

        Args:
            device_id: 设备ID
            time_info: 时间信息

        Returns:
            Dict[str, Any]: 时间同步结果
        """
        try:
            # 检查设备是否存在
            cameras = self.camera_service.get_all_cameras()
            device_exists = any(cam["id"] == device_id for cam in cameras)

            if not device_exists:
                raise ValueError("设备不存在")

            # 获取系统当前时间
            system_time = datetime.now()

            return {
                "status": "success",
                "device_id": device_id,
                "system_time": system_time.isoformat(),
                "message": "时间同步成功",
                "timestamp": system_time.isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "device_id": device_id,
                "message": f"时间同步失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def get_device_list(self, query_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        数据采集接口 - 获取设备列表 (GA/T 1400 标准接口)

        Args:
            query_params: 查询参数

        Returns:
            Dict[str, Any]: 设备列表
        """
        try:
            # 获取所有摄像头
            cameras = self.camera_service.get_all_cameras()

            # 根据查询参数过滤
            if query_params:
                # 可以根据场景类型、位置等条件过滤
                scene_type = query_params.get("scene_type")
                if scene_type:
                    filtered_cameras = []
                    for camera in cameras:
                        try:
                            camera_scene = self.camera_service.get_camera_scene(camera["id"])
                            if camera_scene.get("scene_type") == scene_type:
                                filtered_cameras.append(camera)
                        except:
                            # 如果摄像头未分配场景，则跳过
                            pass
                    cameras = filtered_cameras

            return {
                "status": "success",
                "devices": cameras,
                "total_count": len(cameras),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"获取设备列表失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def subscribe_notifications(self, subscription_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        订阅通知接口 (GA/T 1400 标准接口)

        Args:
            subscription_info: 订阅信息

        Returns:
            Dict[str, Any]: 订阅结果
        """
        try:
            subscription_id = str(uuid.uuid4())
            # 在实际应用中，这里应该保存订阅信息到数据库

            return {
                "status": "success",
                "subscription_id": subscription_id,
                "message": "订阅成功",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"订阅失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def report_alarm(self, alarm_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        报警上报接口 (GA/T 1400 标准接口)

        Args:
            alarm_info: 报警信息

        Returns:
            Dict[str, Any]: 上报结果
        """
        try:
            # 验证报警信息
            required_fields = ["device_id", "scene_type", "timestamp"]
            for field in required_fields:
                if field not in alarm_info:
                    raise ValueError(f"缺少必要字段: {field}")

            # 生成报警ID
            alarm_id = str(uuid.uuid4())

            # 在实际应用中，这里应该保存报警信息到数据库

            return {
                "status": "success",
                "alarm_id": alarm_id,
                "message": "报警信息上报成功",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"报警信息上报失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def query_alarm_data(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        查询报警数据接口 (GA/T 1400 标准接口)

        Args:
            query_params: 查询参数，应包含:
                - device_ids: 设备ID列表
                - scene_type: 场景类型
                - start_time: 开始时间
                - end_time: 结束时间

        Returns:
            Dict[str, Any]: 查询结果
        """
        try:
            # 提取查询参数
            device_ids = query_params.get("device_ids", [])
            scene_type = query_params.get("scene_type")
            start_time = query_params.get("start_time")
            end_time = query_params.get("end_time")

            # 构造查询条件
            query_conditions = {
                "camera_ids": device_ids,
                "scene_type": scene_type,
                "start_time": start_time,
                "end_time": end_time
            }

            # 在实际应用中，这里应该从数据库查询报警数据
            # 模拟返回数据
            alarms = []

            return {
                "status": "success",
                "alarms": alarms,
                "total_count": len(alarms),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"查询报警数据失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """
        获取设备状态接口 (GA/T 1400 扩展接口)

        Args:
            device_id: 设备ID

        Returns:
            Dict[str, Any]: 设备状态信息
        """
        try:
            # 获取摄像头信息
            cameras = self.camera_service.get_all_cameras()
            camera = next((cam for cam in cameras if cam["id"] == device_id), None)

            if not camera:
                raise ValueError("设备不存在")

            # 获取场景信息
            try:
                scene_info = self.camera_service.get_camera_scene(device_id)
            except:
                scene_info = {"scene_type": "unknown"}

            # 获取设备绑定信息
            try:
                device_info = self.camera_service.get_camera_device(device_id)
            except:
                device_info = {"device_source": "unknown"}

            return {
                "status": "success",
                "device_id": device_id,
                "device_info": camera,
                "scene_info": scene_info,
                "device_binding": device_info,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "device_id": device_id,
                "message": f"获取设备状态失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
