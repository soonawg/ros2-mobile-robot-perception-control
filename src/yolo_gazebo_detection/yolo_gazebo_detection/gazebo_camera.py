#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
import cv2
from cv_bridge import CvBridge

class GazeboCamera(Node):
    def __init__(self):
        super().__init__('gazebo_camera')
        
        self.bridge = CvBridge()
        
        # 카메라 이미지 구독
        self.camera_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.camera_callback,
            10
        )
        
        # 카메라 상태 발행
        self.status_pub = self.create_publisher(
            String,
            '/camera_status',
            10
        )
        
        self.get_logger().info('Gazebo Camera 노드가 시작되었습니다.')
        
    def camera_callback(self, msg):
        try:
            # 이미지 수신 확인
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            # 상태 메시지 발행
            status_msg = String()
            status_msg.data = f"카메라 이미지 수신: {cv_image.shape[1]}x{cv_image.shape[0]}"
            self.status_pub.publish(status_msg)
            
        except Exception as e:
            self.get_logger().error(f'카메라 이미지 처리 중 오류: {str(e)}')

def main(args=None):
    rclpy.init(args=args)
    camera = GazeboCamera()
    rclpy.spin(camera)
    camera.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()