---
sidebar_position: 2
title: Nodes, Topics, and Services
description: Building distributed robotic systems with ROS 2 communication patterns
keywords: [ros2, nodes, topics, services, pub-sub]
---

# Nodes, Topics, and Services

## Overview

ROS 2 applications are built from modular components called **nodes** that communicate through **topics** (publish-subscribe) and **services** (request-response).

## Nodes: The Building Blocks

A node is an independent process that performs a specific task in your robotic system.

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class HumanoidController(Node):
    def __init__(self):
        super().__init__('humanoid_controller')
        self.get_logger().info('Humanoid controller initialized')

    def run(self):
        # Main control loop
        pass

def main(args=None):
    rclpy.init(args=args)
    controller = HumanoidController()
    rclpy.spin(controller)
    controller.destroy_node()
    rclpy.shutdown()
```

## Topics: Publish-Subscribe Communication

Topics enable one-to-many communication where publishers send data and subscribers receive it.

```python
# Publisher example
self.joint_state_pub = self.create_publisher(
    JointState,
    'joint_states',
    10
)

# Subscriber example
self.imu_sub = self.create_subscription(
    Imu,
    'imu/data',
    self.imu_callback,
    10
)

def imu_callback(self, msg):
    self.get_logger().info(f'IMU orientation: {msg.orientation}')
```

## Services: Request-Response Pattern

Services provide synchronous communication for operations that require a response.

```python
from example_interfaces.srv import SetBool

# Service server
self.enable_srv = self.create_service(
    SetBool,
    'enable_motors',
    self.enable_motors_callback
)

def enable_motors_callback(self, request, response):
    if request.data:
        # Enable motors
        response.success = True
        response.message = 'Motors enabled'
    else:
        # Disable motors
        response.success = True
        response.message = 'Motors disabled'
    return response
```

## Practical Example: Humanoid Balance Controller

```python
class BalanceController(Node):
    def __init__(self):
        super().__init__('balance_controller')

        # Subscribe to IMU data
        self.imu_sub = self.create_subscription(
            Imu, 'imu/data', self.imu_callback, 10
        )

        # Publish joint commands
        self.joint_cmd_pub = self.create_publisher(
            JointTrajectory, 'joint_commands', 10
        )

        # Service for emergency stop
        self.estop_srv = self.create_service(
            Trigger, 'emergency_stop', self.estop_callback
        )

    def imu_callback(self, msg):
        # Calculate balance correction
        correction = self.calculate_balance(msg)
        self.publish_joint_commands(correction)
```

## Best Practices

1. **Single Responsibility**: Each node should have one clear purpose
2. **Namespace Organization**: Use namespaces to group related topics
3. **QoS Configuration**: Choose appropriate QoS policies for each topic
4. **Error Handling**: Always handle communication failures gracefully

## Next Steps

Learn how to bridge ROS 2 with Python applications for AI integration.
