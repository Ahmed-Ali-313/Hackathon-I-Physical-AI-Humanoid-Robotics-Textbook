---
sidebar_position: 3
title: Robot Tiers
description: Comparing quadruped proxies and full humanoid platforms
keywords: [unitree, go2, g1, humanoid, quadruped, robot-platforms]
---

# Robot Tiers

## Overview

Humanoid robotics development can begin with more accessible quadruped platforms before progressing to full humanoid systems. This chapter compares different robot tiers and their use cases.

## Tier 1: Quadruped Proxies

### Unitree Go2

**Specifications**:
- **Type**: Quadruped robot
- **Weight**: 15 kg
- **Payload**: 5 kg
- **Speed**: 0-5 m/s
- **Battery**: 8000mAh (1-2 hours runtime)
- **Sensors**:
  - 4x fisheye cameras
  - 1x LiDAR
  - IMU, foot force sensors
- **Compute**: NVIDIA Jetson Orin NX (optional)
- **DOF**: 12 (3 per leg)
- **Price**: ~$2,700

**Advantages**:
- Stable platform for learning locomotion
- Lower cost than humanoids
- Robust and durable
- Good for outdoor testing
- Active community support

**Limitations**:
- No manipulation capabilities
- Different kinematics from humanoids
- Limited to quadruped gaits
- Cannot perform human-like tasks

### Use Cases for Go2

1. **Locomotion Research**
   - Gait generation and optimization
   - Terrain adaptation
   - Balance and stability control

2. **Perception Development**
   - Visual SLAM and navigation
   - Obstacle detection and avoidance
   - Multi-sensor fusion

3. **AI Integration**
   - Reinforcement learning for locomotion
   - Vision-language-action models
   - Autonomous navigation

### Go2 ROS 2 Integration

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState, Image

class Go2Controller(Node):
    def __init__(self):
        super().__init__('go2_controller')

        # Subscribe to camera
        self.camera_sub = self.create_subscription(
            Image,
            '/go2/camera/front',
            self.camera_callback,
            10
        )

        # Subscribe to joint states
        self.joint_sub = self.create_subscription(
            JointState,
            '/go2/joint_states',
            self.joint_callback,
            10
        )

        # Publish velocity commands
        self.cmd_pub = self.create_publisher(
            Twist,
            '/go2/cmd_vel',
            10
        )

    def camera_callback(self, msg):
        # Process camera data
        pass

    def joint_callback(self, msg):
        # Monitor joint states
        pass

    def walk_forward(self, speed=0.5):
        cmd = Twist()
        cmd.linear.x = speed
        self.cmd_pub.publish(cmd)
```

## Tier 2: Full Humanoid Robots

### Unitree G1

**Specifications**:
- **Type**: Full humanoid robot
- **Height**: 1.27 m (standing)
- **Weight**: 35 kg
- **DOF**: 23-43 (depending on configuration)
  - Head: 2 DOF
  - Arms: 7 DOF each (with hands: 12 DOF each)
  - Torso: 3 DOF
  - Legs: 6 DOF each
- **Payload**: 2 kg per hand
- **Battery**: 9000mAh (1-2 hours)
- **Sensors**:
  - 3D LiDAR
  - Depth camera (RealSense D435)
  - IMU, force/torque sensors
  - Microphone array
- **Compute**: NVIDIA Jetson Orin (integrated)
- **Price**: ~$16,000 (base) - $90,000 (advanced)

**Advantages**:
- Full humanoid form factor
- Dexterous manipulation
- Human-like interaction
- Suitable for human environments
- Research-grade platform

**Capabilities**:
- Bipedal walking and running
- Object manipulation and grasping
- Human-robot interaction
- Complex task execution
- AI-driven behaviors

### G1 System Architecture

```python
class G1HumanoidController(Node):
    def __init__(self):
        super().__init__('g1_controller')

        # Joint controllers
        self.head_controller = self.create_publisher(
            JointTrajectory, '/g1/head/command', 10
        )
        self.left_arm_controller = self.create_publisher(
            JointTrajectory, '/g1/left_arm/command', 10
        )
        self.right_arm_controller = self.create_publisher(
            JointTrajectory, '/g1/right_arm/command', 10
        )
        self.torso_controller = self.create_publisher(
            JointTrajectory, '/g1/torso/command', 10
        )
        self.leg_controller = self.create_publisher(
            JointTrajectory, '/g1/legs/command', 10
        )

        # Sensor subscribers
        self.setup_sensors()

    def setup_sensors(self):
        # Camera
        self.camera_sub = self.create_subscription(
            Image, '/g1/camera/rgb', self.camera_callback, 10
        )

        # LiDAR
        self.lidar_sub = self.create_subscription(
            PointCloud2, '/g1/lidar/points', self.lidar_callback, 10
        )

        # IMU
        self.imu_sub = self.create_subscription(
            Imu, '/g1/imu', self.imu_callback, 10
        )

        # Force sensors
        self.force_sub = self.create_subscription(
            WrenchStamped, '/g1/force_torque', self.force_callback, 10
        )

    def walk_to_position(self, x, y, theta):
        # Generate walking trajectory
        trajectory = self.generate_walking_trajectory(x, y, theta)

        # Execute trajectory
        self.leg_controller.publish(trajectory)

    def grasp_object(self, object_pose):
        # Calculate inverse kinematics
        joint_angles = self.calculate_ik(object_pose)

        # Generate arm trajectory
        trajectory = self.create_arm_trajectory(joint_angles)

        # Execute grasp
        self.right_arm_controller.publish(trajectory)
