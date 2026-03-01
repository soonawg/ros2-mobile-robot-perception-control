# import rclpy
# from rclpy.node import Node
# from geometry_msgs.msg import Twist
# from sensor_msgs.msg import Image
# from cv_bridge import CvBridge
# import cv2
# import numpy as np

# class ColorTracker(Node):
#     def __init__(self):
#         super().__init__('color_tracker')
#         self.bridge = CvBridge()

#         self.image_sub = self.create_subscription(
#             Image,
#             '/camera/image_raw',
#             self.image_callback,
#             10
#         )

#         self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
#         self.timer = self.create_timer(0.1, self.publish_cmd)

#         self.target_center_x = None
#         self.image_width = None
    
#     def image_callback(self, msg):
#         # ROS 이미지 -> OpenCV 이미지 변환
#         frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

#         # 이미지 너비 저장
#         self.image_width = frame.shape[1]

#         # BGR -> HSV로 변환
#         hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
#         # 초록색 범위 정의 (HSV 색공간)
#         lower_green = np.array([35, 100, 100])   # 초록색 하한
#         upper_green = np.array([85, 255, 255])   # 초록색 상한
#         mask = cv2.inRange(hsv, lower_green, upper_green)

#         # Morphological operations
#         mask = cv2.erode(mask, None, iterations=2)
#         mask = cv2.dilate(mask, None, iterations=2)

#         # Find contours
#         contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#         if contours:
#             largest = max(contours, key=cv2.contourArea)
#             (x, y, w, h) = cv2.boundingRect(largest)
#             self.target_center_x = x + w // 2

#             # For visualization (optional)
#             cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
#         else:
#             self.target_center_x = None

#         # Show frame (for debug)
#         cv2.imshow('Tracking', frame)
#         cv2.waitKey(1)

#     def publish_cmd(self):
#         if self.target_center_x is None or self.image_width is None:
#             self.cmd_vel_pub.publish(Twist())  # stop
#             return

#         twist = Twist()
#         center_error = self.target_center_x - self.image_width // 2

#         # 회전 속도 계산 (단순 proportional 제어)
#         twist.angular.z = -center_error * 0.002  # tuning needed
#         twist.linear.x = 0.1  # 이동 전진 속도

#         self.cmd_vel_pub.publish(twist)


# def main(args=None):
#     rclpy.init(args=args)
#     node = ColorTracker()
#     rclpy.spin(node)
#     node.destroy_node()
#     cv2.destroyAllWindows()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()


## Step1.
# import rclpy
# from rclpy.node import Node
# from geometry_msgs.msg import Twist
# from sensor_msgs.msg import Image
# from cv_bridge import CvBridge
# import cv2
# import numpy as np
# import time

# class ColorTracker(Node):
#     def __init__(self):
#         super().__init__('color_tracker')
#         self.bridge = CvBridge()

#         self.image_sub = self.create_subscription(
#             Image,
#             '/camera/image_raw',
#             self.image_callback,
#             10
#         )

#         self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
#         self.timer = self.create_timer(0.1, self.publish_cmd)

#         self.target_center_x = None
#         self.image_width = None

#         # FPS 측정용
#         self._last_time = time.time()
#         self._frame_count = 0
#         self._fps = 0.0

#         # morphology kernel
#         self.kernel = np.ones((5,5), np.uint8)

#     def image_callback(self, msg):
#         # ROS 이미지 -> OpenCV 이미지 변환
#         frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

#         # 1) resize for consistent processing speed
#         frame = cv2.resize(frame, (320, 240))
#         self.image_width = frame.shape[1]

#         # 2) preprocessing - blur to reduce noise
#         blurred = cv2.GaussianBlur(frame, (5,5), 0)

#         # 3) BGR -> HSV
#         hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

#         mask = cv2.inRange(hsv, self.lower, self.upper)

#         mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel, iterations=self.open_iter)
#         mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel, iterations=self.close_iter)

#         # 6) Find contours
#         contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#         cx = None
#         cy = None
#         contour_area = 0

#         if contours:
#             # 가장 큰 contour 선택
#             largest = max(contours, key=cv2.contourArea)
#             contour_area = cv2.contourArea(largest)

#             # 면적이 너무 작으면 무시
#             if contour_area > self.min_area:
#                 M = cv2.moments(largest)
#                 if M['m00'] != 0:
#                     cx = int(M['m10'] / M['m00'])
#                     cy = int(M['m01'] / M['m00'])
#                     self.target_center_x = cx
#                 else:
#                     self.target_center_x = None
#             else:
#                 self.target_center_x = None
#         else:
#             self.target_center_x = None

