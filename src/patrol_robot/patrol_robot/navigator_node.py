import rclpy
from rclpy.node import Node
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Bool
import time

# 순찰할 위치들
WAYPOINTS = [
    {'x': 0.56, 'y': -1.07, 'yaw': 0.0},    # 5 o'clock
    {'x': 3.50, 'y': -1.08, 'yaw': 1.57},   # 1 o'clock
    {'x': 3.44, 'y': 2.09, 'yaw': 3.14},    # 11 o'clock
    {'x': 0.55, 'y': 2.06, 'yaw': -1.57},   # 7 o'clock
]

class WaypointNavigator(Node):
    def __init__(self):
        super().__init__('navigator_node')

        self.navigator = BasicNavigator()
        self.object_detected = False

        self.detected_sub = self.create_subscription(
            Bool,
            '/object_detected',
            self.detected_callback,
            10
        )

        self.get_logger().info("Waiting for Nav2 lifecycle...")
        self.navigator.waitUntilNav2Active()

        self.get_logger().info("Starting patrol...")
        self.patrol_waypoints()

    def detected_callback(self, msg):
        if msg.data:
            self.get_logger().warn("Object detected! Halting patrol.")
            self.object_detected = True
            self.navigator.cancelTask()

    def patrol_waypoints(self):
        for wp in WAYPOINTS:
            if self.object_detected:
                self.get_logger().info("Patrol interrupted due to object detection.")
                break

            pose = PoseStamped()
            pose.header.frame_id = 'map'
            pose.header.stamp = self.get_clock().now().to_msg()
            pose.pose.position.x = wp['x']
            pose.pose.position.y = wp['y']
            pose.pose.position.z = 0.0

            import math
            from tf_transformations import quaternion_from_euler
            q = quaternion_from_euler(0, 0, wp['yaw'])
            pose.pose.orientation.x = q[0]
            pose.pose.orientation.y = q[1]
            pose.pose.orientation.z = q[2]
            pose.pose.orientation.w = q[3]

            self.get_logger().info(f"Navigating to waypoint: ({wp['x']:.2f}, {wp['y']:.2f})")
            self.navigator.goToPose(pose)

            while not self.navigator.isTaskComplete():
                if self.object_detected:
                    self.get_logger().info("Task cancelled due to object detection.")
                    break
                time.sleep(0.5)

            result = self.navigator.getResult()
            if result == TaskResult.SUCCEEDED:
                self.get_logger().info("Reached waypoint.")
            elif result == TaskResult.CANCELED:
                self.get_logger().warn("Navigation task was cancelled.")
                break
            elif result == TaskResult.FAILED:
                self.get_logger().error("Navigation failed.")

        self.get_logger().info("Patrol finished.")

def main(args=None):
    rclpy.init(args=args)
    node = WaypointNavigator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.navigator.lifecycleShutdown()
    rclpy.shutdown()
