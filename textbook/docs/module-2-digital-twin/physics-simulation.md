---
sidebar_position: 1
title: Physics Simulation Fundamentals
description: Understanding physics engines for realistic humanoid robot simulation
keywords: [gazebo, unity, physics, simulation, digital-twin]
---

# Physics Simulation Fundamentals

## Introduction

Physics simulation is the foundation of digital twin development, enabling safe testing of robot behaviors before hardware deployment. This chapter covers the physics engines used in Gazebo and Unity for humanoid robotics.

## Why Physics Simulation?

Benefits for humanoid robotics:
- **Safety**: Test dangerous scenarios without risk
- **Cost**: Reduce hardware wear and tear
- **Speed**: Iterate faster than real-time
- **Reproducibility**: Consistent test conditions
- **Scalability**: Test multiple scenarios in parallel

## Physics Engine Comparison

### Gazebo (ODE/Bullet/DART)

```xml
<!-- Gazebo world configuration -->
<world name="humanoid_world">
  <physics type="ode">
    <max_step_size>0.001</max_step_size>
    <real_time_factor>1.0</real_time_factor>
    <real_time_update_rate>1000</real_time_update_rate>

    <ode>
      <solver>
        <type>quick</type>
        <iters>50</iters>
        <sor>1.3</sor>
      </solver>
      <constraints>
        <cfm>0.0</cfm>
        <erp>0.2</erp>
        <contact_max_correcting_vel>100.0</contact_max_correcting_vel>
        <contact_surface_layer>0.001</contact_surface_layer>
      </constraints>
    </ode>
  </physics>
</world>
```

### Unity (PhysX)

```csharp
// Unity physics configuration
public class HumanoidPhysics : MonoBehaviour
{
    void Start()
    {
        // Configure physics timestep
        Time.fixedDeltaTime = 0.01f; // 100Hz

        // Set gravity
        Physics.gravity = new Vector3(0, -9.81f, 0);

        // Configure solver iterations
        Physics.defaultSolverIterations = 10;
        Physics.defaultSolverVelocityIterations = 10;
    }
}
```

## Key Physics Concepts

### 1. Rigid Body Dynamics

```python
# ROS 2 Gazebo plugin for humanoid control
class HumanoidGazeboPlugin:
    def update(self, dt):
        # Apply joint torques
        for joint in self.joints:
            torque = self.compute_torque(joint)
            joint.set_force(torque)

        # Read joint states
        positions = [j.position() for j in self.joints]
        velocities = [j.velocity() for j in self.joints]
```

### 2. Contact Dynamics

Contact forces are critical for humanoid balance and locomotion:

```xml
<!-- Gazebo contact sensor -->
<sensor name="foot_contact" type="contact">
  <contact>
    <collision>foot_collision</collision>
  </contact>
  <update_rate>100</update_rate>
</sensor>
```

### 3. Joint Constraints

```xml
<!-- Revolute joint with limits -->
<joint name="knee_joint" type="revolute">
  <axis>
    <xyz>0 1 0</xyz>
    <limit>
      <lower>0.0</lower>
      <upper>2.35</upper>
      <effort>150</effort>
      <velocity>3.0</velocity>
    </limit>
    <dynamics>
      <damping>0.5</damping>
      <friction>0.1</friction>
    </dynamics>
  </axis>
</joint>
```

## Simulation Accuracy vs Performance

### Timestep Selection

```python
# Trade-off between accuracy and speed
TIMESTEPS = {
    'high_accuracy': 0.0001,  # 10kHz - Very slow
    'standard': 0.001,         # 1kHz - Recommended
    'fast': 0.01,              # 100Hz - Less accurate
}
```

### Solver Configuration

```xml
<ode>
  <solver>
    <!-- Quick: Fast but less accurate -->
    <type>quick</type>
    <iters>50</iters>

    <!-- World: Slower but more accurate -->
    <!-- <type>world</type> -->
    <!-- <iters>100</iters> -->
  </solver>
</ode>
```

## Practical Example: Humanoid Walking Simulation

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import WrenchStamped

class WalkingSimulation(Node):
    def __init__(self):
        super().__init__('walking_simulation')

        # Subscribe to contact forces
        self.contact_sub = self.create_subscription(
            WrenchStamped,
            '/foot_contact',
            self.contact_callback,
            10
        )

        # Publish joint commands
        self.joint_pub = self.create_publisher(
            JointState,
            '/joint_commands',
            10
        )

        # Walking controller
        self.phase = 0.0
        self.timer = self.create_timer(0.01, self.control_loop)

    def control_loop(self):
        # Generate walking trajectory
        joint_cmd = self.generate_walking_pattern(self.phase)
        self.joint_pub.publish(joint_cmd)

        self.phase += 0.01

    def contact_callback(self, msg):
        # Monitor ground contact forces
        force_z = msg.wrench.force.z
        if force_z > 100.0:
            self.get_logger().info('Foot contact detected')
```

## Gazebo vs Unity: When to Use Each

**Gazebo**:
- ROS 2 native integration
- Open-source and free
- Strong robotics community
- Better for research

**Unity**:
- Superior graphics and rendering
- Better VR/AR support
- Larger asset ecosystem
- Better for visualization and demos

## Common Simulation Issues

1. **Instability**: Reduce timestep or increase solver iterations
2. **Penetration**: Adjust contact parameters (CFM, ERP)
3. **Jitter**: Increase damping or reduce stiffness
4. **Performance**: Simplify collision geometry

## Best Practices

1. **Start simple**: Test with basic shapes before complex meshes
2. **Validate physics**: Compare simulation to real-world data
3. **Monitor performance**: Track real-time factor
4. **Use appropriate timesteps**: Balance accuracy and speed
5. **Log everything**: Record simulation data for analysis

## Next Steps

Learn how to create realistic rendering and interactive environments for your digital twin.
