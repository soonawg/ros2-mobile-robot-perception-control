import py_trees
import rclpy
from sensor_msgs.msg import BatteryState

class CheckBattery(py_trees.behaviour.Behaviour):
    def __init__(self, name="CheckBattery"):
        super().__init__(name)
        self.battery_percentage = 1.0  # Default to full battery
        self.node = rclpy.create_node('check_battery_node')
        self.sub = self.node.create_subscription(
            BatteryState,
            '/battery_state',
            self.battery_callback,
            10
        )
    
    def battery_callback(self, msg):
        self.battery_percentage = msg.percentage
    
    def update(self):
        rclpy.spin_once(self.node, timeout_sec=0.1)

        if self.battery_percentage is None:
            self.node.get_logger().warn("No battery data received yet")
            return py_trees.common.Status.RUNNING

        self.node.get_logger().info(f"[Battery] Current: {self.battery_percentage * 100:.1f}%")
        if self.battery_percentage < 0.3:
            self.node.get_logger().warn("[Battery] Battery low! (FAILURE)")
            return py_trees.common.Status.FAILURE
        else:
            self.node.get_logger().info("[Battery] Battery OK! (RUNNING)")
            return py_trees.common.Status.RUNNING