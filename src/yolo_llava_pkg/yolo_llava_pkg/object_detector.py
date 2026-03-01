#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultralytics import YOLO
import cv2
import numpy as np

class ObjectDetector(Node):
    def __init__(self):
        super().__init__('object_detector')
        self.bridge = CvBridge()
        self.model = YOLO('/home/hpmcsg1wl7/exc_ws/yolov8n.pt')  # YOLOv8 nano 모델
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)
        self.bbox_pub = self.create_publisher(Image, 'detection_result', 10)
        self.crop_pub = self.create_publisher(Image, 'cropped_object', 10)
        
    def image_callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        results = self.model(cv_image)
        
        # 탐지 결과 시각화
        annotated_frame = results[0].plot()
        self.bbox_pub.publish(self.bridge.cv2_to_imgmsg(annotated_frame, 'bgr8'))
        
        # 객체 크롭 및 전송
        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            crop_img = cv_image[y1:y2, x1:x2]
            if crop_img.size > 0:
                self.crop_pub.publish(self.bridge.cv2_to_imgmsg(crop_img, 'bgr8'))

def main():
    rclpy.init()
    node = ObjectDetector()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()