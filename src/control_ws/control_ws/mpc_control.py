#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
import numpy as np
import math

class SimpleMPC(Node):
    """
    Simple receding-horizon MPC for TurtleBot3 (simulation friendly).
    Decoupled linear/angular low-complexity MPC using least-squares.
    """

    def __init__(self):
        super().__init__('mpc_controller')
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_cb, 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.control_loop)  # 10 Hz

        # MPC params
        self.dt = 0.1
        self.horizon = 10  # prediction steps
        self.u_max = 0.3
        self.omega_max = 1.0

        # cost weights
        self.q_pos = 10.0
        self.q_yaw = 5.0
        self.r_u = 0.1
        self.r_omega = 0.1

        # target (modify as desired)
        self.target_x = 2.0
        self.target_y = 0.0
        self.target_yaw = 0.0

        # state
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.received_odom = False

    def odom_cb(self, msg: Odometry):
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        # convert quaternion to yaw
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        self.x, self.y, self.yaw = p.x, p.y, yaw
        self.received_odom = True

    def control_loop(self):
        if not self.received_odom:
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        goal_dist = math.hypot(dx, dy)
        goal_yaw = math.atan2(dy, dx)
        yaw_error = self._angle_diff(goal_yaw, self.yaw)

        forward_err = goal_dist * math.cos(yaw_error)

        if forward_err < 0:
            # 목표가 뒤에 있음 → 선속도는 0, 각속도는 크게 돌기
            u0 = 0.0
            omega = float(np.clip(1.5 * yaw_error, -self.omega_max, self.omega_max))
        else:
            # 목표가 앞에 있음 → MPC 계산 사용
            N = self.horizon
            A = np.zeros((N, N))
            for i in range(N):
                for j in range(i+1):
                    A[i, j] = self.dt
            x0 = forward_err
            Qs = self.q_pos * (A.T @ A)
            Rs = self.r_u * np.eye(N)
            H = Qs + Rs
            f = self.q_pos * (A.T @ (x0 * np.ones(N))) * 2.0

            reg = 1e-6
            H_reg = H + reg * np.eye(N)
            try:
                U = -np.linalg.solve(H_reg, f / 2.0)
            except np.linalg.LinAlgError:
                U = np.zeros(N)

            u0 = float(np.clip(U[0], 0.0, self.u_max))
            omega = float(np.clip(0.6 * yaw_error, -self.omega_max, self.omega_max))

        twist = Twist()
        twist.linear.x = u0
        twist.angular.z = omega
        self.cmd_pub.publish(twist)

    def _angle_diff(self, a, b):
        d = a - b
        while d > math.pi:
            d -= 2 * math.pi
        while d < -math.pi:
            d += 2 * math.pi
        return d

def main(args=None):
    rclpy.init(args=args)
    node = SimpleMPC()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