#         # FPS 계산 (간단)
#         self._frame_count += 1
#         if time.time() - self._last_time >= 1.0:
#             self._fps = self._frame_count / (time.time() - self._last_time)
#             self._frame_count = 0
#             self._last_time = time.time()

#         # Visualization overlay
#         overlay = frame.copy()
#         if self.target_center_x is not None:
#             cv2.circle(overlay, (self.target_center_x, cy), 5, (0,0,255), -1)
#             cv2.drawContours(overlay, [largest], -1, (0,255,0), 2)
#         # center line
#         cv2.line(overlay, (self.image_width//2,0), (self.image_width//2, frame.shape[0]), (255,0,0),1)

#         # text: fps and status
#         status_text = f"FPS: {self._fps:.1f}"
#         if self.target_center_x is not None:
#             err = self.target_center_x - self.image_width // 2
#             status_text += f" | Error: {err}"
#         else:
#             status_text += " | Target: None"

#         cv2.putText(overlay, status_text, (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 1)

#         cv2.imshow('Tracking', overlay)
#         cv2.imshow('Mask', mask)
#         cv2.waitKey(1)

#     def publish_cmd(self):
#         if self.target_center_x is None or self.image_width is None:
#             # stop
#             self.cmd_vel_pub.publish(Twist())
#             return

#         twist = Twist()
#         center_error = (self.target_center_x - self.image_width // 2)

#         # normalized error in [-1,1]
#         norm_err = center_error / float(self.image_width // 2)
#         # proportional control on angular with stronger gain but clamped
#         K_ang = 0.8
#         ang_z = -K_ang * norm_err
#         # clamp
#         ang_z = max(min(ang_z, 1.0), -1.0)

#         # linear speed reduces when error large to avoid overshoot
#         base_lin = 0.12
#         linear_x = base_lin * (1.0 - min(abs(norm_err), 1.0))

#         twist.angular.z = float(ang_z)
#         twist.linear.x = float(linear_x)

#         self.cmd_vel_pub.publish(twist)


# def main(args=None):
#     rclpy.init(args=args)
#     node = ColorTracker()
#     rclpy.spin(node)
#     node.destroy_node()
#     cv2.destroyAllWindows()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()



##  Step2. calibartion + Json
# import rclpy
# from rclpy.node import Node
# from geometry_msgs.msg import Twist
# from sensor_msgs.msg import Image
# from cv_bridge import CvBridge
# import cv2
# import numpy as np
# import time
# import json
# import os


# class ColorTracker(Node):
#     def __init__(self):
#         super().__init__('color_tracker')
#         self.bridge = CvBridge()

#         self.image_sub = self.create_subscription(
#             Image,
#             '/camera/image_raw',
#             self.image_callback,
#             10
#         )

#         self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
#         self.timer = self.create_timer(0.1, self.publish_cmd)

#         self.target_center_x = None
#         self.image_width = None

#         # FPS 측정용
#         self._last_time = time.time()
#         self._frame_count = 0
#         self._fps = 0.0

#         # morphology kernel
#         self.kernel = np.ones((5,5), np.uint8)

#         # ---- Load HSV Calibration Parameters ----
#         self.hsv_params = self.load_hsv_params()
#         self.lower = np.array(self.hsv_params["lower"])
#         self.upper = np.array(self.hsv_params["upper"])

#         self.kernel = np.ones(
#             (self.hsv_params["kernel_size"], self.hsv_params["kernel_size"]),
#             np.uint8
#         )

#         self.open_iter = self.hsv_params["open_iter"]
#         self.close_iter = self.hsv_params["close_iter"]
#         self.min_area = self.hsv_params["min_contour_area"]



#     def image_callback(self, msg):
#         # ROS 이미지 -> OpenCV 이미지 변환
#         frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

#         # 1) resize for consistent processing speed
#         frame = cv2.resize(frame, (320, 240))
#         self.image_width = frame.shape[1]

#         # 2) preprocessing - blur to reduce noise
#         blurred = cv2.GaussianBlur(frame, (5,5), 0)

#         # 3) BGR -> HSV
#         hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

#         # 4) 색상 범위 (초록) - 필요시 튜닝
#         lower_green = np.array([35, 100, 100])
#         upper_green = np.array([85, 255, 255])
#         mask = cv2.inRange(hsv, lower_green, upper_green)

#         # 5) morphology - open then close to remove noise and fill holes
#         mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel, iterations=1)
#         mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel, iterations=1)

