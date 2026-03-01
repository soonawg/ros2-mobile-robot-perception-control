import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
import numpy as np
import sensor_msgs_py.point_cloud2 as pc2
import open3d as o3d

# pointcloud2에서 검출한 포인트 클라우드를 바닥과 물체를 분리하는 코드 (단 위치만 검출)

class PointCloudProcessorOpen3D(Node):

    def __init__(self):
        super().__init__('point_cloud_processor_open3d')
        
        # 1. 구독자 설정: Gazebo에서 발행되는 PointCloud2 토픽 구독
        self.subscription = self.create_subscription(
            PointCloud2,
            '/camera/points', # 또는 /camera/depth/points 등
            self.pointcloud_callback,
            10
        )
        self.get_logger().info("Open3D PointCloud Processor Node has been started.")

        # 2. 발행자 설정: 처리된 포인트 클라우드 발행
        self.plane_publisher = self.create_publisher(PointCloud2, 'processed_plane_points', 10)
        self.obstacles_publisher = self.create_publisher(PointCloud2, 'processed_obstacle_points', 10)

    def pointcloud_callback(self, msg: PointCloud2):
        # 메시지에 점 데이터가 없으면 종료
        if msg.width * msg.height == 0:
            return

        # 3. PointCloud2 메시지를 numpy 배열로 변환
        # Open3D가 요구하는 float64 타입으로 변환
        points_list = pc2.read_points_list(msg, field_names=("x", "y", "z"))
        if not points_list:
            return

        np_points = np.array(points_list, dtype=np.float64)

        # 4. numpy 배열을 Open3D PointCloud 객체로 변환
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(np_points)

        # 5. Open3D의 RANSAC 알고리즘으로 평면 분할
        # Open3D는 segment_plane 함수로 평면 분할을 쉽게 할 수 있습니다.
        # distance_threshold: 평면으로 간주할 최대 거리
        # ransac_n: RANSAC 알고리즘을 위한 무작위 샘플 점의 수
        # num_iterations: 반복 횟수
        distance_threshold = 0.02
        ransac_n = 3
        num_iterations = 1000
        
        plane_model, inliers = pcd.segment_plane(distance_threshold, ransac_n, num_iterations)
        
        # 6. 분리된 포인트 클라우드 생성
        if len(inliers) > 0:
            # inliers는 평면에 속하는 점들의 인덱스 리스트
            plane_cloud = pcd.select_by_index(inliers)
            obstacle_cloud = pcd.select_by_index(inliers, invert=True)

            # 7. numpy 배열로 변환하여 ROS2 메시지 발행
            header = msg.header
            
            plane_msg = pc2.create_cloud_xyz32(header, np.asarray(plane_cloud.points))
            obstacle_msg = pc2.create_cloud_xyz32(header, np.asarray(obstacle_cloud.points))
            
            self.plane_publisher.publish(plane_msg)
            self.obstacles_publisher.publish(obstacle_msg)
            
            self.get_logger().info(f"Published a plane with {len(inliers)} points and obstacles.")
        else:
            self.get_logger().info("No plane could be found.")

def main(args=None):
    rclpy.init(args=args)
    node = PointCloudProcessorOpen3D()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()