---
sidebar_position: 3
title: Nav2 and Motion Planning
description: Autonomous navigation and path planning for humanoid robots
keywords: [nav2, navigation, path-planning, slam, localization]
---

# Nav2 and Motion Planning

## Introduction

Nav2 (Navigation 2) is the ROS 2 navigation stack that enables autonomous navigation through path planning, obstacle avoidance, and localization. For humanoid robots, Nav2 must be adapted to handle bipedal locomotion constraints.

## Nav2 Architecture

```
Sensors → SLAM → Costmap → Planner → Controller → Robot
  ↓        ↓        ↓          ↓          ↓
Camera  Map     Obstacles   Path      Velocity
LiDAR   Pose    Inflation   Waypoints Commands
```

## Installation and Setup

```bash
# Install Nav2
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup

# Install SLAM Toolbox
sudo apt install ros-humble-slam-toolbox

# Install visualization tools
sudo apt install ros-humble-rviz2
```

## Configuration for Humanoid Robots

### Nav2 Parameters

```yaml
# nav2_params.yaml
bt_navigator:
  ros__parameters:
    use_sim_time: True
    global_frame: map
    robot_base_frame: base_link
    odom_topic: /odom
    bt_loop_duration: 10
    default_server_timeout: 20

controller_server:
  ros__parameters:
    use_sim_time: True
    controller_frequency: 20.0
    min_x_velocity_threshold: 0.001
    min_y_velocity_threshold: 0.5
    min_theta_velocity_threshold: 0.001

    # DWB Controller for humanoid
    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"
      min_vel_x: 0.0
      min_vel_y: 0.0
      max_vel_x: 0.5  # Humanoid walking speed
      max_vel_y: 0.0
      max_vel_theta: 1.0
      min_speed_xy: 0.0
      max_speed_xy: 0.5
      min_speed_theta: 0.0
      acc_lim_x: 0.5
      acc_lim_y: 0.0
      acc_lim_theta: 1.0
      decel_lim_x: -0.5
      decel_lim_y: 0.0
      decel_lim_theta: -1.0

planner_server:
  ros__parameters:
    use_sim_time: True
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner"
      tolerance: 0.5
      use_astar: false
      allow_unknown: true

costmap_2d:
  global_costmap:
    global_costmap:
      ros__parameters:
        update_frequency: 1.0
        publish_frequency: 1.0
        global_frame: map
        robot_base_frame: base_link
        use_sim_time: True
        robot_radius: 0.3  # Humanoid footprint
        resolution: 0.05
        track_unknown_space: true
        plugins: ["static_layer", "obstacle_layer", "inflation_layer"]

  local_costmap:
    local_costmap:
      ros__parameters:
        update_frequency: 5.0
        publish_frequency: 2.0
        global_frame: odom
        robot_base_frame: base_link
        use_sim_time: True
        rolling_window: true
        width: 3
        height: 3
        resolution: 0.05
        robot_radius: 0.3
        plugins: ["obstacle_layer", "inflation_layer"]
```

## SLAM with Humanoid Robots

### SLAM Toolbox Configuration

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'odom_frame': 'odom',
                'map_frame': 'map',
                'base_frame': 'base_link',
                'scan_topic': '/scan',

                # SLAM parameters
                'resolution': 0.05,
                'max_laser_range': 20.0,
                'minimum_travel_distance': 0.2,
                'minimum_travel_heading': 0.2,
                'map_update_interval': 5.0,

                # Loop closure
                'loop_search_maximum_distance': 3.0,
                'do_loop_closing': True,
                'loop_match_minimum_chain_size': 10
            }]
        )
    ])
```

## Path Planning

### Global Planner

```python
import rclpy
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped

class HumanoidNavigator(Node):
    def __init__(self):
        super().__init__('humanoid_navigator')

        # Action client for Nav2
        self.nav_to_pose_client = ActionClient(
            self,
            NavigateToPose,
            'navigate_to_pose'
        )

    def navigate_to_goal(self, x, y, theta):
        # Wait for action server
        self.nav_to_pose_client.wait_for_server()

        # Create goal
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()

        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0

        # Convert theta to quaternion
        goal_msg.pose.pose.orientation.z = np.sin(theta / 2.0)
        goal_msg.pose.pose.orientation.w = np.cos(theta / 2.0)

        # Send goal
        self.get_logger().info(f'Navigating to ({x}, {y}, {theta})')
        send_goal_future = self.nav_to_pose_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        send_goal_future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f'Distance remaining: {feedback.distance_remaining:.2f}m'
        )

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected')
            return

        self.get_logger().info('Goal accepted')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result().result
        self.get_logger().info('Navigation complete!')
