import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

class PIDController(Node):
    def __init__(self):
        super().__init__('pid_controller')
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.timer = self.create_timer(0.1, self.control_loop)

        self.target_x = 2.0
        self.current_x = 0.0
        self.kp, self.ki, self.kd = 1.0, 0.0, 0.1
        self.integral = 0.0
        self.prev_error = 0.0

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x

    def control_loop(self):
        error = self.target_x - self.current_x
        self.integral += error * 0.1
        derivative = (error - self.prev_error) / 0.1
        output = self.kp * error + self.ki * self.integral + self.kd * derivative

        twist = Twist()
        twist.linear.x = max(min(output, 0.3), -0.3)
        self.cmd_pub.publish(twist)

        self.prev_error = error

def main():
    rclpy.init()
    node = PIDController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
