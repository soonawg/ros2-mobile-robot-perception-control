from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'simple_service'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # 서비스 파일 추가
        (os.path.join('share', package_name, 'srv'), glob('srv/*.srv')),
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
            'add_two_ints_server = simple_service.add_two_ints_server:main',
            'add_two_ints_client = simple_service.add_two_ints_client:main',
        ],
    },
)