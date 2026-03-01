import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from geometry_msgs.msg import Point, Twist
from sensor_msgs.msg import Image
from playsound import playsound
import threading

# /object_detected가 True일 때만 작동
# /object_center에서 받은 픽셀 좌표를 사용해서
# 카메라의 중심 기준으로 객체 방향을 추정하고
# 해당 방향으로 로봇을 직진 이동
# 객체와 일정 거리(예: 0.8m 이하)로 가까워지면 정지
# 경고음 송출 (예: playsound 사용)
# 💡 실제 좌표 변환은 안 쓰고, 픽셀 위치만으로 단순 회전 + 직진 방식으로 시뮬레이션용으로 설계

class ObjectTracker(Node):
    def __init__(self):
        super().__init__('object_tracker')
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.sub_detected = self.create_subscription(
            Bool,
            '/object_detected',
            self.detected_callback,
            10
        )

        self.sub_center = self.create_subscription(
            Point,
            '/object_center',
            self.center_callback,
            10
        )

        self.sub_scan = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.object_detected = False
        self.latest_center = None
        self.closest_distance = float('inf')

        self.timer = self.create_timer(0.1, self.track_object)

        self.get_logger().info("Object Tracker Node Started")
    
    def detected_callback(self, msg):
        self.object_detected = msg.data
    
    def center_callback(self, msg):
        self.latest_center = msg
    
    def scan_callback(self, msg):
        # 전방 10도 범위 평균 거리 계산
        center_angle = len(msg.ranges) // 2
        view_range = 10
        selected_ranges = msg.ranges[center_angle - view_range:center_angle + view_range]
        valid_ranges = [r for r in selected_ranges if r > 0.0]
        if valid_ranges:
            self.closest_distance = sum(valid_ranges) / len(valid_ranges)
        else:
            self.closest_distance = float('inf')

    def track_object(self):
        if not self.object_detected or self.latest_center is None:
            return

        if self.closest_distance < 0.8:
            self.get_logger().info("Object reached. Stopping and alerting.")

            # 정지
            stop = Twist()
            self.cmd_pub.publish(stop)

            # 경고음 (비동기로 재생)
            threading.Thread(target=playsound, args=('/home/hpmcsg1wl7/exc_ws/src/patrol_robot/audio/alert.mp3',), daemon=True).start()

            # 한번만 재생되도록 상태 초기화
            self.object_detected = False
            self.latest_center = None
            return

        # 단순 회전: 이미지 중심 기준 좌우 회전
        cx = self.latest_center.x
        image_width = 640  # 가정. 실험 환경에 맞게 수정

        error = cx - (image_width / 2)
        twist = Twist()
        twist.linear.x = 0.15  # 앞으로 전진
        twist.angular.z = -error / 200  # 좌우 조정

        self.cmd_pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = ObjectTracker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()
