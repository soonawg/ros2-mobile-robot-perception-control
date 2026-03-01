import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

class ScanSubscriber(Node):
    def __init__(self):
        super().__init__('scan_subscriber')
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.listener_callback,
            10)
        self.subscription

    def listener_callback(self, msg):
        # 중앙 각도(0도)에 해당하는 거리 출력
        center_index = len(msg.ranges) // 2
        distance = msg.ranges[center_index]
        self.get_logger().info(f'Center distance: {distance:.2f} m')

def main(args=None):
    rclpy.init(args=args)
    node = ScanSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
