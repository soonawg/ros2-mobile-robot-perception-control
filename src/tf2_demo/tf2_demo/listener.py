import rclpy
from rclpy.node import Node
from tf2_ros import Buffer, TransformListener
from rclpy.time import Time

class SimpleListener(Node):
    def __init__(self):
        super().__init__('simple_tf2_listener')
        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)
        self.timer = self.create_timer(1.0, self.lookup_tf)

    def lookup_tf(self):
        try:
            trans = self.buffer.lookup_transform('base_link', 'camera_link', Time())
            self.get_logger().info(f"Transform: {trans.transform.translation}")
        except Exception as e:
            self.get_logger().warn(f"Transform not ready: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = SimpleListener()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
