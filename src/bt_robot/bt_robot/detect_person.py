import py_trees
import rclpy
from std_msgs.msg import Bool
from py_trees.blackboard import Blackboard


class DetectPerson(py_trees.behaviour.Behaviour):
    def __init__(self, name="DetectPerson"):
        super().__init__(name)
        self.person_detected = False
        self.node = rclpy.create_node('detect_person_node')

        self.sub = self.node.create_subscription(
            Bool,
            '/person_detected',
            self.callback,
            10
        )
    
    def callback(self, msg):
        self.person_detected = msg.data
    
    def update(self):
        rclpy.spin_once(self.node, timeout_sec=0.1)

        print(f"[YOLO] Person Detected? -> {self.person_detected}")
        if self.person_detected:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE
