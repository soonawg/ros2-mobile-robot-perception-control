import rclpy
from rclpy.node import Node
import py_trees
import time

from bt_robot.battery_checker import CheckBattery
from bt_robot.detect_person import DetectPerson
from bt_robot.warn_and_stop import WarnAndStop
from bt_robot.patrol import Patrol

class BehaviorTreeNode(Node):
    def __init__(self):
        super().__init__('behavior_tree_node')

        # 트리 구성
        self.tree = self.create_behavior_tree()
        self.behaviour_tree = py_trees.trees.BehaviourTree(self.tree)
        self.behaviour_tree.setup(timeout=15)

        self.timer = self.create_timer(1.0, self.tick_tree)
        self.get_logger().info("Behavior Tree started")
    
    
    def create_behavior_tree(self):
        # 루트 시퀀스
        root = py_trees.composites.Sequence("Root", memory=True)
        
        # 1. 배터리 체크 (항상 실행)
        check_battery = CheckBattery()
        
        # 2. 사람 감지와 순찰을 위한 병렬 노드
        parallel = py_trees.composites.Parallel(
            name="PersonDetectionAndPatrol",
            policy=py_trees.common.ParallelPolicy.SuccessOnAll(synchronise=False)
        )
        
        # 2-1. 사람 감지 시퀀스 (우선순위가 높음)
        person_detected_seq = py_trees.composites.Sequence("PersonDetectedSequence", memory=True)
        detect_person = DetectPerson()
        warn_and_stop = WarnAndStop()
        person_detected_seq.add_children([detect_person, warn_and_stop])
        
        # 2-2. 순찰 액션
        patrol = Patrol()
        
        # 2-3. 사람 감지와 순찰을 병렬로 실행하되, 사람 감지가 우선순위를 갖도록 Selector 사용
        patrol_selector = py_trees.composites.Selector("PatrolSelector", memory=False)
        patrol_selector.add_children([person_detected_seq, patrol])
        
        parallel.add_children([check_battery, patrol_selector])
        
        # 트리 구성
        root.add_child(parallel)
        
        return root
    
    def tick_tree(self):
        self.behaviour_tree.tick()

def main(args=None):
    rclpy.init(args=args)
    node = BehaviorTreeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()



# def main(args=None):
#     rclpy.init(args=args)
#     node = BehaviorTreeNode()
#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         pass
#     node.destroy_node()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()



# Root (Sequence)
# ├── CheckBattery (Condition)
# ├── PatrolSelector (Selector)
# │   ├── PersonDetectedSequence (Sequence)
# │   │   ├── DetectPerson (Condition)
# │   │   └── WarnAndStop (Action)
# │   └── Patrol (Action)

# =>

# Root (Sequence)
# ├── CheckBattery (Condition)
# └── Selector (PatrolSelector)
#     ├── PersonDetectedSequence (Sequence)
#     │   ├── DetectPerson (Condition)
#     │   └── WarnAndStop (Action)
#     └── Patrol (Action)

# =>

# Root (Sequence)
# └── Parallel (PersonDetectionAndPatrol, SuccessOnAll)
#     ├── CheckBattery (Condition)
#     └── Selector (PatrolSelector)
#         ├── PersonDetectedSequence (Sequence)
#         │   ├── DetectPerson (Condition)
#         │   └── WarnAndStop (Action)
#         └── Patrol (Action)

# =>

# Root (Sequence, memory=False)
# ├── CheckBattery (Condition)
# └── Selector (memory=False)
#     ├── PersonDetectedSequence (Sequence)
#     │   ├── DetectPerson (Condition)  [사람 있으면 SUCCESS, 없으면 FAILURE]
#     │   └── WarnAndStop (Action)      [경고음 재생 + 정지, 계속 RUNNING]
#     └── Patrol (Action)                [사람 없으면 순찰, RUNNING or SUCCESS]
