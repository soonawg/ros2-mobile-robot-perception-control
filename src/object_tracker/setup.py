from setuptools import find_packages, setup

package_name = 'object_tracker'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/object_tracker.launch.py']),
    ],
    install_requires=[
        'setuptools',
        'rclpy',
        'sensor_msgs',
        'std_msgs',
        'geometry_msgs',
        'cv_bridge',
        'ultralytics',
        'opencv-python'
    ],
    zip_safe=True,
    maintainer='soonawg',
    maintainer_email='hansangu093@gmail.com',
    description='YOLO 기반 물체 인식 및 추적, Turtlebot3 제어 ROS2 패키지',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'perception_node = object_tracker.perception_node:main',
            'tracker_node = object_tracker.tracker_node:main',
        ],
    },
)
