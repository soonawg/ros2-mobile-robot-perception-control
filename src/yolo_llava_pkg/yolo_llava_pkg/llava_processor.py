#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from PIL import Image as PILImage
from transformers import LlavaNextProcessor, LlavaNextForConditionalGeneration
import torch

class LlavaProcessor(Node):
    def __init__(self):
        super().__init__('llava_processor')
        self.bridge = CvBridge()
        self.processor = LlavaNextProcessor.from_pretrained(
            "llava-hf/llava-v1.6-mistral-7b-hf",
            use_fast=True
        )
        self.model = LlavaNextForConditionalGeneration.from_pretrained(
            "llava-hf/llava-v1.6-mistral-7b-hf", 
            torch_dtype=torch.float16, 
            device_map="auto"
        )
        
        self.subscription = self.create_subscription(
            Image,
            'cropped_object',
            self.image_callback,
            10)
        
    def image_callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        pil_image = PILImage.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
        
        # LLaVA 처리
        prompt = "USER: <image>\nWhat is this object? Provide only the object name.\nASSISTANT:"
        inputs = self.processor(prompt, pil_image, return_tensors="pt").to("cuda")
        
        output = self.model.generate(**inputs, max_new_tokens=20)
        response = self.processor.decode(output[0], skip_special_tokens=True)
        
        # 응답에서 객체 이름 추출
        object_name = response.split("ASSISTANT:")[-1].strip()
        self.get_logger().info(f"Detected object: {object_name}")

def main():
    rclpy.init()
    node = LlavaProcessor()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()