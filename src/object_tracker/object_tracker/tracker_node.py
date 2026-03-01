import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist

FORWARD_SPEED = 0.15
TURN_SPEED = 0.3

class TrackerNode(Node):
    """
    물체 방향에 따라 이동 명령을 내리는 노드.
    """

    def __init__(self):
        super().__init__('tracker_node')
        self.subscription = self.create_subscription(
            String,
            '/object_direction',
            self.direction_callback,
            10
        )
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.current_direction = "NONE"
        self.state = "SEARCH"  # SEARCH, FORWARD, STOP

        self.timer = self.create_timer(0.1, self.control_loop)

    def direction_callback(self, msg):
        """YOLO 방향 결과 콜백."""
        self.current_direction = msg.data

    def control_loop(self):
        """상태에 따라 로봇 이동 제어."""
        twist = Twist()

        if self.state == "SEARCH":
            if self.current_direction == "CENTER":
                self.state = "FORWARD"
            else:
                # 물체 없으면 천천히 회전
                twist.angular.z = TURN_SPEED
        elif self.state == "FORWARD":
            if self.current_direction == "CENTER":
                twist.linear.x = FORWARD_SPEED
            elif self.current_direction == "NONE":
                self.state = "SEARCH"
                twist.angular.z = TURN_SPEED
            else:
                # 물체가 좌/우로 치우치면 정지 후 탐색
                self.state = "STOP"
        elif self.state == "STOP":
            # 정지 후 다시 탐색
            twist = Twist()
            self.state = "SEARCH"

        self.publisher_.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = TrackerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()