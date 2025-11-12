import cv2


class VideoSourceManager:
    def __init__(self, video_files=None):
        """
        初始化视频源管理器
        
        Args:
            video_files: 视频文件列表
        """
        self.video_files = video_files or []
        self.cap = None

    def open_video_source(self):
        """
        打开视频源（优先使用视频文件，然后是摄像头）
        
        Returns:
            cap: 视频捕获对象
            source_type: 源类型 ("video_file" 或 "camera")
        """
        # 尝试打开项目中的视频文件
        for video_file in self.video_files:
            self.cap = cv2.VideoCapture(video_file)
            if self.cap.isOpened():
                print(f"Successfully opened video file: {video_file}")
                return self.cap, "video_file"
            else:
                print(f"Could not open video file: {video_file}")
        
        # 如果没有找到视频文件，则使用摄像头
        print("No video file found, opening camera...")
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            print("Error: Could not open camera or any video file.")
            return None, None
            
        return self.cap, "camera"

    def get_video_properties(self):
        """
        获取视频属性
        
        Returns:
            fps: 帧率
            width: 宽度
            height: 高度
        """
        if not self.cap:
            return None, None, None
            
        original_fps = self.cap.get(cv2.CAP_PROP_FPS)
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = original_fps or 30.0  # 默认FPS为30
        
        return fps, width, height

    def release(self):
        """
        释放视频资源
        """
        if self.cap:
            self.cap.release()