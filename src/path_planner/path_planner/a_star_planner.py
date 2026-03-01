import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid, Path
from geometry_msgs.msg import PoseStamped
import numpy as np
import heapq

class AStarPlanner(Node):
    def __init__(self):
        super().__init__('a_star_planner')
        self.map_sub = self.create_subscription(
            OccupancyGrid, '/map', self.map_callback, 10)
        self.path_pub = self.create_publisher(Path, '/planned_path', 10)

        self.map_data = None
        self.map_width = 0
        self.map_height = 0
        self.map_resolution = 0.0
        self.map_origin = None

        # 목표지점 예시 (맵 좌표계 기준, 미터 단위)
        self.goal_world = (2.0, 2.0)
        self.start_world = (0.0, 0.0)

    def map_callback(self, msg):
        self.get_logger().info('Map received')
        self.map_data = np.array(msg.data).reshape(msg.info.height, msg.info.width)
        self.map_width = msg.info.width
        self.map_height = msg.info.height
        self.map_resolution = msg.info.resolution
        self.map_origin = msg.info.origin
        # 맵 한 번만 받고 계획 시작
        self.plan_path()

    def world_to_map(self, wx, wy):
        mx = int((wx - self.map_origin.position.x) / self.map_resolution)
        my = int((wy - self.map_origin.position.y) / self.map_resolution)
        return mx, my

    def map_to_world(self, mx, my):
        wx = mx * self.map_resolution + self.map_origin.position.x + self.map_resolution / 2.0
        wy = my * self.map_resolution + self.map_origin.position.y + self.map_resolution / 2.0
        return wx, wy

    def is_free(self, x, y):
        if 0 <= x < self.map_width and 0 <= y < self.map_height:
            # occupancy: -1 unknown, 0 free, 100 occupied
            return self.map_data[y][x] == 0
        return False

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])  # 맨해튼 거리

    def neighbors(self, node):
        x, y = node
        nbrs = [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]  # 4방향 이동
        return [n for n in nbrs if self.is_free(n[0], n[1])]

    def plan_path(self):
        if self.map_data is None:
            self.get_logger().warn('No map data yet')
            return

        start = self.world_to_map(*self.start_world)
        goal = self.world_to_map(*self.goal_world)
        self.get_logger().info(f'Planning from {start} to {goal}')

        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while frontier:
            _, current = heapq.heappop(frontier)
            if current == goal:
                break
            for nxt in self.neighbors(current):
                new_cost = cost_so_far[current] + 1
                if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                    cost_so_far[nxt] = new_cost
                    priority = new_cost + self.heuristic(goal, nxt)
                    heapq.heappush(frontier, (priority, nxt))
                    came_from[nxt] = current

        if goal not in came_from:
            self.get_logger().error('경로를 찾을 수 없습니다!')
            return

        # 경로 역추적
        path = []
        current = goal
        while current:
            path.append(current)
            current = came_from[current]
        path.reverse()

        # nav_msgs/Path 메시지 생성
        path_msg = Path()
        path_msg.header.frame_id = "map"
        path_msg.header.stamp = self.get_clock().now().to_msg()

        for mx, my in path:
            wx, wy = self.map_to_world(mx, my)
            pose = PoseStamped()
            pose.header.frame_id = "map"
            pose.pose.position.x = wx
            pose.pose.position.y = wy
            pose.pose.position.z = 0.0
            pose.pose.orientation.w = 1.0
            path_msg.poses.append(pose)

        self.path_pub.publish(path_msg)
        self.get_logger().info('경로를 퍼블리시 했습니다.')

def main(args=None):
    rclpy.init(args=args)
    node = AStarPlanner()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()


# import rclpy
# from rclpy.node import Node
# from nav_msgs.msg import OccupancyGrid, Path
# from geometry_msgs.msg import PoseStamped, Point
# from std_msgs.msg import Header
# import numpy as np
# import heapq
# import math
# from tf2_ros.buffer import Buffer
# from tf2_ros.transform_listener import TransformListener
# from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy

# class NodeState:
#     """A* 알고리즘의 노드를 표현하는 클래스"""
#     def __init__(self, parent=None, position=None):
#         self.parent = parent
#         self.position = position # 튜플 (row, col)
        
