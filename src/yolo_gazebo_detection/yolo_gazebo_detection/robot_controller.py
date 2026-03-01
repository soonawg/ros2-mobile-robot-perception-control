#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import math
import random

class RobotController(Node):
    def __init__(self):
        super().__init__('robot_controller')
        
        # 발행자 설정
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )
        
        # 구독자 설정
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )
        
        # 타이머 설정 (로봇 움직임 제어)
        self.timer = self.create_timer(0.1, self.move_robot)
        
        # 로봇 상태 변수
        self.obstacle_detected = False
        self.min_distance = float('inf')
        self.target_angle = 0.0
        self.current_mode = 'explore'  # 'explore', 'avoid', 'turn'
        
        self.get_logger().info('Robot Controller 노드가 시작되었습니다.')
        
    def scan_callback(self, msg):
        # 라이다 스캔 데이터 처리
        ranges = msg.ranges
        
        # 전방 60도 범위에서 장애물 확인
        front_ranges = ranges[330:] + ranges[:30]
        valid_ranges = [r for r in front_ranges if r > 0.1 and r < 10.0]
        
        if valid_ranges:
            self.min_distance = min(valid_ranges)
            self.obstacle_detected = self.min_distance < 0.5
        else:
            self.obstacle_detected = False
            self.min_distance = float('inf')
    
    def move_robot(self):
        cmd_vel = Twist()
        
        if self.obstacle_detected:
            # 장애물 회피 모드
            self.current_mode = 'avoid'
            cmd_vel.linear.x = 0.0
            cmd_vel.angular.z = 0.5  # 왼쪽으로 회전
        else:
            # 탐색 모드
            self.current_mode = 'explore'
            cmd_vel.linear.x = 0.2  # 천천히 전진
            cmd_vel.angular.z = 0.1 * math.sin(self.get_clock().now().nanoseconds / 1e9)  # 부드러운 곡선 주행
        
        self.cmd_vel_pub.publish(cmd_vel)
        
        # 상태 로그 출력
        if self.current_mode == 'avoid':
            self.get_logger().info(f'장애물 회피 중 - 거리: {self.min_distance:.2f}m')
        else:
            self.get_logger().info(f'탐색 중 - 거리: {self.min_distance:.2f}m')

def main(args=None):
    rclpy.init(args=args)
    controller = RobotController()
    rclpy.spin(controller)
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()