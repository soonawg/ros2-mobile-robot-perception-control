import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import math

class ObstacleAvoidFSM(Node):

    def __init__(self):
        super().__init__('obstacle_avoid_fsm')
        self.scan_sub = self.create_subscription(
            LaserScan, 
            '/scan', 
            self.scan_callback, 
            10
        )
        self.cmd_pub = self.create_publisher(
            Twist, 
            '/cmd_vel', 
            10
        )

        self.timer = self.create_timer(0.1, self.control_loop)
        self.min_front_dist = float('inf')
        self.min_left_dist = float('inf')
        self.min_right_dist = float('inf')
        self.safe_distance = 0.8  # 80cm로 증가

    def scan_callback(self, msg):
        # 각도 기반으로 전방, 좌측, 우측 감지
        angle_increment = msg.angle_increment
        angle_min = msg.angle_min
        
        # 전방 각도 범위 (-15도 ~ +15도)
        front_start_idx = int((-15.0 - angle_min) / angle_increment)
        front_end_idx = int((15.0 - angle_min) / angle_increment)
        
        # 좌측 각도 범위 (15도 ~ 45도)
        left_start_idx = int((15.0 - angle_min) / angle_increment)
        left_end_idx = int((45.0 - angle_min) / angle_increment)
        
        # 우측 각도 범위 (-45도 ~ -15도)
        right_start_idx = int((-45.0 - angle_min) / angle_increment)
        right_end_idx = int((-15.0 - angle_min) / angle_increment)
        
        # 인덱스 범위 보정
        front_start_idx = max(0, front_start_idx)
        front_end_idx = min(len(msg.ranges) - 1, front_end_idx)
        left_start_idx = max(0, left_start_idx)
        left_end_idx = min(len(msg.ranges) - 1, left_end_idx)
        right_start_idx = max(0, right_start_idx)
        right_end_idx = min(len(msg.ranges) - 1, right_end_idx)
        
        # 각 방향의 거리 데이터 추출 및 유효성 검사
        front_ranges = msg.ranges[front_start_idx:front_end_idx + 1]
        left_ranges = msg.ranges[left_start_idx:left_end_idx + 1]
        right_ranges = msg.ranges[right_start_idx:right_end_idx + 1]
        
        # 유효한 거리 값만 필터링
        self.min_front_dist = self.get_min_valid_distance(front_ranges, msg.range_max)
        self.min_left_dist = self.get_min_valid_distance(left_ranges, msg.range_max)
        self.min_right_dist = self.get_min_valid_distance(right_ranges, msg.range_max)

    def get_min_valid_distance(self, ranges, range_max):
        """유효한 거리 값 중 최소값 반환"""
        valid_distances = []
        for distance in ranges:
            if not math.isnan(distance) and not math.isinf(distance) and distance <= range_max:
                valid_distances.append(distance)
        
        if not valid_distances:
            return float('inf')
        
        return min(valid_distances)

    def control_loop(self):
        twist = Twist()
        
        # 디버깅을 위한 로그
        self.get_logger().info(f'Front: {self.min_front_dist:.2f}m, Left: {self.min_left_dist:.2f}m, Right: {self.min_right_dist:.2f}m')

        if self.min_front_dist < self.safe_distance:
            self.get_logger().info(f'장애물 감지! ({self.min_front_dist:.2f}m) 회피 중...')
            twist.linear.x = 0.0  # 정지
            
            # 좌/우회 판단
            if self.min_left_dist > self.min_right_dist:
                twist.angular.z = 0.5  # 왼쪽 회전
                self.get_logger().info('왼쪽으로 회전')
            else:
                twist.angular.z = -0.5  # 오른쪽 회전
                self.get_logger().info('오른쪽으로 회전')
        else:
            twist.linear.x = 0.2  # 전진
            twist.angular.z = 0.0
            self.get_logger().info('전진 중')

        self.cmd_pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoidFSM()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()