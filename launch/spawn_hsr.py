#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2021 TOYOTA MOTOR CORPORATION
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

#  * Redistributions of source code must retain the above copyright notice,
#  this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#  notice, this list of conditions and the following disclaimer in the
#  documentation and/or other materials provided with the distribution.
#  * Neither the name of Toyota Motor Corporation nor the names of its
#  contributors may be used to endorse or promote products derived from
#  this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    RegisterEventHandler,
)
from launch.event_handlers import OnProcessExit
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def load_robot_description():
    # TODO(Takeshita) Use uplaod launch at hsrb/c_robot_description
    description_package = LaunchConfiguration('description_package')
    description_file = LaunchConfiguration('description_file')
    robot_description_content = Command(
        [PathJoinSubstitution([FindExecutable(name='xacro')]), ' ',
         PathJoinSubstitution([FindPackageShare(description_package), 'robots', description_file]), ' ',
         'gazebo_sim:=True'])
    return {'robot_description': robot_description_content}


def get_loading_controller_process(controller_name, output='screen'):
    return ExecuteProcess(
        cmd=['ros2', 'control', 'load_start_controller', controller_name],
        output=output)


def make_static_transform_publisher(parent_frame, child_frame):
    node_name = parent_frame + '_to_' + child_frame + '_publisher'
    return Node(package='tf2_ros',
                executable='static_transform_publisher',
                name=node_name,
                output='log',
                arguments=['0.0', '0.0', '0.0', '0.0', '0.0', '0.0', parent_frame, child_frame])


def declare_arguments():
    declared_arguments = []
    declared_arguments.append(DeclareLaunchArgument('description_package', default_value='hsrb_description',
                                                    description='Description package with robot URDF/xacro files.'))
    declared_arguments.append(DeclareLaunchArgument('description_file', default_value='hsrb4s.urdf.xacro',
                                                    description='URDF/XACRO description file with the robot.'))
    return declared_arguments


def generate_launch_description():
    robot_description = load_robot_description()

    spawn_entity = Node(
        package='gazebo_ros', executable='spawn_entity.py', output='screen',
        arguments=['-topic', 'robot_description', '-entity', 'hsrb'])

    load_joint_state_controller = get_loading_controller_process('joint_state_controller')
    load_head_trajectory_controller = get_loading_controller_process('head_trajectory_controller')
    load_arm_trajectory_controller = get_loading_controller_process('arm_trajectory_controller')
    load_omni_base_controller = get_loading_controller_process('omni_base_controller')
    # It is difficutl to remap with gazebo_ros2_control
    # And migaration of topic_tools not yet
    odom_relay_node = Node(
        package='hsrb_gazebo_bringup', executable='odom_relay', name='odom_relay',
        remappings=[('~/input_odom', 'omni_base_controller/wheel_odom'),
                    ('~/output_odom', 'odom')])

    wheel_odom_connector_tf = Node(package='tf2_ros',
                                   executable='static_transform_publisher',
                                   name='static_transform_publisher',
                                   output='log',
                                   arguments=['0.0', '0.0', '0.0', '0.0', '0.0', '0.0',
                                              'base_footprint_wheel', 'base_footprint'])
    joint_state_publisher = Node(package='joint_state_publisher',
                                 executable='joint_state_publisher',
                                 parameters=[{'source_list': ['/joint_states'], 'use_sim_time': True}],
                                 namespace='whole_body',
                                 remappings=[('robot_description', '/robot_description')])
    robot_state_publisher = Node(package='robot_state_publisher',
                                 executable='robot_state_publisher',
                                 parameters=[robot_description, {'use_sim_time': True}],
                                 namespace='whole_body',
                                 output={'both': 'log'},
                                 remappings=[('robot_description', '/robot_description')])

    static_transform_publishers = [
        make_static_transform_publisher('head_l_stereo_camera_link', 'head_l_stereo_camera_frame'),
        make_static_transform_publisher('head_r_stereo_camera_link', 'head_r_stereo_camera_frame'),
        make_static_transform_publisher('head_rgbd_sensor_link', 'head_rgbd_sensor_rgb_frame'),
        make_static_transform_publisher('head_rgbd_sensor_link', 'head_rgbd_sensor_depth_frame')]

    return LaunchDescription(
        declare_arguments()
        + [RegisterEventHandler(
            event_handler=OnProcessExit(target_action=spawn_entity,
                                        on_exit=[load_joint_state_controller,
                                                 load_head_trajectory_controller,
                                                 load_arm_trajectory_controller,
                                                 load_omni_base_controller])),
            joint_state_publisher, robot_state_publisher, spawn_entity, odom_relay_node, wheel_odom_connector_tf]
        + static_transform_publishers)
