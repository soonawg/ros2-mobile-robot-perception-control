import rclpy
from rclpy.node import Node
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped, Twist
from tf_transformations import quaternion_from_euler
import time
import os
from playsound import playsound

class PatrolWithActions(Node):
    def __init__(self):
        super().__init__('patrol_with_actions')
        self.navigator = BasicNavigator()

        # Waypoint 좌표 설정 (예시, 수정 필요)
        self.waypoints = [
            self.create_pose(3.4951536655426025, -1.0814895629882812, 0.0),  # 1시 (A)
            self.create_pose(0.5569186210632324, -1.072829008102417, 0.0),  # 5시 (B)
            self.create_pose(0.5482261180877686, 2.0645248889923096, 0.0),   # 7시 (C)
            self.create_pose(3.438152551651001, 2.087195634841919, 0.0),    # 11시 (D)
        ]


        # cmd_vel 퍼블리셔는 미리 선언
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)

    def create_pose(self, x, y, yaw):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        
        q = quaternion_from_euler(0, 0, yaw)
        pose.pose.orientation.x = q[0]
        pose.pose.orientation.y = q[1]
        pose.pose.orientation.z = q[2]
        pose.pose.orientation.w = q[3]
        return pose

    def perform_action(self, index):
        if index == 0:
            self.get_logger().info('🔍 A: Stop for 10 sec...')
            # time.sleep 대신 spin + timer로 대체
            start_time = self.get_clock().now()
            duration = 5.0
            while (self.get_clock().now() - start_time).nanoseconds / 1e9 < duration:
                rclpy.spin_once(self, timeout_sec=0.1)

        # elif index == 1:
        #     self.get_logger().info('🔄 B: 360 rotation...')
        #     twist = Twist()
        #     twist.angular.z = 1.0
        #     for _ in range(30):  # 약 3초간 회전
        #         self.cmd_vel_pub.publish(twist)
        #         rclpy.spin_once(self, timeout_sec=0.1)
        #     twist.angular.z = 0.0
        #     self.cmd_vel_pub.publish(twist)
        elif index == 1:
            self.get_logger().info('🔄 B: 360 rotation...')
            twist = Twist()
            twist.angular.z = 0.5  # rad/s

            duration = 2 * 3.14 / 0.5  # 360도 회전 시간 ≈ 12.6초
            rate_hz = 10
            iterations = int(duration * rate_hz)

            for _ in range(iterations):
                self.cmd_vel_pub.publish(twist)
                time.sleep(1.0 / rate_hz)

            twist.angular.z = 0.0
            self.cmd_vel_pub.publish(twist)
            self.get_logger().info('🌀 Rotation complete.')

        elif index == 2:
            self.get_logger().info('📢 C: Warning!')
            # 경고음 비동기 실행 (subprocess 사용)
            playsound('/home/hpmcsg1wl7/exc_ws/src/patrol_bot/audio/alert.mp3')

        elif index == 3:
            self.get_logger().info('👁️ D: Scanning for objects...')

            # YOLO, OpenCV, CVBridge 관련 임포트
            from sensor_msgs.msg import Image
            from cv_bridge import CvBridge
            import cv2
            from ultralytics import YOLO

            # YOLO 모델 로드 (처음 호출 시 자동 다운로드됨)
            model = YOLO("/home/hpmcsg1wl7/exc_ws/yolov8n.pt")  # nano 모델, 빠르고 가벼움
            bridge = CvBridge()

            image_msg = None

            # 콜백 함수로 이미지 메시지 받기
            def image_callback(msg):
                nonlocal image_msg
                image_msg = msg

            # 카메라 이미지 구독 (topic 이름은 환경에 맞게 수정)
            sub = self.create_subscription(Image, '/camera/image_raw', image_callback, 10)

            # 이미지 수신 대기 (최대 5초)
            timeout = time.time() + 5
            while image_msg is None and time.time() < timeout:
                rclpy.spin_once(self)

            if image_msg:
                try:
                    # 이미지 변환
                    cv_image = bridge.imgmsg_to_cv2(image_msg, desired_encoding='bgr8')

                    # YOLO 추론
                    results = model(cv_image)[0]

                    # 감지된 클래스 출력
                    detected_classes = set()
                    for cls_id in results.boxes.cls:
                        cls_name = model.names[int(cls_id)]
                        detected_classes.add(cls_name)

                    if detected_classes:
                        self.get_logger().info(f"🔎 Detected objects: {', '.join(detected_classes)}")
                    else:
                        self.get_logger().info("😶 No objects detected.")
                except Exception as e:
                    self.get_logger().error(f"❌ Error during object detection: {e}")
            else:
                self.get_logger().warn("📷 Failed to receive image from camera.")

            self.get_logger().info('✅ Patrol finished!')




        # elif index == 3:
        #     self.get_logger().info('✅ D: Patrol finished!')

    # 마지막 웨이포인트 앞에 객체 두면 그거 감지하고 출력

    # def perform_action(self, index):
    #     if index == 0:
    #         self.get_logger().info('🔍 A: Stop for 10 sec...')
    #         time.sleep(10)

    #     elif index == 1:
    #         self.get_logger().info('🔄 B: 360 rotation...')
    #         twist = Twist()
    #         twist.angular.z = 1.0
    #         for _ in range(30):  # 약 3초간 회전
    #             self.cmd_vel_pub.publish(twist)
    #             time.sleep(0.1)
    #         twist.angular.z = 0.0
    #         self.cmd_vel_pub.publish(twist)

    #     elif index == 2:
    #         self.get_logger().info('📢 C: Warning!')
    #         # 경고음 파일 경로 수정 필요
    #         os.system('play /home/hpmcsg1wl7/exc_ws/src/patrol_bot/audio/alert.mp3')

    #     elif index == 3:
    #         self.get_logger().info('✅ D: Patrol finished!')


    def patrol(self):
        self.get_logger().info('🚀 Patrol started!')

        for i, pose in enumerate(self.waypoints):
            self.get_logger().info(f'➡️ Moving to waypoint {i}...')
            self.navigator.goToPose(pose)

            while not self.navigator.isTaskComplete():
                rclpy.spin_once(self, timeout_sec=0.1)

            result = self.navigator.getResult()
            self.get_logger().info(f'🧪 Navigation result: {result}')
            if result == TaskResult.SUCCEEDED:
                self.get_logger().info(f'📍 Arrived at waypoint {i}')
                self.perform_action(i)
            else:
                self.get_logger().warn(f'⚠️ Failed to reach waypoint {i}')

        self.get_logger().info('🏁 Patrol finished.')
    
    # def patrol(self):
    #     self.get_logger().info('🚀 Patrol started!')

    #     # (선택) 순찰 시작 전 한 번 취소
    #     self.navigator.cancelTask()

    #     for i, pose in enumerate(self.waypoints):
    #         self.get_logger().info(f'➡️ Moving to waypoint {i}...')

    #         # cancelTask() 제거
    #         self.navigator.goToPose(pose)

    #         while not self.navigator.isTaskComplete():
    #             rclpy.spin_once(self)

    #         result = self.navigator.getResult()
    #         self.get_logger().info(f'🧪 Navigation result: {result}')
    #         if result == 'SUCCEEDED':
    #             self.get_logger().info(f'📍 Arrived at waypoint {i}')
    #             self.perform_action(i)
    #         else:
    #             self.get_logger().warn(f'⚠️ Failed to reach waypoint {i}')

    #     self.get_logger().info('🏁 Patrol finished.')

    # def patrol(self):
    #     self.get_logger().info('🚀 Patrol started!')
    #     for i, pose in enumerate(self.waypoints):
    #         self.get_logger().info(f'➡️ Moving to waypoint {i}...')
    #         self.navigator.goToPose(pose)
    #         while not self.navigator.isTaskComplete():
    #             time.sleep(0.5)

    #         result = self.navigator.getResult()
    #         if result == 'SUCCEEDED':
    #             self.get_logger().info(f'📍 Arrived at waypoint {i}')
    #             self.perform_action(i)
    #         else:
    #             self.get_logger().warn(f'⚠️ Failed to reach waypoint {i}')

    #     self.get_logger().info('🏁 Patrol finished.')
    # def patrol(self):
    #     self.get_logger().info('🚀 Patrol started!')
    #     for i, pose in enumerate(self.waypoints):
    #         self.get_logger().info(f'➡️ Moving to waypoint {i}...')

    #         self.navigator.cancelTask()      # 이전 목표 취소
    #         self.navigator.goToPose(pose)

    #         while not self.navigator.isTaskComplete():
    #             rclpy.spin_once(self)        # ROS 콜백 처리

    #         result = self.navigator.getResult()
    #         self.get_logger().info(f'🧪 Navigation result: {result}')
    #         if result == 'SUCCEEDED':
    #             self.get_logger().info(f'📍 Arrived at waypoint {i}')
    #             self.perform_action(i)
    #         else:
    #             self.get_logger().warn(f'⚠️ Failed to reach waypoint {i}')

    #     self.get_logger().info('🏁 Patrol finished.')
    


def main(args=None):
    rclpy.init(args=args)
    node = PatrolWithActions()
    node.patrol()
    rclpy.shutdown()
