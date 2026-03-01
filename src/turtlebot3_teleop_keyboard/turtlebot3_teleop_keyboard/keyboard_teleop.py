import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys, select, termios, tty

# 키 맵핑 설정
move_bindings = {
    'w': (1.0, 0.0),
    's': (-1.0, 0.0),
    'a': (0.0, 1.0),
    'd': (0.0, -1.0),
    'x': (0.0, 0.0)  # 정지
}

settings = None

# 키 입력 처리 함수
def get_key():
    tty.setraw(sys.stdin.fileno())
    select.select([sys.stdin], [], [], 0)
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

# 노드 클래스
class KeyboardTeleopNode(Node):
    def __init__(self):
        super().__init__('keyboard_teleop')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.linear_speed = 0.2
        self.angular_speed = 1.0
        self.get_logger().info('키보드로 W A S D 제어 시작 (x : 정지 / Ctrl+C : 종료)')

    def run(self):
        try:
            while True:
                key = get_key()
                twist = Twist()
                if key in move_bindings:
                    linear, angular = move_bindings[key]
                    twist.linear.x = linear * self.linear_speed
                    twist.angular.z = angular * self.angular_speed
                    self.publisher.publish(twist)
                elif key == '\x03':  # Ctrl+C
                    break
        except KeyboardInterrupt:
            pass
        finally:
            twist = Twist()  # 종료 시 정지 명령
            self.publisher.publish(twist)
            self.destroy_node()
            rclpy.shutdown()

def main():
    """ROS2 엔트리포인트 함수."""
    global settings
    settings = termios.tcgetattr(sys.stdin)
    rclpy.init()
    node = KeyboardTeleopNode()
    node.run()

if __name__ == '__main__':
    main()