#         self.g = 0 # 시작점에서 현재 노드까지의 비용
#         self.h = 0 # 현재 노드에서 목표까지의 휴리스틱 비용
#         self.f = 0 # 총 비용 (g + h)

#     def __eq__(self, other):
#         return self.position == other.position
    
#     def __lt__(self, other):
#         return self.f < other.f

# class AStarPlanner(Node):
#     def __init__(self):
#         super().__init__('a_star_planner')
        
#         # 1. 지도 구독자
#         qos_profile = QoSProfile(
#             reliability=QoSReliabilityPolicy.RELIABLE,
#             history=QoSHistoryPolicy.KEEP_LAST,
#             depth=1,
#             durability=QoSDurabilityPolicy.TRANSIENT_LOCAL
#         )
#         self.map_subscription = self.create_subscription(
#             OccupancyGrid,
#             '/map',
#             self.map_callback,
#             qos_profile
#         )
#         self.map_data = None
#         self.map_info = None
        
#         # 2. 목표점 구독자 (RViz에서 2D Nav Goal 버튼을 누르면 이 토픽으로 메시지가 발행됩니다.)
#         self.goal_subscription = self.create_subscription(
#             PoseStamped,
#             '/goal_pose', 
#             self.goal_callback,
#             10
#         )
        
#         # 3. 경로 발행자
#         self.path_publisher = self.create_publisher(Path, 'planned_path', 10)
        
#         self.tf_buffer = Buffer()
#         self.tf_listener = TransformListener(self.tf_buffer, self)
        
#         self.get_logger().info('A* Planner Node Started.')

#     def map_callback(self, msg: OccupancyGrid):
#         self.map_data = msg.data
#         self.map_info = msg.info
#         self.get_logger().info('Map data received.')

#     def goal_callback(self, msg: PoseStamped):
#         if self.map_data is None:
#             self.get_logger().warn('No map data received yet. Cannot plan a path.')
#             return
            
#         start_pose = self.get_current_robot_pose()
#         goal_pose = msg.pose
        
#         start_grid = self.world_to_map(start_pose.pose.position.x, start_pose.pose.position.y)
#         goal_grid = self.world_to_map(goal_pose.position.x, goal_pose.position.y)
        
#         if start_grid is None or goal_grid is None:
#             self.get_logger().error("Failed to convert start/goal to grid. Check map info and frames.")
#             return
        
#         if not self.is_valid(start_grid) or not self.is_valid(goal_grid):
#             self.get_logger().error("Start or goal position is outside the map or on an obstacle.")
#             return

#         self.get_logger().info(f"Planning path from {start_grid} to {goal_grid}...")
#         path_nodes = self.a_star_search(start_grid, goal_grid)
        
#         if path_nodes:
#             path_poses = [self.map_to_world(node.position[0], node.position[1]) for node in path_nodes]
#             # 필터: 변환 실패(None) 제거
#             path_poses = [p for p in path_poses if p is not None]
#             if not path_poses:
#                 self.get_logger().warn('Path nodes exist but world conversion failed.')
#                 return
#             self.publish_path(path_poses)
#             self.get_logger().info('Path found and published.')
#         else:
#             self.get_logger().warn('No path found to the goal.')

#     def a_star_search(self, start_grid, goal_grid):
#         """A* 알고리즘의 실제 로직을 구현합니다."""
#         start_node = NodeState(None, start_grid)
#         start_node.g = start_node.h = start_node.f = 0
#         goal_node = NodeState(None, goal_grid)
#         goal_node.g = goal_node.h = goal_node.f = 0

#         open_list = []
#         closed_list = set()

#         heapq.heappush(open_list, (start_node.f, start_node))
        
#         while open_list:
#             current_f, current_node = heapq.heappop(open_list)
            
#             closed_list.add(current_node.position)

#             if current_node.position == goal_node.position:
#                 path = []
#                 current = current_node
#                 while current is not None:
#                     path.append(current)
#                     current = current.parent
#                 return path[::-1] # 경로를 역순으로 반환

