---
sidebar_position: 1
title: Workstations
description: GPU workstation requirements for robotics development
keywords: [workstation, gpu, nvidia, rtx, ubuntu]
---

# Workstations

## Overview

A powerful GPU workstation is essential for robotics development, enabling simulation, AI training, and real-time perception. This chapter covers the hardware specifications needed for effective humanoid robotics work.

## Minimum Requirements

### GPU

**NVIDIA RTX GPU (12GB+ VRAM)**

- **Recommended**: RTX 4070 Ti, RTX 4080, RTX 4090
- **Minimum**: RTX 3060 (12GB), RTX 3070, RTX 3080

**Why NVIDIA?**
- CUDA support for Isaac Sim and Isaac ROS
- TensorRT for optimized AI inference
- RTX ray tracing for photorealistic simulation
- Extensive robotics software ecosystem

### CPU

**Multi-Core Processor**

- **Recommended**: AMD Ryzen 9 7950X, Intel Core i9-13900K
- **Minimum**: AMD Ryzen 7 5800X, Intel Core i7-12700K

**Requirements**:
- 8+ cores for parallel simulation
- High single-thread performance for ROS 2
- AVX2 instruction set support

### RAM

**32GB+ DDR4/DDR5**

- **Recommended**: 64GB DDR5-5600
- **Minimum**: 32GB DDR4-3200

**Usage**:
- Isaac Sim: 16-32GB
- Multiple ROS 2 nodes: 4-8GB
- AI model training: 8-16GB
- Operating system: 4GB

### Storage

**NVMe SSD (1TB+)**

- **Recommended**: 2TB PCIe 4.0 NVMe SSD
- **Minimum**: 1TB PCIe 3.0 NVMe SSD

**Requirements**:
- Fast read/write for simulation data
- Large datasets for AI training
- Multiple OS installations (dual boot)

## Operating System

### Ubuntu 22.04 LTS

**Why Ubuntu?**
- Official ROS 2 Humble support
- NVIDIA driver compatibility
- Large robotics community
- Long-term support (5 years)

### Installation

```bash
# Download Ubuntu 22.04 LTS
# https://ubuntu.com/download/desktop

# Create bootable USB
sudo dd if=ubuntu-22.04-desktop-amd64.iso of=/dev/sdX bs=4M status=progress

# Install with:
# - Minimal installation
# - Install third-party drivers
# - Erase disk and install Ubuntu (or dual boot)
```

### Post-Installation Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install build essentials
sudo apt install -y \
    build-essential \
    cmake \
    git \
    curl \
    wget \
    vim

# Install NVIDIA drivers
sudo ubuntu-drivers autoinstall
sudo reboot

# Verify GPU
nvidia-smi
```

## NVIDIA Software Stack

### CUDA Toolkit

```bash
# Install CUDA 12.x
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt install -y cuda-toolkit-12-3

# Add to PATH
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# Verify installation
nvcc --version
```

### cuDNN

```bash
# Download cuDNN from NVIDIA website
# https://developer.nvidia.com/cudnn

# Install
sudo dpkg -i cudnn-local-repo-ubuntu2204-8.9.7.29_1.0-1_amd64.deb
sudo cp /var/cudnn-local-repo-ubuntu2204-8.9.7.29/cudnn-local-*-keyring.gpg /usr/share/keyrings/
sudo apt update
sudo apt install -y libcudnn8 libcudnn8-dev
```

### TensorRT

```bash
# Install TensorRT
sudo apt install -y tensorrt

# Verify
dpkg -l | grep TensorRT
```

## ROS 2 Installation

```bash
# Add ROS 2 repository
sudo apt install -y software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install -y curl

sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Install ROS 2 Humble
sudo apt update
sudo apt install -y ros-humble-desktop

# Install development tools
sudo apt install -y \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool

# Initialize rosdep
sudo rosdep init
rosdep update

# Setup environment
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

## Development Tools

### Visual Studio Code

```bash
# Install VS Code
sudo snap install code --classic

# Install extensions
code --install-extension ms-python.python
code --install-extension ms-vscode.cpptools
code --install-extension ms-iot.vscode-ros
```

### Docker

```bash
# Install Docker
sudo apt install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker

# Test GPU in Docker
docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi
```

## Performance Optimization

### GPU Settings

```bash
# Set GPU to maximum performance
sudo nvidia-smi -pm 1
sudo nvidia-smi -pl 350  # Set power limit (adjust for your GPU)

# Enable persistence mode
sudo nvidia-smi -pm ENABLED
```

### System Tuning

```bash
# Increase file descriptor limits
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize network settings
sudo sysctl -w net.core.rmem_max=134217728
sudo sysctl -w net.core.wmem_max=134217728
```

## Recommended Workstation Builds

### Budget Build ($2,000-$3,000)

- **GPU**: NVIDIA RTX 4070 Ti (12GB)
- **CPU**: AMD Ryzen 7 7700X
- **RAM**: 32GB DDR5-5600
- **Storage**: 1TB NVMe SSD
- **PSU**: 750W 80+ Gold

### Professional Build ($4,000-$6,000)

- **GPU**: NVIDIA RTX 4080 (16GB)
- **CPU**: AMD Ryzen 9 7950X
- **RAM**: 64GB DDR5-6000
- **Storage**: 2TB NVMe SSD
- **PSU**: 850W 80+ Platinum

### High-End Build ($8,000+)

- **GPU**: NVIDIA RTX 4090 (24GB) or dual RTX 4080
- **CPU**: AMD Threadripper PRO 5975WX
- **RAM**: 128GB DDR4-3200 ECC
- **Storage**: 4TB NVMe SSD (RAID 0)
- **PSU**: 1200W 80+ Titanium

## Troubleshooting

### GPU Not Detected

```bash
# Check GPU
lspci | grep -i nvidia

# Reinstall drivers
sudo apt purge nvidia-*
sudo ubuntu-drivers autoinstall
sudo reboot
```

### CUDA Version Mismatch

```bash
# Check CUDA version
nvcc --version
nvidia-smi  # Shows driver CUDA version

# Install specific CUDA version
sudo apt install cuda-toolkit-12-3
```

### Out of Memory Errors

```bash
# Monitor GPU memory
watch -n 1 nvidia-smi

# Clear GPU memory
sudo fuser -v /dev/nvidia*
sudo kill -9 <PID>
```

## Next Steps

Learn about edge computing hardware for deploying robots in the field.