#         # 6) Find contours
#         contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#         cx = None
#         cy = None
#         contour_area = 0

#         if contours:
#             # 가장 큰 contour 선택
#             largest = max(contours, key=cv2.contourArea)
#             contour_area = cv2.contourArea(largest)

#             # 면적이 너무 작으면 무시
#             if contour_area > 200:
#                 M = cv2.moments(largest)
#                 if M['m00'] != 0:
#                     cx = int(M['m10'] / M['m00'])
#                     cy = int(M['m01'] / M['m00'])
#                     self.target_center_x = cx
#                 else:
#                     self.target_center_x = None
#             else:
#                 self.target_center_x = None
#         else:
#             self.target_center_x = None

#         # FPS 계산 (간단)
#         self._frame_count += 1
#         if time.time() - self._last_time >= 1.0:
#             self._fps = self._frame_count / (time.time() - self._last_time)
#             self._frame_count = 0
#             self._last_time = time.time()

#         # Visualization overlay
#         overlay = frame.copy()
#         if self.target_center_x is not None:
#             cv2.circle(overlay, (self.target_center_x, cy), 5, (0,0,255), -1)
#             cv2.drawContours(overlay, [largest], -1, (0,255,0), 2)
#         # center line
#         cv2.line(overlay, (self.image_width//2,0), (self.image_width//2, frame.shape[0]), (255,0,0),1)

#         # text: fps and status
#         status_text = f"FPS: {self._fps:.1f}"
#         if self.target_center_x is not None:
#             err = self.target_center_x - self.image_width // 2
#             status_text += f" | Error: {err}"
#         else:
#             status_text += " | Target: None"

#         cv2.putText(overlay, status_text, (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 1)

#         cv2.imshow('Tracking', overlay)
#         cv2.imshow('Mask', mask)
#         cv2.waitKey(1)

#     def load_hsv_params(self):
#         default_params = {
#             "lower": [35, 100, 100],
#             "upper": [85, 255, 255],
#             "kernel_size": 5,
#             "open_iter": 1,
#             "close_iter": 1,
#             "min_contour_area": 200
#         }

#         if os.path.exists("hsv_params.json"):
#             try:
#                 with open("hsv_params.json", "r") as f:
#                     params = json.load(f)
#                 print(">> Loaded HSV parameters from file.")
#                 return params
#             except:
#                 print(">> Failed to read hsv_params.json — using defaults.")
#                 return default_params
#         else:
#             print(">> hsv_params.json not found — using defaults.")
#             return default_params
    

#     def publish_cmd(self):
#         if self.target_center_x is None or self.image_width is None:
#             # stop
#             self.cmd_vel_pub.publish(Twist())
#             return

#         twist = Twist()
#         center_error = (self.target_center_x - self.image_width // 2)

#         # normalized error in [-1,1]
#         norm_err = center_error / float(self.image_width // 2)
#         # proportional control on angular with stronger gain but clamped
#         K_ang = 0.8
#         ang_z = -K_ang * norm_err
#         # clamp
#         ang_z = max(min(ang_z, 1.0), -1.0)

#         # linear speed reduces when error large to avoid overshoot
#         base_lin = 0.12
#         linear_x = base_lin * (1.0 - min(abs(norm_err), 1.0))

#         twist.angular.z = float(ang_z)
#         twist.linear.x = float(linear_x)

#         self.cmd_vel_pub.publish(twist)


# def main(args=None):
#     rclpy.init(args=args)
#     node = ColorTracker()
#     rclpy.spin(node)
#     node.destroy_node()
#     cv2.destroyAllWindows()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()



## Step3. FSM 추가
# import rclpy
# from rclpy.node import Node
# from geometry_msgs.msg import Twist
# from sensor_msgs.msg import Image
# from cv_bridge import CvBridge
# import cv2
# import numpy as np
# import time
# import json
# import os


# class ColorTracker(Node):
#     def __init__(self):
#         super().__init__('color_tracker')
#         self.bridge = CvBridge()

#         self.image_sub = self.create_subscription(
#             Image,
#             '/camera/image_raw',
#             self.image_callback,
#             10
#         )

#         self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
#         self.timer = self.create_timer(0.1, self.publish_cmd)

#         self.target_center_x = None
#         self.image_width = None

#         # FPS 측정용
#         self._last_time = time.time()
#         self._frame_count = 0
#         self._fps = 0.0

#         # morphology kernel
#         self.kernel = np.ones((5,5), np.uint8)

#         # ---- Load HSV Calibration Parameters ----
#         self.hsv_params = self.load_hsv_params()
#         self.lower = np.array(self.hsv_params["lower"])
#         self.upper = np.array(self.hsv_params["upper"])

