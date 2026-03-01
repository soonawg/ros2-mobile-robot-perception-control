import cv2
import numpy as np
from cv_bridge import CvBridge
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import json

class HSVCalibrator(Node):
    def __init__(self):
        super().__init__("hsv_calibrator")
        self.bridge = CvBridge()

        self.sub = self.create_subscription(
            Image,
            "/camera/image_raw",
            self.image_callback,
            10
        )

        cv2.namedWindow("Calibration", cv2.WINDOW_NORMAL)

        # HSV Lower (기본값: 초록색)
        cv2.createTrackbar("LH", "Calibration", 35, 179, lambda x: None)
        cv2.createTrackbar("LS", "Calibration", 100, 255, lambda x: None)
        cv2.createTrackbar("LV", "Calibration", 100, 255, lambda x: None)

        # HSV Upper
        cv2.createTrackbar("UH", "Calibration", 85, 179, lambda x: None)
        cv2.createTrackbar("US", "Calibration", 255, 255, lambda x: None)
        cv2.createTrackbar("UV", "Calibration", 255, 255, lambda x: None)

        cv2.createTrackbar("Kernel Size", "Calibration", 5, 20, lambda x: None)
        cv2.createTrackbar("Open Iter", "Calibration", 1, 10, lambda x: None)
        cv2.createTrackbar("Close Iter", "Calibration", 1, 10, lambda x: None)
        cv2.createTrackbar("Min Area", "Calibration", 200, 2000, lambda x: None)


    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        frame = cv2.resize(frame, (320, 240))
        
        # 원본을 흐리게 처리 (Tracker와 동일한 전처리)
        blurred = cv2.GaussianBlur(frame, (5,5), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # trackbar values
        lh = cv2.getTrackbarPos("LH", "Calibration")
        ls = cv2.getTrackbarPos("LS", "Calibration")
        lv = cv2.getTrackbarPos("LV", "Calibration")

        uh = cv2.getTrackbarPos("UH", "Calibration")
        us = cv2.getTrackbarPos("US", "Calibration")
        uv = cv2.getTrackbarPos("UV", "Calibration")

        kernel_size = cv2.getTrackbarPos("Kernel Size", "Calibration")
        open_iter = cv2.getTrackbarPos("Open Iter", "Calibration")
        close_iter = cv2.getTrackbarPos("Close Iter", "Calibration")
        min_area = cv2.getTrackbarPos("Min Area", "Calibration")

        if kernel_size < 1:
            kernel_size = 1
        kernel = np.ones((kernel_size, kernel_size), np.uint8)

        lower = np.array([lh, ls, lv])
        upper = np.array([uh, us, uv])

        mask = cv2.inRange(hsv, lower, upper)
        
        # --- Tracker와 동일한 로직으로 미리보기 (WYSIWYG) ---
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=open_iter)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=close_iter)
        # --- (수정 끝) ---

        # Min Area 필터링 결과 시각화
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        result_overlay = frame.copy()

        if contours:
            largest = max(contours, key=cv2.contourArea)
            contour_area = cv2.contourArea(largest)
            
            # min_area 기준으로 필터링
            if contour_area > min_area:
                cv2.drawContours(result_overlay, [largest], -1, (0,255,0), 2)
                M = cv2.moments(largest)
                if M['m00'] != 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    cv2.circle(result_overlay, (cx, cy), 5, (0,0,255), -1)

        # show
        cv2.imshow("Result (Filtered by Min Area)", result_overlay)
        cv2.imshow("Mask (Raw)", mask)

        key = cv2.waitKey(1)
        if key == ord('s'):
            # --- Tracker와 호환되는 키 이름으로 저장 ---
            params = {
                "lower": lower.tolist(),
                "upper": upper.tolist(),
                "kernel_size": int(kernel_size),
                "open_iter": int(open_iter),
                "close_iter": int(close_iter),
                "min_contour_area": int(min_area)
            }
            # --- (수정 끝) ---
            
            with open("hsv_params.json", "w") as f:
                json.dump(params, f, indent=4)
            print(">> [Tracker 호환] 파라미터 저장 완료! (hsv_params.json)")

def main(args=None):
    rclpy.init(args=args)
    node = HSVCalibrator()
    rclpy.spin(node)
    node.destroy_node()
    cv2.destroyAllWindows()
    rclpy.shutdown()

if __name__ == "__main__":
    main()