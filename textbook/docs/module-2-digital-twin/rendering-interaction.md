---
sidebar_position: 2
title: Rendering and Interactive Environments
description: Creating photorealistic and interactive digital twin environments
keywords: [rendering, unity, gazebo, visualization, interactive]
---

# Rendering and Interactive Environments

## Overview

High-quality rendering and interactive environments are essential for effective digital twins, enabling realistic visualization, human-robot interaction testing, and data generation for AI training.

## Rendering Pipelines

### Gazebo Rendering

```xml
<!-- Gazebo scene configuration -->
<scene>
  <ambient>0.4 0.4 0.4 1</ambient>
  <background>0.7 0.7 0.7 1</background>
  <shadows>true</shadows>
  <grid>false</grid>
</scene>

<!-- Camera sensor with rendering -->
<sensor name="camera" type="camera">
  <camera>
    <horizontal_fov>1.047</horizontal_fov>
    <image>
      <width>1920</width>
      <height>1080</height>
      <format>R8G8B8</format>
    </image>
    <clip>
      <near>0.1</near>
      <far>100</far>
    </clip>
  </camera>
  <update_rate>30</update_rate>
</sensor>
```

### Unity High-Definition Render Pipeline (HDRP)

```csharp
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.HighDefinition;

public class PhotorealisticRenderer : MonoBehaviour
{
    public Volume postProcessVolume;

    void Start()
    {
        // Configure HDRP settings
        var hdCamera = GetComponent<HDAdditionalCameraData>();
        hdCamera.antialiasing = HDAdditionalCameraData.AntialiasingMode.TemporalAntialiasing;

        // Enable ray tracing (if supported)
        if (SystemInfo.supportsRayTracing)
        {
            hdCamera.customRenderingSettings = true;
            hdCamera.renderingPathCustomFrameSettings.SetEnabled(
                FrameSettingsField.RayTracing, true
            );
        }

        // Configure post-processing
        ConfigurePostProcessing();
    }

    void ConfigurePostProcessing()
    {
        if (postProcessVolume.profile.TryGet<Bloom>(out var bloom))
        {
            bloom.intensity.value = 0.3f;
            bloom.threshold.value = 1.0f;
        }

        if (postProcessVolume.profile.TryGet<DepthOfField>(out var dof))
        {
            dof.focusDistance.value = 5.0f;
            dof.aperture.value = 5.6f;
        }
    }
}
```

## Lighting Systems

### Dynamic Lighting

```csharp
public class DynamicLighting : MonoBehaviour
{
    public Light sunLight;
    public float dayDuration = 120f; // 2 minutes per day cycle

    void Update()
    {
        // Simulate day/night cycle
        float time = (Time.time % dayDuration) / dayDuration;
        float angle = time * 360f - 90f;

        sunLight.transform.rotation = Quaternion.Euler(angle, 170f, 0f);

        // Adjust intensity based on time
        sunLight.intensity = Mathf.Lerp(0.1f, 1.0f,
            Mathf.Clamp01(Mathf.Sin(time * Mathf.PI * 2f)));
    }
}
```

## Interactive Elements

### Object Manipulation

```csharp
public class InteractiveObject : MonoBehaviour
{
    private Rigidbody rb;
    private bool isGrabbed = false;

    void Start()
    {
        rb = GetComponent<Rigidbody>();
    }

    public void Grab(Transform hand)
    {
        isGrabbed = true;
        rb.isKinematic = true;
        transform.SetParent(hand);
    }

    public void Release()
    {
        isGrabbed = false;
        rb.isKinematic = false;
        transform.SetParent(null);

        // Apply release velocity
        rb.velocity = CalculateReleaseVelocity();
    }
}
```

### ROS 2 Integration for Interactive Control

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
from std_srvs.srv import Trigger