#         self.kernel = np.ones(
#             (self.hsv_params["kernel_size"], self.hsv_params["kernel_size"]),
#             np.uint8
#         )

#         self.open_iter = self.hsv_params["open_iter"]
#         self.close_iter = self.hsv_params["close_iter"]
#         self.min_area = self.hsv_params["min_contour_area"]

#         # FSM State
#         self.state = "SEARCHING" # TRACKING / LOST / SEARCHING
#         self.lost_frames = 0
#         self.lost_threshold = 15



#     def image_callback(self, msg):
#         # ROS 이미지 -> OpenCV 이미지 변환
#         frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

#         # 1) resize for consistent processing speed
#         frame = cv2.resize(frame, (320, 240))
#         self.image_width = frame.shape[1]

#         # 2) preprocessing - blur to reduce noise
#         blurred = cv2.GaussianBlur(frame, (5,5), 0)

#         # 3) BGR -> HSV
#         hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

#         # 4) 색상 범위 (초록) - 필요시 튜닝
#         lower_green = np.array([35, 100, 100])
#         upper_green = np.array([85, 255, 255])
#         mask = cv2.inRange(hsv, lower_green, upper_green)

#         # 5) morphology - open then close to remove noise and fill holes
#         mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel, iterations=1)
#         mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel, iterations=1)

#         # 6) Find contours
#         contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#         cx = None
#         cy = None
#         contour_area = 0

#         if contours:
#             # 가장 큰 contour 선택
#             largest = max(contours, key=cv2.contourArea)
#             contour_area = cv2.contourArea(largest)

#             # 면적이 너무 작으면 무시
#             if contour_area > 200:
#                 M = cv2.moments(largest)
#                 if M['m00'] != 0:
#                     cx = int(M['m10'] / M['m00'])
#                     cy = int(M['m01'] / M['m00'])
#                     self.target_center_x = cx
#                 else:
#                     self.target_center_x = None
#             else:
#                 self.target_center_x = None
#         else:
#             self.target_center_x = None
        
#         # -----------------------
#         # BBOX HEIGHT (distance proxy)
#         # -----------------------
#         self.bbox_h = None
#         self.image_height = frame.shape[0]

#         if contours and contour_area > 200:
#             x, y, w, h = cv2.boundingRect(largest)
#             self.bbox_h = h
#         else:
#             self.bbox_h = None



#         # -------------------------------
#         #   🔥 FSM STATE UPDATE LOGIC
#         # -------------------------------
#         if self.target_center_x is not None:
#             # ---- TRACKING ----
#             if self.state != "TRACKING":
#                 print(">> Reacquired → TRACKING")
#             self.state = "TRACKING"
#             self.lost_frames = 0

#         else:
#             # ---- LOST START ----
#             if self.state == "TRACKING":
#                 print(">> Target Lost → LOST")
#                 self.state = "LOST"
#                 self.lost_frames = 1

#             # ---- LOST CONTINUE ----
#             elif self.state == "LOST":
#                 self.lost_frames += 1
#                 if self.lost_frames > self.lost_threshold:
#                     print(">> LOST threshold exceeded → SEARCHING")
#                     self.state = "SEARCHING"

#             # ---- SEARCHING STAY ----
#             elif self.state == "SEARCHING":
#                 pass


#         # FPS 계산 (간단)
#         self._frame_count += 1
#         if time.time() - self._last_time >= 1.0:
#             self._fps = self._frame_count / (time.time() - self._last_time)
#             self._frame_count = 0
#             self._last_time = time.time()

#         # Visualization overlay
#         overlay = frame.copy()
#         if self.target_center_x is not None:
#             cv2.circle(overlay, (self.target_center_x, cy), 5, (0,0,255), -1)
#             cv2.drawContours(overlay, [largest], -1, (0,255,0), 2)
#         # center line
#         cv2.line(overlay, (self.image_width//2,0), (self.image_width//2, frame.shape[0]), (255,0,0),1)

#         # text: fps and status
#         status_text = f"FPS: {self._fps:.1f}"
#         if self.target_center_x is not None:
#             err = self.target_center_x - self.image_width // 2
#             status_text += f" | Error: {err}"
#         else:
#             status_text += " | Target: None"

#         cv2.putText(overlay, status_text, (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 1)

#         cv2.imshow('Tracking', overlay)
#         cv2.imshow('Mask', mask)
#         cv2.waitKey(1)

