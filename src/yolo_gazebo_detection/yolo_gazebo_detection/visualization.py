#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from visualization_msgs.msg import MarkerArray, Marker
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
import numpy as np

class VisualizationNode(Node):
    def __init__(self):
        super().__init__('visualization')
        
        self.bridge = CvBridge()
        
        # 구독자 설정
        self.detection_sub = self.create_subscription(
            MarkerArray,
            '/detected_objects',
            self.detection_callback,
            10
        )
        
        self.image_sub = self.create_subscription(
            Image,
            '/annotated_image',
            self.image_callback,
            10
        )
        
        # 상태 발행
        self.status_pub = self.create_publisher(
            String,
            '/detection_status',
            10
        )
        
        self.get_logger().info('Visualization 노드가 시작되었습니다.')
        
    def detection_callback(self, msg):
        # 감지된 객체 수 계산
        num_objects = len(msg.markers)
        
        status_msg = String()
        status_msg.data = f"감지된 객체 수: {num_objects}"
        self.status_pub.publish(status_msg)
        
        self.get_logger().info(f'감지된 객체: {num_objects}개')
        
    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            # 이미지 크기 조정 (선택사항)
            height, width = cv_image.shape[:2]
            if width > 800:
                scale = 800 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                cv_image = cv2.resize(cv_image, (new_width, new_height))
            
            # OpenCV 창에 표시
            cv2.imshow('YOLO Detection', cv_image)
            cv2.waitKey(1)
            
        except Exception as e:
            self.get_logger().error(f'이미지 표시 중 오류: {str(e)}')

def main(args=None):
    rclpy.init(args=args)
    viz = VisualizationNode()
    rclpy.spin(viz)
    viz.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()