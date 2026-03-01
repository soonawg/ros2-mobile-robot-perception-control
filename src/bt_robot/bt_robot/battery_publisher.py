import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
import time

class BatteryPublisher(Node):
    def __init__(self):
        super().__init__('battery_publisher')
        self.publisher_ = self.create_publisher(BatteryState, '/battery_state', 10)
        self.timer = self.create_timer(2.0, self.timer_callback)
        self.battery_level = 1.0  # 100%에서 시작 (0.0 ~ 1.0 범위)
        self.last_time = time.time()
        self.DECREMENT_RATE = 0.01  # 매 타이머 콜백마다 1%씩 감소
    
    def timer_callback(self):
        msg = BatteryState()
        
        # 배터리 레벨 감소 (0.0 이하로는 내려가지 않음)
        self.battery_level = max(0.0, self.battery_level - self.DECREMENT_RATE)
        
        msg.percentage = self.battery_level
        msg.voltage = 12.0 * self.battery_level  # 전압도 비례해서 감소
        msg.current = 1.0
        
        self.publisher_.publish(msg)
        self.get_logger().info(f"Battery percentage: {msg.percentage * 100:.1f}%")

def main(args=None):
    rclpy.init(args=args)
    node = BatteryPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()