#     def load_hsv_params(self):
#         default_params = {
#             "lower": [35, 100, 100],
#             "upper": [85, 255, 255],
#             "kernel_size": 5,
#             "open_iter": 1,
#             "close_iter": 1,
#             "min_contour_area": 200
#         }

#         if os.path.exists("hsv_params.json"):
#             try:
#                 with open("hsv_params.json", "r") as f:
#                     params = json.load(f)
#                 print(">> Loaded HSV parameters from file.")
#                 return params
#             except:
#                 print(">> Failed to read hsv_params.json — using defaults.")
#                 return default_params
#         else:
#             print(">> hsv_params.json not found — using defaults.")
#             return default_params
    

#     def publish_cmd(self):
#         twist = Twist()

#         # ----------------------------
#         #   🔥 FSM-BASED CONTROL
#         # ----------------------------

#         # 1) TRACKING — 정상 추적 제어
#         if self.state == "TRACKING":
#             err = (self.target_center_x - self.image_width // 2)

#             norm_err = err / float(self.image_width // 2)
#             K_ang = 0.8
#             ang_z = -K_ang * norm_err
#             ang_z = max(min(ang_z, 1.0), -1.0)

#             base_lin = 0.12
#             lin_x = base_lin * (1.0 - min(abs(norm_err), 1.0))

#             twist.angular.z = float(ang_z)
#             twist.linear.x = float(lin_x)

#         # 2) LOST — 약한 추적 유지
#         elif self.state == "LOST":
#             twist.angular.z = 0.3   # 부드럽게 좌회전하며 재탐색
#             twist.linear.x = 0.05

#         # 3) SEARCHING — 크게 회전하며 탐색
#         elif self.state == "SEARCHING":
#             twist.angular.z = 0.6   # 더 강하게 스캔
#             twist.linear.x = 0.0    # 이동은 멈춤

#         self.cmd_vel_pub.publish(twist)

# def main(args=None):
#     rclpy.init(args=args)
#     node = ColorTracker()
#     rclpy.spin(node)
#     node.destroy_node()
#     cv2.destroyAllWindows()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()




## Step 4. 거리기반 속도 제어
# import rclpy
# from rclpy.node import Node
# from geometry_msgs.msg import Twist
# from sensor_msgs.msg import Image
# from cv_bridge import CvBridge
# import cv2
# import numpy as np
# import time
# import json
# import os


# class ColorTracker(Node):
#     def __init__(self):
#         super().__init__('color_tracker')
#         self.bridge = CvBridge()

#         self.image_sub = self.create_subscription(
#             Image,
#             '/camera/image_raw',
#             self.image_callback,
#             10
#         )

#         self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
#         self.timer = self.create_timer(0.1, self.publish_cmd)

#         self.target_center_x = None
#         self.image_width = None

#         self.bbox_h = None
#         self.image_height = None


#         # FPS 측정용
#         self._last_time = time.time()
#         self._frame_count = 0
#         self._fps = 0.0

#         # morphology kernel
#         self.kernel = np.ones((5,5), np.uint8)

#         # ---- Load HSV Calibration Parameters ----
#         self.hsv_params = self.load_hsv_params()
#         self.lower = np.array(self.hsv_params["lower"])
#         self.upper = np.array(self.hsv_params["upper"])

#         self.kernel = np.ones(
#             (self.hsv_params["kernel_size"], self.hsv_params["kernel_size"]),
#             np.uint8
#         )

#         self.open_iter = self.hsv_params["open_iter"]
#         self.close_iter = self.hsv_params["close_iter"]
#         self.min_area = self.hsv_params["min_contour_area"]

#         # FSM State
#         self.state = "SEARCHING" # TRACKING / LOST / SEARCHING
#         self.lost_frames = 0
#         self.lost_threshold = 15



#     def image_callback(self, msg):
#         # ROS 이미지 -> OpenCV 이미지 변환
#         frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

#         # 1) resize for consistent processing speed
#         frame = cv2.resize(frame, (320, 240))
#         self.image_width = frame.shape[1]

#         # 2) preprocessing - blur to reduce noise
#         blurred = cv2.GaussianBlur(frame, (5,5), 0)

#         # 3) BGR -> HSV
#         hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

#         # 4) 색상 범위 (초록) - 필요시 튜닝
#         lower_green = np.array([35, 100, 100])
#         upper_green = np.array([85, 255, 255])
#         mask = cv2.inRange(hsv, lower_green, upper_green)

#         # 5) morphology - open then close to remove noise and fill holes
#         mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel, iterations=1)
#         mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel, iterations=1)

