import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from visualization_msgs.msg import Marker, MarkerArray
from std_msgs.msg import Header
from cv_bridge import CvBridge
from ultralytics import YOLO
import cv2
import numpy as np
import random

# 클래스별 고유 색상 매핑 (임의 지정)
def get_color_for_class(class_id):
    random.seed(class_id)
    return (
        int(random.uniform(50, 255)),
        int(random.uniform(50, 255)),
        int(random.uniform(50, 255)),
    )

class YoloMarkerNode(Node):
    """
    YOLO로 객체 탐지 후, MarkerArray로 RViz에 시각화하는 노드.

    - 모든 객체 클래스 지원
    - 3D 좌표는 Z=0.5m(고정), X/Y는 이미지 중심 기준 비례 변환(간단)
    """

    def __init__(self):
        super().__init__('yolo_marker_node')
        self.bridge = CvBridge()
        self.model = YOLO('/home/hpmcsg1wl7/exp_ws/yolov8n.pt')  # 모델 경로 필요시 수정
        self.class_names = self.model.model.names if hasattr(self.model.model, 'names') else None

        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )
        self.marker_pub = self.create_publisher(
            MarkerArray,
            '/detected_objects/markers',
            10
        )
        self.marker_lifetime = 0.5  # 초

    def image_callback(self, msg):
        """
        이미지 콜백: YOLO 추론 → MarkerArray 생성/퍼블리시
        """
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        results = self.model(cv_image)
        marker_array = MarkerArray()

        img_h, img_w = cv_image.shape[:2]
        header = Header()
        header.stamp = msg.header.stamp
        header.frame_id = msg.header.frame_id if msg.header.frame_id else "camera_link"

        marker_id = 0
        for det in results[0].boxes:
            class_id = int(det.cls[0])
            class_name = self.class_names[class_id] if self.class_names else str(class_id)
            x1, y1, x2, y2 = det.xyxy[0]
            bbox_cx = (x1 + x2) / 2
            bbox_cy = (y1 + y2) / 2

            # 3D 좌표 추정 (Z=0.5m, X/Y는 이미지 중심 기준 비례 변환)
            z = 0.5
            x = (bbox_cx - img_w / 2) / img_w * 0.8  # 시야폭 0.8m 가정
            y = -(bbox_cy - img_h / 2) / img_h * 0.6  # 시야높이 0.6m 가정, 위가 +y

            color = get_color_for_class(class_id)

            # Sphere Marker
            marker = Marker()
            marker.header = header
            marker.ns = "detected_objects"
            marker.id = marker_id
            marker_id += 1
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD
            marker.pose.position.x = float(x)
            marker.pose.position.y = float(y)
            marker.pose.position.z = float(z)
            marker.pose.orientation.x = 0.0
            marker.pose.orientation.y = 0.0
            marker.pose.orientation.z = 0.0
            marker.pose.orientation.w = 1.0
            marker.scale.x = 0.08
            marker.scale.y = 0.08
            marker.scale.z = 0.08
            marker.color.r = color[0] / 255.0
            marker.color.g = color[1] / 255.0
            marker.color.b = color[2] / 255.0
            marker.color.a = 0.8
            marker.lifetime = rclpy.duration.Duration(seconds=self.marker_lifetime).to_msg()
            marker_array.markers.append(marker)

            # Text Marker (label)
            text_marker = Marker()
            text_marker.header = header
            text_marker.ns = "detected_labels"
            text_marker.id = marker_id
            marker_id += 1
            text_marker.type = Marker.TEXT_VIEW_FACING
            text_marker.action = Marker.ADD
            text_marker.pose.position.x = float(x)
            text_marker.pose.position.y = float(y)
            text_marker.pose.position.z = float(z + 0.10)
            text_marker.pose.orientation.w = 1.0
            text_marker.scale.z = 0.08
            text_marker.color.r = color[0] / 255.0
            text_marker.color.g = color[1] / 255.0
            text_marker.color.b = color[2] / 255.0
            text_marker.color.a = 1.0
            text_marker.text = class_name
            text_marker.lifetime = rclpy.duration.Duration(seconds=self.marker_lifetime).to_msg()
            marker_array.markers.append(text_marker)

        self.marker_pub.publish(marker_array)
        self.get_logger().info(f"Published {len(marker_array.markers)//2} objects to RViz.")

def main(args=None):
    rclpy.init(args=args)
    node = YoloMarkerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()