FROM ros:humble-perception

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-colcon-common-extensions \
    python3-pip \
    ros-humble-mavros \
    ros-humble-mavros-msgs \
    ros-humble-gazebo-ros-pkgs \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN pip3 install --no-cache-dir \
    numpy \
    scipy

# Setup workspace
WORKDIR /ws
COPY src /ws/src

# Build workspace
RUN . /opt/ros/humble/setup.sh && colcon build

# Setup entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