class InteractiveEnvironment(Node):
    def __init__(self):
        super().__init__('interactive_environment')

        # Service to spawn objects
        self.spawn_srv = self.create_service(
            Trigger,
            'spawn_object',
            self.spawn_object_callback
        )

        # Publisher for object poses
        self.pose_pub = self.create_publisher(
            Pose,
            'object_poses',
            10
        )

    def spawn_object_callback(self, request, response):
        # Spawn interactive object in simulation
        self.spawn_object_at_random_location()
        response.success = True
        response.message = 'Object spawned'
        return response
```

## Material Systems

### Physically-Based Rendering (PBR)

```csharp
public class PBRMaterialController : MonoBehaviour
{
    public Material robotMaterial;

    void ConfigurePBRMaterial()
    {
        // Metallic workflow
        robotMaterial.SetFloat("_Metallic", 0.8f);
        robotMaterial.SetFloat("_Smoothness", 0.6f);

        // Normal mapping
        robotMaterial.EnableKeyword("_NORMALMAP");

        // Emission for LED indicators
        robotMaterial.EnableKeyword("_EMISSION");
        robotMaterial.SetColor("_EmissionColor", Color.blue * 2f);
    }
}
```

## Performance Optimization

### Level of Detail (LOD)

```csharp
public class LODManager : MonoBehaviour
{
    public GameObject[] lodLevels;
    public float[] lodDistances = { 10f, 25f, 50f };

    void Update()
    {
        float distance = Vector3.Distance(
            transform.position,
            Camera.main.transform.position
        );

        // Switch LOD based on distance
        for (int i = 0; i < lodLevels.Length; i++)
        {
            bool shouldShow = (i == 0 && distance < lodDistances[0]) ||
                            (i > 0 && distance >= lodDistances[i-1] &&
                             distance < lodDistances[i]);
            lodLevels[i].SetActive(shouldShow);
        }
    }
}
```

### Occlusion Culling

```csharp
void Start()
{
    // Enable occlusion culling
    Camera.main.useOcclusionCulling = true;

    // Bake occlusion data in Unity Editor:
    // Window > Rendering > Occlusion Culling
}
```

## Data Generation for AI Training

### Synthetic Data Pipeline

```python
class SyntheticDataGenerator(Node):
    def __init__(self):
        super().__init__('synthetic_data_generator')

        # Subscribe to camera feeds
        self.rgb_sub = self.create_subscription(
            Image, '/camera/rgb', self.rgb_callback, 10
        )
        self.depth_sub = self.create_subscription(
            Image, '/camera/depth', self.depth_callback, 10
        )

        # Storage for training data
        self.dataset_path = '/data/synthetic_humanoid/'

    def rgb_callback(self, msg):
        # Save RGB image with annotations
        cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

        # Add bounding boxes, segmentation masks
        annotated = self.add_annotations(cv_image)

        # Save to dataset
        self.save_training_sample(annotated)
```

## VR/AR Integration

### Unity XR Toolkit

```csharp
using UnityEngine.XR.Interaction.Toolkit;

public class VRHumanoidController : MonoBehaviour
{
    public XRController leftController;
    public XRController rightController;

    void Update()
    {
        // Map VR controller input to robot commands
        if (rightController.inputDevice.TryGetFeatureValue(
            CommonUsages.trigger, out float triggerValue))
        {
            if (triggerValue > 0.5f)
            {
                SendGraspCommand();
            }
        }
    }

    void SendGraspCommand()
    {
        // Send command to ROS 2
        var msg = new ROS2Message();
        msg.command = "grasp";
        ros2Publisher.Publish(msg);
    }
}
```

## Best Practices

1. **Balance quality and performance** - Use LOD and culling
2. **Leverage GPU acceleration** - Offload rendering to GPU
3. **Use asset streaming** - Load assets on-demand
4. **Implement proper lighting** - Use baked lighting where possible
5. **Test on target hardware** - Ensure performance meets requirements

## Common Issues

- Frame rate drops with complex scenes
- Memory leaks from improper asset management
- Lighting artifacts from incorrect settings
- Physics-rendering synchronization issues

## Next Steps

Learn how to simulate realistic sensors for perception system development.