#         # 6) Find contours
#         contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#         cx = None
#         cy = None
#         contour_area = 0

#         if contours:
#             largest = max(contours, key=cv2.contourArea)
#             contour_area = cv2.contourArea(largest)

#             if contour_area > 200:
#                 x, y, w, h = cv2.boundingRect(largest)
#                 self.bbox_h = h           # 여기서 bbox_h 업데이트!
#                 self.image_height = frame.shape[0]  # 전체 이미지 높이
#                 M = cv2.moments(largest)
#                 if M['m00'] != 0:
#                     cx = int(M['m10'] / M['m00'])
#                     cy = int(M['m01'] / M['m00'])
#                     self.target_center_x = cx
#                 else:
#                     self.target_center_x = None
#                     self.bbox_h = None
#             else:
#                 self.target_center_x = None
#                 self.bbox_h = None
#         else:
#             self.target_center_x = None
#             self.bbox_h = None




#         # -------------------------------
#         #   🔥 FSM STATE UPDATE LOGIC
#         # -------------------------------
#         if self.target_center_x is not None:
#             # ---- TRACKING ----
#             if self.state != "TRACKING":
#                 print(">> Reacquired → TRACKING")
#             self.state = "TRACKING"
#             self.lost_frames = 0

#         else:
#             # ---- LOST START ----
#             if self.state == "TRACKING":
#                 print(">> Target Lost → LOST")
#                 self.state = "LOST"
#                 self.lost_frames = 1

#             # ---- LOST CONTINUE ----
#             elif self.state == "LOST":
#                 self.lost_frames += 1
#                 if self.lost_frames > self.lost_threshold:
#                     print(">> LOST threshold exceeded → SEARCHING")
#                     self.state = "SEARCHING"

#             # ---- SEARCHING STAY ----
#             elif self.state == "SEARCHING":
#                 pass


#         # FPS 계산 (간단)
#         self._frame_count += 1
#         if time.time() - self._last_time >= 1.0:
#             self._fps = self._frame_count / (time.time() - self._last_time)
#             self._frame_count = 0
#             self._last_time = time.time()

#         # Visualization overlay
#         overlay = frame.copy()
#         if self.target_center_x is not None:
#             cv2.circle(overlay, (self.target_center_x, cy), 5, (0,0,255), -1)
#             cv2.drawContours(overlay, [largest], -1, (0,255,0), 2)
#         # center line
#         cv2.line(overlay, (self.image_width//2,0), (self.image_width//2, frame.shape[0]), (255,0,0),1)

#         # text: fps and status
#         status_text = f"FPS: {self._fps:.1f}"
#         if self.target_center_x is not None:
#             err = self.target_center_x - self.image_width // 2
#             status_text += f" | Error: {err}"
#         else:
#             status_text += " | Target: None"

#         cv2.putText(overlay, status_text, (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 1)

#         cv2.imshow('Tracking', overlay)
#         cv2.imshow('Mask', mask)
#         cv2.waitKey(1)

#     def load_hsv_params(self):
#         default_params = {
#             "lower": [35, 100, 100],
#             "upper": [85, 255, 255],
#             "kernel_size": 5,
#             "open_iter": 1,
#             "close_iter": 1,
#             "min_contour_area": 200
#         }

#         if os.path.exists("hsv_params.json"):
#             try:
#                 with open("hsv_params.json", "r") as f:
#                     params = json.load(f)
#                 print(">> Loaded HSV parameters from file.")
#                 return params
#             except:
#                 print(">> Failed to read hsv_params.json — using defaults.")
#                 return default_params
#         else:
#             print(">> hsv_params.json not found — using defaults.")
#             return default_params
    

#     def publish_cmd(self):
#         twist = Twist()

#         # ----------------------------
#         #   🔥 FSM-BASED CONTROL
#         # ----------------------------

#         # 1) TRACKING — 정상 추적 제어
#         if self.state == "TRACKING":

#             # ----------------------------
#             #  (A) 각속도 (기존 동일)
#             # ----------------------------
#             err = (self.target_center_x - self.image_width // 2)
#             norm_err = err / float(self.image_width // 2)
#             K_ang = 0.8
#             ang_z = -K_ang * norm_err
#             ang_z = max(min(ang_z, 1.0), -1.0)

#             # ----------------------------
#             #  (B) 거리 기반 선형 속도
#             # ----------------------------

#             # bbox_h 없으면(= 작은 contour 탐지 실패) 안전하게 멈춤
#             if self.bbox_h is None:
#                 linear_x = 0.0

