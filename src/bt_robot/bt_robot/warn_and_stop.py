import py_trees
import rclpy
from geometry_msgs.msg import Twist
import os
import threading
from playsound import playsound
import time

class WarnAndStop(py_trees.behaviour.Behaviour):
    def __init__(self, name="WarnAndStop"):
        super().__init__(name)
        self.node = rclpy.create_node("warn_and_stop_node")
        self.pub = self.node.create_publisher(Twist, "/cmd_vel", 10)
        self._sound_played = False
        self._last_stop_time = 0
        self._stop_interval = 0.1  # 100ms 간격으로 정지 명령 전송

        self.warning_sound = "/home/hpmcsg1wl7/exc_ws/src/bt_robot/sounds/alert.mp3"
        
        if not os.path.exists(self.warning_sound):
            self.node.get_logger().warn(f"Warning sound file not found at: {self.warning_sound}")
    
    def initialise(self):
        self._sound_played = False
        self._last_stop_time = 0
    
    def stop_robot(self):
        twist = Twist()
        twist.linear.x = 0.0
        twist.linear.y = 0.0
        twist.linear.z = 0.0
        twist.angular.x = 0.0
        twist.angular.y = 0.0
        twist.angular.z = 0.0
        self.pub.publish(twist)
    
    def update(self):
        rclpy.spin_once(self.node, timeout_sec=0.01)
        current_time = time.time()
        
        if current_time - self._last_stop_time >= self._stop_interval:
            self.stop_robot()
            self._last_stop_time = current_time
        
        if not self._sound_played and os.path.exists(self.warning_sound):
            try:
                self.node.get_logger().info("[WarnAndStop] Playing warning sound")
                threading.Thread(target=playsound, args=(self.warning_sound,), daemon=True).start()
                self._sound_played = True
            except Exception as e:
                self.node.get_logger().error(f"Failed to play sound: {str(e)}")
        
        self.node.get_logger().info("[WarnAndStop] Robot stopped due to person detection")
        return py_trees.common.Status.RUNNING

