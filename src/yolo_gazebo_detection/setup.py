from setuptools import setup
import os
from glob import glob

package_name = 'yolo_gazebo_detection'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.world')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'models'), glob('models/**/*', recursive=True)),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='hpmcsg1wl7',
    maintainer_email='hansangu093@gmail.com',
    description='YOLOv8 real-time object detection with Gazebo simulator',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'yolo_detector = yolo_gazebo_detection.yolo_detector:main',
            'gazebo_camera = yolo_gazebo_detection.gazebo_camera:main',
            'visualization = yolo_gazebo_detection.visualization:main',
            'robot_controller = yolo_gazebo_detection.robot_controller:main',
        ],
    },
)