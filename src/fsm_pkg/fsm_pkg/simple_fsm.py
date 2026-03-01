import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class SimpleFSM(Node):
    def __init__(self):
        super().__init__('simple_fsm')
        self.subscriber = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )
        self.safe_distance = 0.5  # 50cm 이하일 때 정지
        self.get_logger().info("Simple FSM Node Started")

    def scan_callback(self, msg):
        # 전방 감지: 배열의 마지막 부분 (0도 방향)
        num_samples = len(msg.ranges)
        
        # 전방 ±15도 범위의 데이터를 확인
        # 배열 끝부분과 시작부분을 합쳐서 전방 영역을 만듦
        front_samples = []
        
        # 마지막 10개 샘플 (약 -15도 ~ 0도)
        front_samples.extend(msg.ranges[-10:])
        # 처음 10개 샘플 (약 0도 ~ +15도)  
        front_samples.extend(msg.ranges[:10])
        
        # 무한값이나 NaN 제거
        valid_samples = [d for d in front_samples if not (d == float('inf') or d != d)]
        
        if not valid_samples:
            self.get_logger().warn("No valid front scan data!")
            return
            
        min_distance = min(valid_samples)

        twist = Twist()

        if min_distance < self.safe_distance:
            self.get_logger().info(f"Too close! ({min_distance:.2f} m) → STOP")
            twist.linear.x = 0.0
        else:
            self.get_logger().info(f"Clear ({min_distance:.2f} m) → MOVE")
            twist.linear.x = 0.2

        self.publisher.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = SimpleFSM()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()