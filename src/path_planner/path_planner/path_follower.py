# path_planner_py/path_planner_py/path_follower.py
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path
from geometry_msgs.msg import Twist, PoseStamped
import math
import tf2_ros

class PathFollower(Node):
    def __init__(self):
        super().__init__('path_follower_node')
        
        # 1. 경로 구독자
        self.path_subscription = self.create_subscription(
            Path,
            'planned_path',
            self.path_callback,
            10
        )
        
        # 2. 로봇 제어를 위한 발행자
        self.cmd_vel_publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        
        # 3. 로봇 위치를 위한 TF2 리스너
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        
        # 4. 제어 주기 타이머
        self.timer = self.create_timer(0.05, self.timer_callback) # 20Hz
        
        self.path = None
        self.current_path_index = 0
        self.get_logger().info('Path Follower Node Started.')

    def path_callback(self, msg: Path):
        self.path = msg
        self.current_path_index = 0
        self.get_logger().info(f'Received a new path with {len(self.path.poses)} points.')

    def timer_callback(self):
        if self.path is None or self.current_path_index >= len(self.path.poses):
            # 경로가 없거나 끝에 도달하면 정지
            self.stop_robot()
            return

        # 5. 로봇의 현재 위치 가져오기
        try:
            transform = self.tf_buffer.lookup_transform('map', 'base_link', rclpy.time.Time())
            robot_pose_x = transform.transform.translation.x
            robot_pose_y = transform.transform.translation.y
        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException) as e:
            self.get_logger().error(f'TF lookup failed: {e}')
            return
        
        # 6. 다음 목표 지점 설정
        target_pose = self.path.poses[self.current_path_index].pose
        target_x = target_pose.position.x
        target_y = target_pose.position.y

        # 7. 목표 지점과의 거리 계산
        distance_to_target = math.sqrt((target_x - robot_pose_x)**2 + (target_y - robot_pose_y)**2)
        
        # 8. 목표 지점에 도달했는지 확인
        if distance_to_target < 0.2: # 20cm 이내면 다음 지점으로 이동
            self.current_path_index += 1
            if self.current_path_index >= len(self.path.poses):
                self.stop_robot()
                return

        # 9. 제어 명령 생성 (P-제어기)
        cmd_vel = Twist()
        
        # 선속도 (직진)
        cmd_vel.linear.x = 0.3 # 0.3 m/s

        # 각속도 (회전)
        angle_to_target = math.atan2(target_y - robot_pose_y, target_x - robot_pose_x)
        current_yaw = self.get_yaw_from_quaternion(transform.transform.rotation)
        angle_error = angle_to_target - current_yaw
        
        # 각도 오차를 -pi ~ pi 범위로 정규화
        if angle_error > math.pi:
            angle_error -= 2 * math.pi
        elif angle_error < -math.pi:
            angle_error += 2 * math.pi
        
        cmd_vel.angular.z = 1.0 * angle_error # 간단한 P-제어기
        
        self.cmd_vel_publisher.publish(cmd_vel)
        
    def stop_robot(self):
        twist = Twist()
        self.cmd_vel_publisher.publish(twist)
        self.get_logger().info("Path finished. Robot stopped.")

    def get_yaw_from_quaternion(self, q):
        # Quaternion을 Yaw(Z축 회전) 각도로 변환
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        return math.atan2(siny_cosp, cosy_cosp)

def main(args=None):
    rclpy.init(args=args)
    path_follower = PathFollower()
    rclpy.spin(path_follower)
    path_follower.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()