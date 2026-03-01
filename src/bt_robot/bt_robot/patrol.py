import py_trees
import rclpy
from rclpy.node import Node
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped
from py_trees.blackboard import Blackboard
import time
from tf_transformations import quaternion_from_euler

WAYPOINTS = [
    {'x': 0.56, 'y': -1.07, 'yaw': 0.0},
    {'x': 3.50, 'y': -1.08, 'yaw': 1.57},
    {'x': 3.44, 'y': 2.09, 'yaw': 3.14},
    {'x': 0.55, 'y': 2.06, 'yaw': -1.57},
]

def create_pose(x, y, yaw, frame="map"):
    pose = PoseStamped()
    pose.header.frame_id = frame
    pose.header.stamp = rclpy.time.Time().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    q = quaternion_from_euler(0, 0, yaw)
    pose.pose.orientation.x = q[0]
    pose.pose.orientation.y = q[1]
    pose.pose.orientation.z = q[2]
    pose.pose.orientation.w = q[3]
    return pose

class Patrol(py_trees.behaviour.Behaviour):
    def __init__(self, name="Patrol"):
        super().__init__(name)
        self.node = rclpy.create_node('patrol_node')
        self.navigator = BasicNavigator()
        self.initialized = False
        self.waypoints = []

    def update(self):
        rclpy.spin_once(self.node, timeout_sec=0.1)

        blackboard = Blackboard()
        person_detected = getattr(blackboard, "person_detected", False)

        # 사람이 감지되면 순찰 중지 시도 (예비 안전장치)
        if person_detected:
            if self.navigator.isTaskActive():
                self.navigator.cancelTask()
                self.node.get_logger().warn("[Patrol] Cancelled due to person detection")
            return py_trees.common.Status.FAILURE

        # 순찰 시작
        if not self.initialized:
            self.navigator.waitUntilNav2Active()
            self.waypoints = [create_pose(**wp) for wp in WAYPOINTS]
            self.navigator.followWaypoints(self.waypoints)
            self.initialized = True
            self.node.get_logger().info("[Patrol] Waypoints sent")

        result = self.navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            self.node.get_logger().info("[Patrol] Completed all waypoints")
            self.initialized = False
            return py_trees.common.Status.SUCCESS
        elif result == TaskResult.FAILED:
            self.node.get_logger().info("[Patrol] Waypoints navigation failed")
            self.initialized = False
            return py_trees.common.Status.FAILURE
        else:
            self.node.get_logger().info("[Patrol] Moving to waypoints...")
            return py_trees.common.Status.RUNNING
