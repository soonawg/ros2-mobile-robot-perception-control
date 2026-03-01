import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
import cv2
from cv_bridge import CvBridge
from ultralytics import YOLO

DIRECTION_NONE = "NONE"
DIRECTION_LEFT = "LEFT"
DIRECTION_CENTER = "CENTER"
DIRECTION_RIGHT = "RIGHT"

class PerceptionNode(Node):
    """
    YOLO 기반 물체 인식 노드.
    카메라 이미지를 받아 YOLO로 추론 후, 물체 방향을 publish한다.
    """

    def __init__(self):
        super().__init__('perception_node')
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )
        self.publisher_ = self.create_publisher(String, '/object_direction', 10)
        self.bridge = CvBridge()
        self.model = YOLO('yolov8n.pt')  # ultralytics 모델, 환경에 맞게 경로 조정

    def image_callback(self, msg):
        """이미지 콜백: YOLO 추론 후 방향 publish."""
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        results = self.model(cv_image)
        direction = self.get_object_direction(results, cv_image.shape[1])
        self.publisher_.publish(String(data=direction))
        self.get_logger().info(f"Detected direction: {direction}")

    def get_object_direction(self, results, img_width):
        """
        가장 큰 물체의 bbox 중심을 기준으로 방향 결정.
        Args:
            results: YOLO 추론 결과
            img_width: 이미지 가로 픽셀 수
        Returns:
            str: LEFT, CENTER, RIGHT, NONE
        """
        if len(results[0].boxes) == 0:
            return DIRECTION_NONE

        # 가장 큰 bbox 선택
        max_area = 0
        max_box = None
        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            area = (x2 - x1) * (y2 - y1)
            if area > max_area:
                max_area = area
                max_box = box

        if max_box is None:
            return DIRECTION_NONE

        x1, y1, x2, y2 = max_box.xyxy[0]
        center_x = (x1 + x2) / 2

        if center_x < img_width * 0.33:
            return DIRECTION_LEFT
        elif center_x > img_width * 0.66:
            return DIRECTION_RIGHT
        else:
            return DIRECTION_CENTER

def main(args=None):
    rclpy.init(args=args)
    node = PerceptionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()