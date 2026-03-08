"""
음성(STT) → 로컬 키워드 매칭 → cmd_vel 퍼블리시 ROS2 노드
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

from stt_control.stt_utils import transcribe_audio, parse_command_locally


class SttControlNode(Node):
    """음성 명령을 받아 Turtlebot3를 제어하는 ROS2 노드"""

    def __init__(self):
        super().__init__('stt_control_node')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.get_logger().info("STT Control Node (Local Mode) 초기화 완료")

    def process_audio_and_publish(self, audio_path: str):
        """오디오 파일을 처리하여 명령을 퍼블리시한다.

        Args:
            audio_path (str): 입력 오디오 파일 경로
        """
        self.get_logger().info(f"오디오 파일 인식 시작: {audio_path}")
        try:
            text = transcribe_audio(audio_path)
            self.get_logger().info(f"STT 결과: '{text}'")
        except FileNotFoundError:
            self.get_logger().error(f"오디오 파일을 찾을 수 없습니다: {audio_path}")
            return
        except Exception as e:
            self.get_logger().error(f"오디오 처리 중 에러 발생: {e}")
            return

        command = parse_command_locally(text)
        self.get_logger().info(f"해석된 명령: {command}")

        twist = Twist()
        if command == "forward":
            twist.linear.x = 0.2
            twist.angular.z = 0.0
        elif command == "stop":
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        elif command == "backward":
            twist.linear.x = -0.2
            twist.angular.z = 0.0
        elif command == "left":
            twist.linear.x = 0.0
            twist.angular.z = 0.5
        elif command == "right":
            twist.linear.x = 0.0
            twist.angular.z = -0.5
        else:
            self.get_logger().warn("알 수 없는 명령, 동작하지 않음")
            # 알 수 없는 명령에는 아무것도 보내지 않거나, 정지 신호를 보낼 수 있습니다.
            # 여기서는 아무것도 보내지 않도록 합니다.
            return

        self.publisher_.publish(twist)
        self.get_logger().info(f"cmd_vel 퍼블리시 완료: {command}")


def main(args=None):
    """노드 실행 진입점"""
    rclpy.init(args=args)

    try:
        node = SttControlNode()
        # 예시: audio/sample.wav 파일을 처리
        # 이 파일을 직접 생성하거나 다른 경로로 수정해야 합니다.
        audio_path = "audio/converted_1.wav"
        node.process_audio_and_publish(audio_path)
        # 한 번 실행 후 종료되도록 spin을 주석 처리. 반복 실행을 원하면 주석 해제.
        # rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if 'node' in locals() and rclpy.ok():
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
