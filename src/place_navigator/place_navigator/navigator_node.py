import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
import math

# 장소 좌표 (예시)
LOCATIONS = {
    1: {'x': 2.542, 'y': -0.725, 'yaw': 0.0},
    2: {'x': 1.0,   'y': 0.5,   'yaw': 1.57},
    3: {'x': -1.0,  'y': 2.0,   'yaw': 3.14}
}

def quaternion_from_yaw(yaw: float):
    """
    Yaw(라디안) 값을 quaternion(x, y, z, w)로 변환
    """
    qx = 0.0
    qy = 0.0
    qz = math.sin(yaw * 0.5)
    qw = math.cos(yaw * 0.5)
    return (qx, qy, qz, qw)

class TargetController(Node):
    def __init__(self):
        super().__init__('target_controller')
        self.navigator = BasicNavigator()
        self.navigator.waitUntilNav2Active()
        self.get_logger().info("Nav2 is ready for use!")
        self.get_logger().info("목표 장소 번호를 입력하세요 (예: 1, 2, 3)")
        self.run()

    def run(self):
        while rclpy.ok():
            try:
                loc_id = int(input(">> 장소 번호: "))
                if loc_id not in LOCATIONS:
                    self.get_logger().warn("잘못된 번호입니다.")
                    continue
                self.go_to_location(loc_id)
            except KeyboardInterrupt:
                self.get_logger().info("프로그램 종료")
                break

    def go_to_location(self, loc_id: int):
        target = LOCATIONS[loc_id]

        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.navigator.get_clock().now().to_msg()
        pose.pose.position.x = target['x']
        pose.pose.position.y = target['y']

        qx, qy, qz, qw = quaternion_from_yaw(target['yaw'])
        pose.pose.orientation.x = qx
        pose.pose.orientation.y = qy
        pose.pose.orientation.z = qz
        pose.pose.orientation.w = qw

        self.get_logger().info(f"{loc_id}번 장소로 이동 중...")
        self.navigator.goToPose(pose)

        # 이동 결과 확인
        result = self.navigator.getResult()
        if result:
            self.get_logger().info("도착 완료!")
        else:
            self.get_logger().warn("도착 실패!")

def main(args=None):
    rclpy.init(args=args)
    node = TargetController()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