#             (row, col) = current_node.position
#             neighbors = [
#                 (row-1, col), (row+1, col), (row, col-1), (row, col+1),
#                 (row-1, col-1), (row-1, col+1), (row+1, col-1), (row+1, col+1)
#             ]
            
#             for next_pos in neighbors:
#                 if not self.is_valid(next_pos) or next_pos in closed_list:
#                     continue
                
#                 # 비용 계산 (대각선 이동 고려)
#                 cost_add = math.sqrt((next_pos[0]-row)**2 + (next_pos[1]-col)**2)
                
#                 neighbor_node = NodeState(current_node, next_pos)
#                 neighbor_node.g = current_node.g + cost_add
#                 neighbor_node.h = self.heuristic(neighbor_node.position, goal_node.position)
#                 neighbor_node.f = neighbor_node.g + neighbor_node.h
                
#                 # open_list에 이미 더 좋은 노드가 있는지 확인
#                 if self.is_better_node_in_open(open_list, neighbor_node):
#                     continue
                
#                 heapq.heappush(open_list, (neighbor_node.f, neighbor_node))

#         return None # 경로를 찾지 못함

#     def heuristic(self, a, b):
#         """유클리디안 거리 휴리스틱 함수"""
#         return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

#     def is_valid(self, pos):
#         """노드가 유효한 위치인지 확인 (지도 밖, 장애물)"""
#         (row, col) = pos
#         if not (0 <= row < self.map_info.height and 0 <= col < self.map_info.width):
#             return False
        
#         index = int(row * self.map_info.width + col)
#         cell = self.map_data[index]
#         # OccupancyGrid: -1(unknown), 0~100. 안전을 위해 unknown도 장애물 취급
#         if cell == -1 or cell > 50:
#             return False
            
#         return True

#     def is_better_node_in_open(self, open_list, neighbor_node):
#         for f, node in open_list:
#             if neighbor_node == node and neighbor_node.g >= node.g:
#                 return True
#         return False
        
#     def world_to_map(self, x, y):
#         """월드 좌표를 지도 격자 좌표로 변환"""
#         if self.map_info is None:
#             return None
#         origin_x = self.map_info.origin.position.x
#         origin_y = self.map_info.origin.position.y
#         resolution = self.map_info.resolution
        
#         col = int((x - origin_x) / resolution)
#         row = int((y - origin_y) / resolution)
#         return (row, col)

#     def map_to_world(self, row, col):
#         """지도 격자 좌표를 월드 좌표로 변환"""
#         if self.map_info is None:
#             return None
#         origin_x = self.map_info.origin.position.x
#         origin_y = self.map_info.origin.position.y
#         resolution = self.map_info.resolution
        
#         # 셀 중심으로 변환
#         x = origin_x + (col + 0.5) * resolution
#         y = origin_y + (row + 0.5) * resolution
        
#         point = Point()
#         point.x = x
#         point.y = y
#         return point

#     def get_current_robot_pose(self):
#         """로봇의 현재 위치를 받아오는 함수 (TF2 사용)"""
#         try:
#             trans = self.tf_buffer.lookup_transform('map', 'base_link', rclpy.time.Time())
#             pose = PoseStamped()
#             pose.header = trans.header
#             pose.pose.position.x = trans.transform.translation.x
#             pose.pose.position.y = trans.transform.translation.y
#             return pose
#         except Exception as e:
#             self.get_logger().error(f"Failed to get current robot pose: {e}")
#             return None

#     def publish_path(self, path_points):
#         """Path 메시지를 만들어 발행"""
#         path_msg = Path()
#         path_msg.header = Header()
#         path_msg.header.stamp = self.get_clock().now().to_msg()
#         path_msg.header.frame_id = "map"
        
#         for point in path_points:
#             pose_stamped = PoseStamped()
#             pose_stamped.header = path_msg.header
#             pose_stamped.pose.position.x = point.x
#             pose_stamped.pose.position.y = point.y
#             path_msg.poses.append(pose_stamped)
        
#         self.path_publisher.publish(path_msg)

# def main(args=None):
#     rclpy.init(args=args)
#     a_star_planner = AStarPlanner()
#     rclpy.spin(a_star_planner)
#     a_star_planner.destroy_node()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()