#             else:
#                 # 정규화된 높이: 가까울수록 1에 가까움
#                 h_norm = self.bbox_h / float(self.image_height)

#                 # 멀면 빠르게, 가까우면 느리게
#                 max_speed = 0.15
#                 linear_x = max_speed * (1.0 - min(h_norm, 1.0))

#                 # 너무 가까우면 STOP(충돌 방지)
#                 if h_norm > 0.65:
#                     linear_x = 0.0

#                 # 회전 오차가 크면 속도 감속
#                 linear_x *= (1.0 - min(abs(norm_err), 1.0))

#             twist.angular.z = float(ang_z)
#             twist.linear.x = float(linear_x)


#         # 2) LOST — 약한 추적 유지
#         elif self.state == "LOST":
#             twist.angular.z = 0.3   # 부드럽게 좌회전하며 재탐색
#             twist.linear.x = 0.05

#         # 3) SEARCHING — 크게 회전하며 탐색
#         elif self.state == "SEARCHING":
#             twist.angular.z = 0.6   # 더 강하게 스캔
#             twist.linear.x = 0.0    # 이동은 멈춤

#         self.cmd_vel_pub.publish(twist)

# def main(args=None):
#     rclpy.init(args=args)
#     node = ColorTracker()
#     rclpy.spin(node)
#     node.destroy_node()
#     cv2.destroyAllWindows()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()



## Last Step. 성능 로깅
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
import time
import json
import csv
import os


