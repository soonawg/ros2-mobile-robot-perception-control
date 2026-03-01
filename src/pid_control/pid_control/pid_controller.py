import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math

class PidController(Node):
    def __init__(self):
        super().__init__('pid_controller')

        # PID gains
        self.Kp_lin = 0.5
        self.Ki_lin = 0.05
        self.Kd_lin = 0.1

        self.Kp_ang = 1.5
        self.Ki_ang = 0.02
        self.Kd_ang = 0.05

        self.target_x = 1.0
        self.target_y = 1.0

        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscriber_ = self.create_subscription(Odometry, '/odom', self.odometry_callback, 10)

        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0

        # PID control variables
        self.prev_dist_error = 0.0
        self.integral_dist = 0.0

        self.prev_yaw_error = 0.0
        self.integral_yaw = 0.0

        self.dt = 0.02  # Control loop time step (50 Hz)

        self.timer = self.create_timer(self.dt, self.control_loop)

    def odometry_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.current_yaw = math.atan2(siny_cosp, cosy_cosp)

    def control_loop(self):
        error_x = self.target_x - self.current_x
        error_y = self.target_y - self.current_y
        distance_to_target = math.sqrt(error_x**2 + error_y**2)

        if distance_to_target < 0.05:
            self.stop_robot()
            return

        desired_yaw = math.atan2(error_y, error_x)
        yaw_error = desired_yaw - self.current_yaw
        # Normalize yaw error to [-pi, pi]
        yaw_error = math.atan2(math.sin(yaw_error), math.cos(yaw_error))

        # PID for linear speed
        self.integral_dist += distance_to_target * self.dt
        derivative_dist = (distance_to_target - self.prev_dist_error) / self.dt
        linear_speed = (self.Kp_lin * distance_to_target +
                        self.Ki_lin * self.integral_dist +
                        self.Kd_lin * derivative_dist)
        self.prev_dist_error = distance_to_target

        # PID for angular speed
        self.integral_yaw += yaw_error * self.dt
        derivative_yaw = (yaw_error - self.prev_yaw_error) / self.dt
        angular_speed = (self.Kp_ang * yaw_error +
                         self.Ki_ang * self.integral_yaw +
                         self.Kd_ang * derivative_yaw)
        self.prev_yaw_error = yaw_error

        # Limit speeds to TurtleBot3 max values
        linear_speed = max(min(linear_speed, 0.22), -0.22)
        angular_speed = max(min(angular_speed, 2.84), -2.84)

        msg = Twist()
        msg.linear.x = linear_speed
        msg.angular.z = angular_speed

        self.publisher_.publish(msg)

        # Print PID debug info
        self.get_logger().info(
            f"Distance error: {distance_to_target:.3f}, Linear speed: {linear_speed:.3f}, "
            f"Yaw error: {yaw_error:.3f}, Angular speed: {angular_speed:.3f}"
        )

    def stop_robot(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.publisher_.publish(msg)
        self.get_logger().info("Target reached. Stopping the robot.")
        self.destroy_node()
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    pid_controller = PidController()
    rclpy.spin(pid_controller)

if __name__ == '__main__':
    main()
