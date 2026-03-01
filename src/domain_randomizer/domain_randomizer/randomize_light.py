import rclpy
from rclpy.node import Node
from gazebo_msgs.srv import SetLightProperties
from std_msgs.msg import ColorRGBA
import random


class RandomizeLight(Node):
    def __init__(self):
        super().__init__('randomize_light')
        self.cli = self.create_client(SetLightProperties, '/gazebo/set_light_properties')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for light service...')
        self.timer = self.create_timer(5.0, self.timer_callback)

    def timer_callback(self):
        req = SetLightProperties.Request()
        req.light_name = 'sun'
        req.diffuse = ColorRGBA(
            r=random.uniform(0.4, 1.0),
            g=random.uniform(0.4, 1.0),
            b=random.uniform(0.4, 1.0),
            a=1.0
        )
        req.attenuation_constant = 0.5
        req.attenuation_linear = 0.01
        req.attenuation_quadratic = 0.001

        self.get_logger().info(f'조명 색상 설정: {req.diffuse}')
        future = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self, future)

        if future.result() is not None:
            self.get_logger().info('✅ 조명 설정 성공')
        else:
            self.get_logger().error('❌ 조명 설정 실패')


def main(args=None):
    rclpy.init(args=args)
    node = RandomizeLight()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
