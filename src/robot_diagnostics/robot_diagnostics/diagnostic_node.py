import rclpy
from rclpy.node import Node
from diagnostic_updater import Updater, DiagnosticStatusWrapper
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus
import random

class DiagnosticNode(Node):
    def __init__(self):
        super().__init__('diagnostic_node')

        self.updater = Updater(self)
        self.updater.setHardwareID("turtlebot3")

        self.updater.add("Battery Status", self.check_battery)
        self.updater.add("Movement Status", self.check_movement)

        # 상태 값 시뮬레이션용 타이머
        self.battery_level = 100
        self.moving = True

        self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        # 배터리 감소 시뮬레이션
        self.battery_level -= random.uniform(0.1, 0.5)
        if self.battery_level < 0:
            self.battery_level = 100

        # 상태 업데이트
        self.updater.update()

    def check_battery(self, stat: DiagnosticStatusWrapper):
        if self.battery_level > 50:
            stat.summary(DiagnosticStatus.OK, "Battery OK")
        elif self.battery_level > 20:
            stat.summary(DiagnosticStatus.WARN, "Battery Low")
        else:
            stat.summary(DiagnosticStatus.ERROR, "Battery Critically Low")

        stat.add("Battery Level", f"{self.battery_level:.2f}%")
        return stat

    def check_movement(self, stat: DiagnosticStatusWrapper):
        # 무작위 이동 여부 전환
        self.moving = not self.moving if random.random() < 0.2 else self.moving
        status_str = "Moving" if self.moving else "Stopped"

        stat.summary(DiagnosticStatus.OK, f"Robot is {status_str}")
        stat.add("Movement", status_str)
        return stat

def main(args=None):
    rclpy.init(args=args)
    node = DiagnosticNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
