---
sidebar_position: 1
title: ROS 2 Middleware Architecture
description: Understanding the DDS-based middleware that powers ROS 2 communication
keywords: [ros2, middleware, dds, communication]
---

# ROS 2 Middleware Architecture

## Introduction

ROS 2 (Robot Operating System 2) represents a fundamental shift in robotic middleware design, built on top of the Data Distribution Service (DDS) standard. This chapter explores the architectural foundations that make ROS 2 suitable for production robotics systems.

## What is Middleware?

Middleware acts as the "nervous system" of a robot, enabling different software components to communicate seamlessly. In ROS 2, this communication layer is built on DDS, providing:

- **Real-time communication** for time-critical robot control
- **Quality of Service (QoS)** policies for reliable data delivery
- **Discovery mechanisms** for automatic node detection
- **Security features** for production deployments

## DDS: The Foundation

The Data Distribution Service (DDS) is an industry-standard protocol that provides:

```python
# Example: Creating a ROS 2 node with custom QoS
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class MiddlewareDemo(Node):
    def __init__(self):
        super().__init__('middleware_demo')

        # Define QoS profile for reliable communication
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.publisher = self.create_publisher(
            String,
            'robot_status',
            qos_profile
        )
```

## Key Concepts

### 1. Quality of Service (QoS)

QoS policies determine how messages are delivered between nodes:

- **Reliability**: Best-effort vs. reliable delivery
- **Durability**: Transient-local vs. volatile data
- **History**: Keep-last vs. keep-all message buffering

### 2. Discovery

ROS 2 nodes automatically discover each other on the network without requiring a central master (unlike ROS 1).

### 3. Security

Built-in support for DDS Security (SROS2) enables encrypted communication and access control.

## Practical Applications

In humanoid robotics, the middleware layer handles:

- Sensor data streams (cameras, IMUs, force sensors)
- Motor control commands at high frequencies
- State estimation and localization data
- High-level planning and decision-making

## Next Steps

In the next chapter, we'll explore how to create nodes, topics, and services to build distributed robotic systems.

## Further Reading

- [ROS 2 Design Documentation](https://design.ros2.org/)
- [DDS Specification](https://www.omg.org/spec/DDS/)
- [ROS 2 QoS Policies](https://docs.ros.org/en/rolling/Concepts/About-Quality-of-Service-Settings.html)
