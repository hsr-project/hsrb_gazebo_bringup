# Copyright (C) 2022 Toyota Motor Corporation
import glob

from setuptools import setup

package_name = 'hsrb_gazebo_bringup'

setup(
    name=package_name,
    version='2.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob.glob('launch/*.py')),
        ('share/' + package_name + '/config', glob.glob('config/*.yaml')),
    ],
    install_requires=['launch', 'setuptools'],
    zip_safe=True,
    maintainer='Keisuke Takeshita',
    maintainer_email='keisuke_takeshita@mail.toyota.co.jp',
    description='Bringup scripts for gazebo simulation',
    license='TMC',
    tests_require=[],
    entry_points={
        'console_scripts': [
            'odom_relay = ' + package_name + '.odom_relay:main'
        ],
    },
)
