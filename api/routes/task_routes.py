"""
任务管理相关路由
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import os
from api.routes.file_routes import processing_tasks
from api.config.settings import PROCESSED_DIR

router = APIRouter()

@router.get("/task_status/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    if task_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="任务未找到")

    return processing_tasks[task_id]


@router.get("/download_processed/{task_id}")
async def download_processed_video(task_id: str):
    """下载处理后的视频"""
    if task_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="任务未找到")

    task = processing_tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="任务尚未完成")

    if not task["result_path"] or not os.path.exists(task["result_path"]):
        raise HTTPException(status_code=404, detail="处理后的视频文件未找到")

    def iterfile():
        with open(task["result_path"], mode="rb") as file_like:
            yield from file_like

    return StreamingResponse(iterfile(), media_type="video/mp4")