class ColorTracker(Node):
    def __init__(self):
        super().__init__('color_tracker')
        self.bridge = CvBridge()

        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.publish_cmd)

        self.target_center_x = None
        self.image_width = None

        self.bbox_h = None
        self.image_height = None


        # FPS 측정용
        self._last_time = time.time()
        self._frame_count = 0
        self._fps = 0.0

        # morphology kernel
        self.kernel = np.ones((5,5), np.uint8)

        # ---- Load HSV Calibration Parameters ----
        self.hsv_params = self.load_hsv_params()
        self.lower = np.array(self.hsv_params["lower"])
        self.upper = np.array(self.hsv_params["upper"])

        self.kernel = np.ones(
            (self.hsv_params["kernel_size"], self.hsv_params["kernel_size"]),
            np.uint8
        )

        self.open_iter = self.hsv_params["open_iter"]
        self.close_iter = self.hsv_params["close_iter"]
        self.min_area = self.hsv_params["min_contour_area"]

        # FSM State
        self.state = "SEARCHING" # TRACKING / LOST / SEARCHING
        self.lost_frames = 0
        self.lost_threshold = 15

        self.log_file = open("tracking_log.csv", "w", newline="")
        self.logger = csv.writer(self.log_file)
        self.logger.writerow(["time", "state", "target_center_x", "bbox_h", "error", "fps", "linear_x", "angular_z"])


    def image_callback(self, msg):
        # ROS 이미지 -> OpenCV 이미지 변환
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # 1) resize for consistent processing speed
        frame = cv2.resize(frame, (320, 240))
        self.image_width = frame.shape[1]

        # 2) preprocessing - blur to reduce noise
        blurred = cv2.GaussianBlur(frame, (5,5), 0)

        # 3) BGR -> HSV
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # 4) 색상 범위 (초록) - 필요시 튜닝
        lower_green = np.array([35, 100, 100])
        upper_green = np.array([85, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # 5) morphology - open then close to remove noise and fill holes
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel, iterations=1)

        # 6) Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        cx = None
        cy = None
        contour_area = 0

        if contours:
            largest = max(contours, key=cv2.contourArea)
            contour_area = cv2.contourArea(largest)

            if contour_area > 200:
                x, y, w, h = cv2.boundingRect(largest)
                self.bbox_h = h           # 여기서 bbox_h 업데이트!
                self.image_height = frame.shape[0]  # 전체 이미지 높이
                M = cv2.moments(largest)
                if M['m00'] != 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    self.target_center_x = cx
                else:
                    self.target_center_x = None
                    self.bbox_h = None
            else:
                self.target_center_x = None
                self.bbox_h = None
        else:
            self.target_center_x = None
            self.bbox_h = None




        # -------------------------------
        #   🔥 FSM STATE UPDATE LOGIC
        # -------------------------------
        if self.target_center_x is not None:
            # ---- TRACKING ----
            if self.state != "TRACKING":
                print(">> Reacquired → TRACKING")
            self.state = "TRACKING"
            self.lost_frames = 0

        else:
            # ---- LOST START ----
            if self.state == "TRACKING":
                print(">> Target Lost → LOST")
                self.state = "LOST"
                self.lost_frames = 1

            # ---- LOST CONTINUE ----
            elif self.state == "LOST":
                self.lost_frames += 1
                if self.lost_frames > self.lost_threshold:
                    print(">> LOST threshold exceeded → SEARCHING")
                    self.state = "SEARCHING"

            # ---- SEARCHING STAY ----
            elif self.state == "SEARCHING":
                pass


        # FPS 계산 (간단)
        self._frame_count += 1
        if time.time() - self._last_time >= 1.0:
            self._fps = self._frame_count / (time.time() - self._last_time)
            self._frame_count = 0
            self._last_time = time.time()

        # Visualization overlay
        overlay = frame.copy()
        if self.target_center_x is not None:
            cv2.circle(overlay, (self.target_center_x, cy), 5, (0,0,255), -1)
            cv2.drawContours(overlay, [largest], -1, (0,255,0), 2)
        # center line
        cv2.line(overlay, (self.image_width//2,0), (self.image_width//2, frame.shape[0]), (255,0,0),1)

        # text: fps and status
        status_text = f"FPS: {self._fps:.1f}"
        if self.target_center_x is not None:
            err = self.target_center_x - self.image_width // 2
            status_text += f" | Error: {err}"
        else:
            status_text += " | Target: None"

        cv2.putText(overlay, status_text, (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 1)

        cv2.imshow('Tracking', overlay)
        cv2.imshow('Mask', mask)
        cv2.waitKey(1)

    def load_hsv_params(self):
        default_params = {
            "lower": [35, 100, 100],
            "upper": [85, 255, 255],
            "kernel_size": 5,
            "open_iter": 1,
            "close_iter": 1,
            "min_contour_area": 200
        }

        if os.path.exists("hsv_params.json"):
            try:
                with open("hsv_params.json", "r") as f:
                    params = json.load(f)
                print(">> Loaded HSV parameters from file.")
                return params
            except:
                print(">> Failed to read hsv_params.json — using defaults.")
                return default_params
        else:
            print(">> hsv_params.json not found — using defaults.")
            return default_params
    

    def publish_cmd(self):
        twist = Twist()

        # ----------------------------
        #   🔥 FSM-BASED CONTROL
        # ----------------------------

        # 1) TRACKING — 정상 추적 제어
        if self.state == "TRACKING":

            # ----------------------------
            #  (A) 각속도 (기존 동일)
            # ----------------------------
            err = (self.target_center_x - self.image_width // 2)
            norm_err = err / float(self.image_width // 2)
            K_ang = 0.8
            ang_z = -K_ang * norm_err
            ang_z = max(min(ang_z, 1.0), -1.0)

            # ----------------------------
            #  (B) 거리 기반 선형 속도
            # ----------------------------

            # bbox_h 없으면(= 작은 contour 탐지 실패) 안전하게 멈춤
            if self.bbox_h is None:
                linear_x = 0.0

            else:
                # 정규화된 높이: 가까울수록 1에 가까움
                h_norm = self.bbox_h / float(self.image_height)

                # 멀면 빠르게, 가까우면 느리게
                max_speed = 0.15
                linear_x = max_speed * (1.0 - min(h_norm, 1.0))

                # 너무 가까우면 STOP(충돌 방지)
                if h_norm > 0.65:
                    linear_x = 0.0

                # 회전 오차가 크면 속도 감속
                linear_x *= (1.0 - min(abs(norm_err), 1.0))

            twist.angular.z = float(ang_z)
            twist.linear.x = float(linear_x)


        # 2) LOST — 약한 추적 유지
        elif self.state == "LOST":
            twist.angular.z = 0.3   # 부드럽게 좌회전하며 재탐색
            twist.linear.x = 0.05

        # 3) SEARCHING — 크게 회전하며 탐색
        elif self.state == "SEARCHING":
            twist.angular.z = 0.6   # 더 강하게 스캔
            twist.linear.x = 0.0    # 이동은 멈춤

        self.cmd_vel_pub.publish(twist)

        # --- 로그 기록 ---
        err = (self.target_center_x - self.image_width // 2) if self.target_center_x is not None else 0
        self.logger.writerow([
            time.time(),
            self.state,
            self.target_center_x if self.target_center_x is not None else -1,
            self.bbox_h if self.bbox_h is not None else -1,
            err,
            self._fps,
            twist.linear.x,
            twist.angular.z
        ])

def main(args=None):
    rclpy.init(args=args)
    node = ColorTracker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.log_file.close()  # 파일 닫기
        node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()

if __name__ == '__main__':
    main()