```

## Comparison: Go2 vs G1

### Locomotion

| Feature | Go2 (Quadruped) | G1 (Humanoid) |
|---------|-----------------|---------------|
| Stability | High (4 legs) | Moderate (2 legs) |
| Speed | Up to 5 m/s | Up to 2 m/s |
| Terrain | Excellent | Good |
| Stairs | Limited | Excellent |
| Energy Efficiency | High | Moderate |

### Manipulation

| Feature | Go2 (Quadruped) | G1 (Humanoid) |
|---------|-----------------|---------------|
| Grasping | None | Dexterous hands |
| Reach | N/A | 0.8m workspace |
| Payload | N/A | 2kg per hand |
| DOF | 0 | 12 per arm |

### Cost and Accessibility

| Aspect | Go2 | G1 |
|--------|-----|-----|
| Base Price | $2,700 | $16,000 |
| Full Config | $3,500 | $90,000 |
| Maintenance | Low | Moderate |
| Learning Curve | Moderate | Steep |
| Community | Large | Growing |

## Development Progression

### Phase 1: Simulation (Free)

```bash
# Start with Gazebo/Isaac Sim
# No hardware required
# Learn ROS 2, control algorithms, AI integration
```

### Phase 2: Quadruped Proxy ($3,000-$5,000)

```bash
# Unitree Go2 + accessories
# Learn locomotion, perception, navigation
# Test algorithms on real hardware
# Build confidence with physical systems
```

### Phase 3: Entry Humanoid ($16,000-$30,000)

```bash
# Unitree G1 (base configuration)
# Add manipulation capabilities
# Human-robot interaction
# Full system integration
```

### Phase 4: Advanced Humanoid ($50,000-$100,000)

```bash
# Unitree G1 (advanced configuration)
# Custom sensors and actuators
# Research-grade capabilities
# Production-ready systems
```

## Alternative Platforms

### Other Quadrupeds

**Boston Dynamics Spot**
- Price: ~$75,000
- Industrial-grade
- Extensive API
- Enterprise support

**Anymal C**
- Price: ~$150,000
- Research platform
- Waterproof (IP67)
- Advanced autonomy

### Other Humanoids

**Agility Robotics Digit**
- Price: ~$250,000
- Warehouse automation
- 1.5m tall, 65kg
- Commercial deployment

**Tesla Optimus**
- Price: TBD (target $20,000)
- General-purpose humanoid
- In development
- Future availability

## Practical Recommendations

### For Students and Researchers

1. **Start with simulation** - Master ROS 2 and algorithms
2. **Consider Go2** - Affordable entry to physical robotics
3. **Join communities** - Learn from others' experiences
4. **Build incrementally** - Don't rush to expensive hardware

### For Startups and Labs

1. **Assess use case** - Match robot to application
2. **Budget for accessories** - Sensors, compute, tools
3. **Plan for maintenance** - Parts, repairs, upgrades
4. **Consider leasing** - Some platforms offer rental options

### For Enterprise

1. **Evaluate ROI** - Calculate deployment costs
2. **Pilot programs** - Start small, scale gradually
3. **Support contracts** - Ensure vendor support
4. **Integration planning** - Factor in system integration

## Safety Considerations

### Quadruped Safety

- Lower center of gravity (more stable)
- Less risk of falling on humans
- Predictable motion patterns
- Easier emergency stops

### Humanoid Safety

- Higher fall risk (bipedal)
- Greater reach (collision risk)
- More complex behaviors
- Requires safety protocols

### General Safety Practices

```python
class SafetyMonitor(Node):
    def __init__(self):
        super().__init__('safety_monitor')

        # Emergency stop service
        self.estop_srv = self.create_service(
            Trigger,
            'emergency_stop',
            self.emergency_stop_callback
        )

        # Monitor robot state
        self.timer = self.create_timer(0.1, self.check_safety)

    def check_safety(self):
        # Check battery level
        if self.battery_level < 10:
            self.initiate_safe_shutdown()

        # Check joint limits
        if self.check_joint_limits_exceeded():
            self.emergency_stop()

        # Check collision detection
        if self.collision_detected():
            self.emergency_stop()

    def emergency_stop(self):
        # Stop all motion
        self.publish_zero_velocity()

        # Log event
        self.get_logger().error('EMERGENCY STOP ACTIVATED')
```

## Conclusion

**Choose Go2 if you:**
- Are learning robotics fundamentals
- Focus on locomotion and navigation
- Have budget constraints
- Need a robust outdoor platform

**Choose G1 if you:**
- Need manipulation capabilities
- Require human-like interaction
- Have specific humanoid research goals
- Can invest in advanced hardware

**Start with simulation if you:**
- Are new to robotics
- Want to learn without hardware risk
- Need to prototype algorithms
- Have limited budget

## Resources

- [Unitree Robotics](https://www.unitree.com/)
- [ROS 2 Humble Documentation](https://docs.ros.org/en/humble/)
- [Unitree ROS 2 SDK](https://github.com/unitreerobotics)
- [Humanoid Robotics Community](https://discourse.ros.org/)

## Next Steps

You've completed the hardware requirements section! Return to the course modules to continue your learning journey, or start building your own humanoid robotics system.
