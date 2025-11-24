import React, { useState } from 'react';
import { FileUploader, DetectionControls, TaskMonitor } from '../../components';
import './Detection.css';

const DetectionPage = () => {
  // 文件上传状态
  const [fileId, setFileId] = useState('');
  const [taskId, setTaskId] = useState('');

  // 处理文件上传完成事件
  const handleFileUploaded = (fileId) => {
    setFileId(fileId);
  };

  // 处理开始检测事件
  const handleStartDetection = async (params) => {
    if (!fileId) {
      alert('请先上传文件并获取文件ID');
      return;
    }

    try {
      // 根据检测类型添加相应的参数
      let url = `http://localhost:8000/process_video/?file_id=${fileId}`;

      // 添加检测类型参数
      if (params.detection_type) {
        url += `&detection_type=${params.detection_type}`;
      }

      // 根据检测类型添加相应的参数
      if (params.detection_type === 'loitering') {
        url += `&detect_loitering=true`;
        if (params.loitering_time_threshold) {
          url += `&loitering_time_threshold=${params.loitering_time_threshold}`;
        }
      } else if (params.detection_type === 'gather') {
        url += `&detect_loitering=false`;
        if (params.gather_threshold) {
          url += `&gather_threshold=${params.gather_threshold}`;
        }
        if (params.gather_roi) {
          // URL编码ROI参数
          url += `&gather_roi=${encodeURIComponent(params.gather_roi)}`;
        }
      } else if (params.detection_type === 'leave') {
        url += `&detect_loitering=false`;
        if (params.leave_threshold) {
          url += `&leave_threshold=${params.leave_threshold}`;
        }
      } else if (params.detection_type === 'banner') {
        url += `&detect_loitering=false`;
        if (params.banner_conf_threshold) {
          url += `&banner_conf_threshold=${params.banner_conf_threshold}`;
        }
        if (params.banner_iou_threshold) {
          url += `&banner_iou_threshold=${params.banner_iou_threshold}`;
        }
      }

      const response = await fetch(url, {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setTaskId(data.task_id);
    } catch (error) {
      alert('处理启动失败: ' + error.message);
    }
  };

  // 定义检测类型及其参数
  const detectionTypes = [
    {
      value: 'loitering',
      label: '徘徊检测',
      parameters: [
        {
          name: 'loitering_time_threshold',
          label: '徘徊时间阈值',
          type: 'number',
          default: 20,
          min: 1,
          unit: '秒'
        }
      ]
    },
    {
      value: 'gather',
      label: '聚集检测',
      parameters: [
        {
          name: 'gather_threshold',
          label: '聚集人数阈值',
          type: 'number',
          default: 5,
          min: 1,
          unit: '人'
        },
        {
          name: 'gather_roi',
          label: '聚集检测区域',
          type: 'text',
          default: '[(220,300),(700,300),(700,700),(200,700)]',
          placeholder: '格式: [(x1,y1),(x2,y2),(x3,y3),(x4,y4)]'
        }
      ]
    },
    {
      value: 'leave',
      label: '离岗检测',
      parameters: [
        {
          name: 'leave_threshold',
          label: '离岗时间阈值',
          type: 'number',
          default: 5,
          min: 1,
          unit: '秒'
        }
      ]
    },
    {
      value: 'banner',
      label: '横幅检测',
      parameters: [
        {
          name: 'banner_conf_threshold',
          label: '置信度阈值',
          type: 'number',
          default: 0.5,
          min: 0.1,
          max: 1.0,
          step: 0.1,
          unit: ''
        },
        {
          name: 'banner_iou_threshold',
          label: 'IoU阈值',
          type: 'number',
          default: 0.45,
          min: 0.1,
          max: 1.0,
          step: 0.1,
          unit: ''
        }
      ]
    }
  ];

  return (
    <div className="detection-page">
      <h1>视频检测</h1>

      {/* 视频上传部分 */}
      <section className="upload-section">
        <h2>视频上传</h2>
        <FileUploader
          onFileUploaded={handleFileUploaded}
          uploadEndpoint="http://localhost:8000/upload/"
          allowedTypes="video/*"
        />
      </section>

      {/* 检测控制部分 */}
      <section className="detection-section">
        <h2>检测控制</h2>
        <DetectionControls
          onStartDetection={handleStartDetection}
          detectionTypes={detectionTypes}
        />
      </section>

      {/* 任务状态部分 */}
      <section className="status-section">
        <h2>任务状态</h2>
        <TaskMonitor
          taskId={taskId}
          statusEndpoint="http://localhost:8000/task_status"
          downloadEndpoint="http://localhost:8000/download_processed"
        />
      </section>

    </div>
  );
};

export default DetectionPage;
