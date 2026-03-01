#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import numpy as np
import math

class ImpedanceController(Node):
    """
    Virtual impedance controller for a mobile base (TurtleBot3).
    Uses LiDAR front distance to compute a virtual force and map it to velocity.
    """

    def __init__(self):
        super().__init__('impedance_controller')
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_cb, 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.control_loop)

        # virtual impedance params
        self.K = 5.0   # stiffness (spring) toward desired position
        self.D = 2.0   # damping
        self.B = 1.0   # virtual mass / translational factor

        # desired forward displacement (relative) - we want to go forward this much
        self.x_des = 1.0  # meters (virtual setpoint)

        # sensor
        self.front_dist = float('inf')
        self.min_dist_threshold = 0.5  # m: consider obstacle near

        # state
        self.x = 0.0   # virtual current position relative to start (integrated)
        self.v = 0.0   # approximate virtual velocity

    def scan_cb(self, msg: LaserScan):
        ranges = np.array(msg.ranges)
        # Clean up invalid readings
        finite = np.isfinite(ranges)
        if not np.any(finite):
            self.front_dist = float('inf')
            return
        # Consider front sector +/- 20 degrees
        angle = np.linspace(msg.angle_min, msg.angle_max, ranges.size)
        mask = np.abs(angle) <= math.radians(20.0)
        if np.any(finite & mask):
            d = np.min(ranges[finite & mask])
            self.front_dist = float(d)
        else:
            self.front_dist = float(np.min(ranges[finite]))

    def control_loop(self):
        # compute virtual spring-damper force: F = K*(x_des - x) - D*v
        force = self.K * (self.x_des - self.x) - self.D * self.v

        # add repulsive force if obstacle close
        if self.front_dist < self.min_dist_threshold:
            # simple inverse-distance repulsion
            repulse = 2.0 * (1.0 / max(self.front_dist, 0.01) - 1.0 / self.min_dist_threshold)
            force -= repulse

        # map force -> velocity command (divide by virtual B)
        v_cmd = force / self.B
        # saturate
        v_cmd = float(np.clip(v_cmd, -0.3, 0.3))

        # update virtual state (simple integration)
        self.v = 0.9 * self.v + 0.1 * v_cmd
        self.x += self.v * 0.1  # dt = 0.1

        twist = Twist()
        twist.linear.x = v_cmd
        twist.angular.z = 0.0
        self.cmd_pub.publish(twist)

def main():
    rclpy.init()
    node = ImpedanceController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
