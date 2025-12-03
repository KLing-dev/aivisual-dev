"""
GA/T 1400 公安视频图像信息应用系统标准接口路由
实现符合GA/T 1400标准的RESTful API接口
"""

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from ..services.ga1400_service import GA1400Service

router = APIRouter(prefix="/api/1400")

# 初始化GA1400服务
ga1400_service = GA1400Service()

@router.post("/register")
async def register_device(device_info: Dict[str, Any] = Body(...)):
    """
    设备注册接口 (GA/T 1400 标准接口)
    """
    try:
        result = ga1400_service.register_device(device_info)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/unregister")
async def unregister_device(device_info: Dict[str, Any] = Body(...)):
    """
    设备注销接口 (GA/T 1400 标准接口)
    """
    try:
        device_id = device_info.get("device_id")
        if not device_id:
            raise HTTPException(status_code=400, detail="缺少设备ID参数")

        result = ga1400_service.unregister_device(device_id)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/keepalive")
async def keepalive_device(device_info: Dict[str, Any] = Body(...)):
    """
    设备保活接口 (GA/T 1400 标准接口)
    """
    try:
        device_id = device_info.get("device_id")
        if not device_id:
            raise HTTPException(status_code=400, detail="缺少设备ID参数")

        result = ga1400_service.keepalive_device(device_id)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync_time")
async def sync_device_time(time_info: Dict[str, Any] = Body(...)):
    """
    时间同步接口 (GA/T 1400 标准接口)
    """
    try:
        device_id = time_info.get("device_id")
        if not device_id:
            raise HTTPException(status_code=400, detail="缺少设备ID参数")

        result = ga1400_service.sync_device_time(device_id, time_info)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/devices")
async def get_device_list(scene_type: Optional[str] = None):
    """
    数据采集接口 - 获取设备列表 (GA/T 1400 标准接口)
    """
    try:
        query_params = {}
        if scene_type:
            query_params["scene_type"] = scene_type

        result = ga1400_service.get_device_list(query_params)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/subscribe")
async def subscribe_notifications(subscription_info: Dict[str, Any] = Body(...)):
    """
    订阅通知接口 (GA/T 1400 标准接口)
    """
    try:
        result = ga1400_service.subscribe_notifications(subscription_info)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alarm/report")
async def report_alarm(alarm_info: Dict[str, Any] = Body(...)):
    """
    报警上报接口 (GA/T 1400 标准接口)
    """
    try:
        result = ga1400_service.report_alarm(alarm_info)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alarm/query")
async def query_alarm_data(query_params: Dict[str, Any] = Body(...)):
    """
    查询报警数据接口 (GA/T 1400 标准接口)
    """
    try:
        result = ga1400_service.query_alarm_data(query_params)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/device/status/{device_id}")
async def get_device_status(device_id: str):
    """
    获取设备状态接口 (GA/T 1400 扩展接口)
    """
    try:
        result = ga1400_service.get_device_status(device_id)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