```

## Obstacle Avoidance

### Dynamic Window Approach (DWA)

```python
class HumanoidDWA(Node):
    def __init__(self):
        super().__init__('humanoid_dwa')

        # Subscribe to laser scan
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        # Publish velocity commands
        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # DWA parameters
        self.max_speed = 0.5  # m/s
        self.max_yaw_rate = 1.0  # rad/s
        self.robot_radius = 0.3  # m

    def scan_callback(self, msg):
        # Get goal from global planner
        goal = self.get_current_goal()

        # Generate velocity samples
        velocities = self.generate_velocity_samples()

        # Evaluate each velocity
        best_vel = None
        best_score = -float('inf')

        for vel in velocities:
            # Predict trajectory
            trajectory = self.predict_trajectory(vel)

            # Check collision
            if self.check_collision(trajectory, msg):
                continue

            # Score trajectory
            score = self.score_trajectory(trajectory, goal)

            if score > best_score:
                best_score = score
                best_vel = vel

        # Publish best velocity
        if best_vel is not None:
            self.cmd_pub.publish(best_vel)

    def predict_trajectory(self, vel, dt=0.1, steps=20):
        trajectory = []
        x, y, theta = 0.0, 0.0, 0.0

        for _ in range(steps):
            x += vel.linear.x * np.cos(theta) * dt
            y += vel.linear.x * np.sin(theta) * dt
            theta += vel.angular.z * dt
            trajectory.append((x, y, theta))

        return trajectory

    def check_collision(self, trajectory, scan):
        # Check if trajectory intersects obstacles
        for x, y, _ in trajectory:
            if self.point_in_obstacle(x, y, scan):
                return True
        return False

    def score_trajectory(self, trajectory, goal):
        # Distance to goal
        final_x, final_y, final_theta = trajectory[-1]
        dist_to_goal = np.hypot(goal.x - final_x, goal.y - final_y)

        # Heading to goal
        angle_to_goal = np.arctan2(goal.y - final_y, goal.x - final_x)
        heading_diff = abs(angle_to_goal - final_theta)

        # Combined score
        score = -dist_to_goal - 0.5 * heading_diff

        return score
```

## Footstep Planning for Humanoids

### Discrete Footstep Planner

```python
from geometry_msgs.msg import PoseArray, Pose

class FootstepPlanner(Node):
    def __init__(self):
        super().__init__('footstep_planner')

        # Subscribe to goal
        self.goal_sub = self.create_subscription(
            PoseStamped,
            '/goal_pose',
            self.goal_callback,
            10
        )

        # Publish footstep plan
        self.footstep_pub = self.create_publisher(
            PoseArray,
            '/footstep_plan',
            10
        )

        # Footstep parameters
        self.step_length = 0.3  # m
        self.step_width = 0.2   # m

    def goal_callback(self, msg):
        # Plan footsteps from current pose to goal
        footsteps = self.plan_footsteps(
            self.get_current_pose(),
            msg.pose
        )

        # Publish footstep plan
        footstep_array = PoseArray()
        footstep_array.header = msg.header
        footstep_array.poses = footsteps

        self.footstep_pub.publish(footstep_array)

    def plan_footsteps(self, start, goal):
        footsteps = []

        # Calculate number of steps
        distance = np.hypot(
            goal.position.x - start.position.x,
            goal.position.y - start.position.y
        )
        num_steps = int(distance / self.step_length)

        # Generate footsteps
        for i in range(num_steps):
            # Alternate left and right foot
            side = 1 if i % 2 == 0 else -1

            # Calculate footstep pose
            progress = (i + 1) / num_steps
            x = start.position.x + progress * (goal.position.x - start.position.x)
            y = start.position.y + progress * (goal.position.y - start.position.y)
            y += side * self.step_width / 2

            footstep = Pose()
            footstep.position.x = x
            footstep.position.y = y
            footstep.position.z = 0.0

            footsteps.append(footstep)

        return footsteps
```

## Recovery Behaviors

### Humanoid-Specific Recovery

```python
class HumanoidRecovery(Node):
    def __init__(self):
        super().__init__('humanoid_recovery')

        # Recovery behaviors
        self.behaviors = [
            self.clear_costmap,
            self.rotate_in_place,
            self.step_back,
            self.emergency_stop
        ]

    def clear_costmap(self):
        self.get_logger().info('Clearing costmap')
        # Call clear costmap service
        # ...

    def rotate_in_place(self):
        self.get_logger().info('Rotating to find clear path')
        cmd = Twist()
        cmd.angular.z = 0.5

        for _ in range(20):
            self.cmd_pub.publish(cmd)
            time.sleep(0.1)

    def step_back(self):
        self.get_logger().info('Stepping backward')
        cmd = Twist()
        cmd.linear.x = -0.1

        for _ in range(10):
            self.cmd_pub.publish(cmd)
            time.sleep(0.1)

    def emergency_stop(self):
        self.get_logger().warn('Emergency stop activated')
        cmd = Twist()  # Zero velocity
        self.cmd_pub.publish(cmd)
```

## Best Practices

1. **Tune for bipedal locomotion** - Adjust velocity limits for walking
2. **Use appropriate footprint** - Account for humanoid body shape
3. **Implement recovery behaviors** - Handle navigation failures gracefully
4. **Monitor battery/energy** - Plan paths considering energy consumption
5. **Test in simulation first** - Validate navigation before hardware deployment

## Common Issues

- Oscillation due to aggressive controller gains
- Getting stuck in narrow passages
- Poor localization causing navigation failures
- Costmap inflation too conservative or too aggressive

## Next Steps

Explore Vision-Language-Action models for natural language robot control.
