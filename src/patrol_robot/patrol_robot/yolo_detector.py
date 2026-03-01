#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Bool
from cv_bridge import CvBridge
from ultralytics import YOLO
from geometry_msgs.msg import Point
import cv2
import numpy as np


# 센서 이미지 구독: /camera/image_raw
# YOLOv8로 객체 탐지
# 사람이 탐지되면 → /object_detected에 std_msgs/Bool(data=True) 발행
# 해당 객체의 중심 픽셀 좌표를 /object_center에 geometry_msgs/Point로 발행



class YoloV8PersonDetector(Node):
    def __init__(self):
        super().__init__('yolo_v8_detector')
        self.bridge = CvBridge()

        # YOLOv8 모델 로드
        self.model = YOLO('/home/hpmcsg1wl7/exc_ws/yolov8m.pt')

        # 이미지 구독
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # 물체 감지 여부 publish
        self.detected_pub = self.create_publisher(Bool, '/object_detected', 10)

        # 객체 중심 위치 publish (픽셀 좌표 기준)
        self.center_pub = self.create_publisher(Point, '/object_center', 10)

        self.get_logger().info("YOLOv8 Person Detector Node initialized")
    
    def image_callback(self, msg):
        # ROS Image -> CV Image
        frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        results = self.model(frame)[0]

        found = False
        for result in results.boxes:
            cls_id = int(result.cls.item())
            class_name = self.model.names[cls_id]

            if class_name == "person":
                found = True

                # 중심 좌표 계산
                x1, y1, x2, y2 = map(int, result.xyxy[0])
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                # 중심 좌표 publish
                point = Point()
                point.x = float(cx)
                point.y = float(cy)
                point.z = 0.0
                self.center_pub.publish(point)

                break  # 하나 찾으면 중단
        
        # 감지 여부 publish
        self.detected_pub.publish(Bool(data=found))

def main(args=None):
    rclpy.init(args=args)
    node = YoloV8PersonDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()