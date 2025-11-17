import React, { useState } from 'react';
import axios from 'axios';
import './Detection.css';

const DetectionPage = () => {
  // 文件上传状态
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [fileId, setFileId] = useState('');
  
  // 检测控制状态
  const [detectionType, setDetectionType] = useState('loitering');
  const [loiteringTimeThreshold, setLoiteringTimeThreshold] = useState(20);
  const [gatherThreshold, setGatherThreshold] = useState(5);
  const [leaveThreshold, setLeaveThreshold] = useState(5);
  const [taskId, setTaskId] = useState('');
  const [processStatus, setProcessStatus] = useState('');
  
  // 任务状态
  const [taskStatus, setTaskStatus] = useState(null);
  const [statusMessage, setStatusMessage] = useState('');

  // 处理文件选择
  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  // 处理文件上传
  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus('请选择一个文件');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      setUploadStatus('上传中...');
      const response = await axios.post('http://localhost:8000/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setFileId(response.data.file_id);
      setUploadStatus(`上传成功! 文件ID: ${response.data.file_id}`);
    } catch (error) {
      setUploadStatus('上传失败: ' + error.message);
    }
  };

  // 开始检测
  const handleStartDetection = async () => {
    if (!fileId) {
      setProcessStatus('请先上传文件并获取文件ID');
      return;
    }

    try {
      setProcessStatus('处理中...');
      
      const params = {
        file_id: fileId,
        detection_type: detectionType
      };

      // 根据检测类型添加相应的参数
      if (detectionType === 'loitering') {
        params.loitering_time_threshold = loiteringTimeThreshold;
      } else if (detectionType === 'gather') {
        params.gather_threshold = gatherThreshold;
      } else if (detectionType === 'leave') {
        params.leave_threshold = leaveThreshold;
      }

      const response = await axios.post('http://localhost:8000/process_video/', null, { params });
      
      setTaskId(response.data.task_id);
      setProcessStatus(`处理已启动! 任务ID: ${response.data.task_id}`);
    } catch (error) {
      setProcessStatus('处理启动失败: ' + error.message);
    }
  };

  // 检查任务状态
  const handleCheckStatus = async () => {
    if (!taskId) {
      setStatusMessage('请先启动检测任务获取任务ID');
      return;
    }

    try {
      const response = await axios.get(`http://localhost:8000/task_status/${taskId}`);
      setTaskStatus(response.data);
      setStatusMessage('');
    } catch (error) {
      setStatusMessage('获取任务状态失败: ' + error.message);
      setTaskStatus(null);
    }
  };

  // 下载处理后的视频
  const handleDownload = async () => {
    if (!taskId) {
      setStatusMessage('请先启动检测任务获取任务ID');
      return;
    }

    try {
      const response = await axios.get(`http://localhost:8000/download_processed/${taskId}`, {
        responseType: 'blob'
      });
      
      // 创建下载链接
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `processed_video_${taskId}.mp4`);
      document.body.appendChild(link);
      link.click();
      
      // 清理
      link.parentNode.removeChild(link);
    } catch (error) {
      setStatusMessage('下载失败: ' + error.message);
    }
  };

  return (
    <div className="detection-page">
      <h1>视频检测</h1>
      
      {/* 视频上传部分 */}
      <section className="upload-section">
        <h2>视频上传</h2>
        <div className="upload-controls">
          <input type="file" accept="video/*" onChange={handleFileChange} />
          <button onClick={handleUpload}>上传视频</button>
          <p className="status">{uploadStatus}</p>
          {fileId && <p className="file-id">文件ID: {fileId}</p>}
        </div>
      </section>

      {/* 检测控制部分 */}
      <section className="detection-section">
        <h2>检测控制</h2>
        <div className="detection-controls">
          <div className="form-group">
            <label>
              检测类型:
              <select value={detectionType} onChange={(e) => setDetectionType(e.target.value)}>
                <option value="loitering">徘徊检测</option>
                <option value="gather">聚集检测</option>
                <option value="leave">离岗检测</option>
              </select>
            </label>
          </div>
          
          {detectionType === 'loitering' && (
            <div className="form-group">
              <label>
                徘徊时间阈值 (秒):
                <input 
                  type="number" 
                  value={loiteringTimeThreshold} 
                  onChange={(e) => setLoiteringTimeThreshold(e.target.value)} 
                  min="1"
                />
              </label>
            </div>
          )}
          
          {detectionType === 'gather' && (
            <div className="form-group">
              <label>
                聚集人数阈值:
                <input 
                  type="number" 
                  value={gatherThreshold} 
                  onChange={(e) => setGatherThreshold(e.target.value)} 
                  min="1"
                />
              </label>
            </div>
          )}
          
          {detectionType === 'leave' && (
            <div className="form-group">
              <label>
                离岗时间阈值 (秒):
                <input 
                  type="number" 
                  value={leaveThreshold} 
                  onChange={(e) => setLeaveThreshold(e.target.value)} 
                  min="1"
                />
              </label>
            </div>
          )}
          
          <button onClick={handleStartDetection}>开始检测</button>
          <p className="status">{processStatus}</p>
          {taskId && <p className="task-id">任务ID: {taskId}</p>}
        </div>
      </section>

      {/* 任务状态部分 */}
      <section className="status-section">
        <h2>任务状态</h2>
        <div className="status-controls">
          <button onClick={handleCheckStatus}>检查状态</button>
          <button onClick={handleDownload} disabled={!taskStatus || taskStatus.status !== 'completed'}>
            下载处理后的视频
          </button>
          <p className="status">{statusMessage}</p>
          
          {taskStatus && (
            <div className="task-details">
              <h3>状态详情</h3>
              <p>状态: {taskStatus.status}</p>
              {taskStatus.progress !== undefined && <p>进度: {taskStatus.progress}%</p>}
              {taskStatus.frame_count && <p>处理帧数: {taskStatus.frame_count}</p>}
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default DetectionPage;