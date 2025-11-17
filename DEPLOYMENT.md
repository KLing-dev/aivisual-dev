# 部署说明

本项目采用 React + FastAPI 的前后端分离架构，并支持 Docker 容器化部署。

## 项目结构

```
project/
├── api/                      # FastAPI 后端服务
│   ├── algorithms/           # 核心算法模块
│   │   ├── __init__.py
│   │   ├── core.py
│   │   ├── loitering_detection.py
│   │   ├── leave_detection.py
│   │   ├── gather_detection.py
│   │   └── video_processor.py
│   ├── config/              # 配置文件
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── models/              # 模型管理
│   │   ├── __init__.py
│   │   └── yolo_models.py
│   ├── routes/              # API路由
│   │   ├── __init__.py
│   │   ├── file_routes.py
│   │   └── task_routes.py
│   ├── core/                # 核心业务逻辑
│   ├── utils/               # 工具函数
│   ├── uploads/             # 上传文件目录
│   ├── processed_videos/    # 处理后视频目录
│   └── cv_api.py            # FastAPI 主服务
├── frontend/                # React 前端应用
│   ├── public/              # 静态资源
│   ├── src/                 # 源代码
│   │   ├── components/      # 公共组件（可复用）
│   │   ├── pages/           # 页面组件
│   │   │   ├── Home.js      # 首页
│   │   │   ├── Upload/      # 上传页面
│   │   │   │   ├── index.js
│   │   │   │   └── VideoUpload.js
│   │   │   ├── Detect/      # 检测页面
│   │   │   │   ├── index.js
│   │   │   │   └── DetectionControl.js
│   │   │   ├── Status/      # 状态页面
│   │   │   │   ├── index.js
│   │   │   │   └── TaskStatus.js
│   │   ├── routes/          # 前端路由配置
│   │   │   └── index.js     # 路由定义
│   │   ├── App.js           # 主应用组件
│   │   ├── App.css          # 样式
│   │   └── index.js         # 入口文件
│   └── package.json         # 前端依赖配置
├── yolov12/                 # YOLOv12 模型文件
├── Dockerfile.backend       # 后端 Docker 配置
├── Dockerfile.frontend      # 前端 Docker 配置
├── docker-compose.yml       # Docker 容器编排配置
└── requirements.txt         # Python 依赖
```

## 本地开发部署

### 环境要求

- Python 3.8+
- Node.js 14+
- Docker & Docker Compose (可选，用于容器化部署)

### 前端依赖安装

```bash
cd frontend
npm install
```

### 后端依赖安装

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装lap库（ByteTrack需要）
pip install lap>=0.5.12

# 安装PyTorch相关库（根据你的环境选择合适的版本）
# CUDA 12.1版本
pip install torch==2.8.0+cu121 torchvision==0.13.0+cu121 torchaudio==2.0.0+cu121 --extra-index-url https://download.pytorch.org/whl/cu121

# CPU版本
pip install torch==2.8.0+cpu torchvision==0.13.0+cpu torchaudio==2.0.0+cpu --extra-index-url https://download.pytorch.org/whl/cpu
```

### 后端服务启动

```bash
# 启动 FastAPI 服务
uvicorn api.cv_api:app --host 0.0.0.0 --port 8000

# 或者使用 Python 直接运行
python api/cv_api.py
```

访问 `http://localhost:8000` 查看 API 文档

### 前端应用启动

```bash
cd frontend
npm start
```

访问 `http://localhost:3000` 使用前端应用

## Docker 容器化部署

### 构建和运行

使用 docker-compose 一键部署：

```bash
docker-compose up --build
```

### 访问应用

- 前端界面: http://localhost:3000
- 后端 API: http://localhost:8000

### 分别构建和运行

分别构建前后端镜像：

```bash
# 构建后端镜像
docker build -t cv-backend -f Dockerfile.backend .

# 构建前端镜像
docker build -t cv-frontend -f Dockerfile.frontend .
```

分别运行容器：

```bash
# 运行后端服务
docker run -d -p 8000:8000 --name backend cv-backend

# 运行前端应用
docker run -d -p 3000:3000 --name frontend cv-frontend
```

## 前端路由说明

前端使用 React Router 进行路由管理，包含以下路由：

1. `/` - 首页
2. `/upload` - 视频上传页面
3. `/detect` - 行为检测控制页面
4. `/status` - 任务状态查看页面

路由配置文件位于 `frontend/src/routes/index.js`，与组件分离以提高可维护性。

## 后端API接口说明

后端提供以下主要接口：

1. `POST /upload/` - 上传视频文件
2. `POST /process_video/` - 处理视频文件
3. `GET /task_status/{task_id}` - 获取任务状态
4. `GET /download_processed/{task_id}` - 下载处理后的视频

## 配置说明

### CORS 配置

后端已在 FastAPI 中配置 CORS 支持，允许所有来源访问。在生产环境中，建议修改 `api/cv_api.py` 中的 CORS 配置，指定具体的域名：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # 指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 环境变量

前端通过环境变量配置后端 API 地址，在 Docker 环境中已配置为 `http://localhost:8000`。在本地开发环境中，可以通过修改前端代码中的 API 地址来配置。

## 核心算法模块说明

所有核心算法已整合到 `api/algorithms` 目录中：

- `loitering_detection.py`: 徘徊检测算法，基于 YOLOv12 和 ByteTrack
- `leave_detection.py`: 离岗检测算法
- `gather_detection.py`: 聚集检测算法
- `video_processor.py`: 统一视频处理接口，整合所有检测功能

所有算法和模型都在后端运行，前端只负责用户界面和与后端 API 交互。