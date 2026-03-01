from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'bt_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'sounds'), glob('bt_robot/sounds/*.mp3')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='hpmcsg1wl7',
    maintainer_email='hansangu093@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'bt_main = bt_robot.bt_main:main',
            'battery_publisher = bt_robot.battery_publisher:main',
            'yolo_person_detector = bt_robot.yolo_person_detector:main',
        ],
    },
)
