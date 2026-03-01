#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from visualization_msgs.msg import MarkerArray, Marker
from geometry_msgs.msg import Point
from std_msgs.msg import Header
import cv2
import numpy as np
from cv_bridge import CvBridge
from ultralytics import YOLO
import os

class YOLODetector(Node):
    def __init__(self):
        super().__init__('yolo_detector')
        
        # YOLO 모델 로드
        self.model = YOLO('yolov8n.pt')  # 또는 'yolov8s.pt', 'yolov8m.pt' 등
        
        # CV Bridge 초기화
        self.bridge = CvBridge()
        
        # 구독자 및 발행자 설정
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )
        
        self.detection_pub = self.create_publisher(
            MarkerArray,
            '/detected_objects',
            10
        )
        
        self.annotated_image_pub = self.create_publisher(
            Image,
            '/annotated_image',
            10
        )
        
        self.get_logger().info('YOLO Detector 노드가 시작되었습니다.')
        
        # 감지 설정
        self.confidence_threshold = 0.5
        self.class_names = self.model.names
        
    def image_callback(self, msg):
        try:
            # ROS 이미지를 OpenCV 형식으로 변환
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            # YOLO 추론 실행
            results = self.model(cv_image, conf=self.confidence_threshold)
            
            # 결과 처리
            self.process_detections(results, cv_image, msg.header)
            
        except Exception as e:
            self.get_logger().error(f'이미지 처리 중 오류 발생: {str(e)}')
    
    def process_detections(self, results, cv_image, header):
        marker_array = MarkerArray()
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # 바운딩 박스 좌표
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    # 클래스 및 신뢰도
                    cls = int(box.cls[0].cpu().numpy())
                    conf = float(box.conf[0].cpu().numpy())
                    class_name = self.class_names[cls]
                    
                    # 바운딩 박스 그리기
                    cv2.rectangle(cv_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # 라벨 텍스트
                    label = f'{class_name}: {conf:.2f}'
                    cv2.putText(cv_image, label, (x1, y1-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    # 3D 마커 생성 (Gazebo에서 시각화용)
                    marker = self.create_3d_marker(x1, y1, x2, y2, class_name, conf, header)
                    marker_array.markers.append(marker)
        
        # 결과 발행
        self.detection_pub.publish(marker_array)
        
        # 주석이 추가된 이미지 발행
        annotated_msg = self.bridge.cv2_to_imgmsg(cv_image, "bgr8")
        annotated_msg.header = header
        self.annotated_image_pub.publish(annotated_msg)
    
    def create_3d_marker(self, x1, y1, x2, y2, class_name, confidence, header):
        marker = Marker()
        marker.header = header
        marker.ns = "detected_objects"
        marker.id = len(header.frame_id) + hash(class_name) % 1000
        marker.type = Marker.CUBE
        marker.action = Marker.ADD
        
        # 마커 위치 (이미지 중앙)
        marker.pose.position.x = (x1 + x2) / 2.0
        marker.pose.position.y = (y1 + y2) / 2.0
        marker.pose.position.z = 0.0
        
        # 마커 크기
        marker.scale.x = float(x2 - x1)
        marker.scale.y = float(y2 - y1)
        marker.scale.z = 1.0
        
        # 마커 색상 (신뢰도에 따라)
        alpha = confidence
        marker.color.r = 0.0
        marker.color.g = 1.0
        marker.color.b = 0.0
        marker.color.a = alpha
        
        return marker

def main(args=None):
    rclpy.init(args=args)
    detector = YOLODetector()
    rclpy.spin(detector)
    detector.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()