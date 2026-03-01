# fsm_node.py (WSL2에서 실행)
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import socket
import threading

class FSMController(Node):
    def __init__(self):
        super().__init__('fsm_controller')
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.current_state = "STOP"

        # TCP 서버
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('0.0.0.0', 9999))
        self.sock.listen(1)
        threading.Thread(target=self.tcp_listener, daemon=True).start()

        self.timer = self.create_timer(0.1, self.publish_cmd)

    def tcp_listener(self):
        conn, _ = self.sock.accept()
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                msg = data.decode().strip()
                self.get_logger().info(f"Command received: {msg}")
                if msg in ["FORWARD", "ROTATE", "BACK", "STOP"]:
                    self.current_state = msg

    def publish_cmd(self):
        twist = Twist()
        if self.current_state == "FORWARD":
            twist.linear.x = 0.2
        elif self.current_state == "ROTATE":
            twist.angular.z = 0.5
        elif self.current_state == "BACK":
            twist.linear.x = -0.2
        elif self.current_state == "STOP":
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        self.cmd_pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = FSMController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
