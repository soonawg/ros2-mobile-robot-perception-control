import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Bool
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO

class YoloPersonDetector(Node):
    def __init__(self):
        super().__init__('yolo_person_detector')
        self.sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )
        self.pub = self.create_publisher(Bool, '/person_detected', 10)
        self.bridge = CvBridge()
        self.model = YOLO('/home/hpmcsg1wl7/exc_ws/yolov8m.pt')
        
        self.get_logger().info("YOLO Person Detector Node initialized")
    
    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        results = self.model.predict(frame, conf=0.5, verbose=False)
        person_found = False

        for r in results:
            for cls in r.boxes.cls:
                if int(cls) == 0:  # class 0 == person
                    person_found = True
                    break

        msg_out = Bool()
        msg_out.data = person_found
        self.pub.publish(msg_out)

        self.get_logger().info(f"Person detected: {person_found}") 

def main(args=None):
    rclpy.init(args=args)
    node = YoloPersonDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()