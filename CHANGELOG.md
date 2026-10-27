# Changelog

All notable changes to this project will be documented in this file.

## [1.3.1] - 2026-10-28
### Added & Improved
- **Futuristic Hero Banner**: Designed and integrated a high-resolution, cinematic 16:9 aerospace banner depicting an autonomous multi-UAV swarm in V-formation with glowing cyan mesh network telemetry lines and HUD overlays.
- **Repository Branding**: Modernized `README.md` hero presentation with full-width responsive header and TEKNOFEST competition slogan *"Gökyüzünde Takım Oyunu"*.

## [1.3.0] - 2026-10-28
### Added
- **Core Algorithmic Engines (`swarm_core/algorithms.py`)**:
  - `BoidsController`: 3D Reynolds Flocking with Cohesion, true Alignment, Separation, and Goal Attraction.
  - `FormationController`: Leader-Follower multi-agent formations (`V_SHAPE`, `LINE`, `COLUMN`, `CIRCLE`, `GRID`) with dynamic heading rotation and slot allocation.
  - `ArtificialPotentialField`: APF obstacle avoidance with LiDAR range gradient repulsion and velocity damping.
  - `SearchPatternGenerator`: Search & Rescue coverage generators (Archimedean Expanding Spiral and Boustrophedon Lawnmower sweeps).
  - `AnomalyDetector`: Byzantine fault tolerance & cyber-physical security detecting GNSS spoofing, teleportation, and kinematic violations.
  - `FailSafeManager`: Autonomous health checks, communication blackout monitoring, and Return-to-Launch (RTL) state machine.
- **Enhanced Live Telemetry Dashboard (`swarm_core/dashboard.py`)**:
  - Real-time fleet monitor with centroid $(\bar{X}, \bar{Y}, \bar{Z})$ calculation, swarm dispersion index, connection health, and security status.
- **Post-Mission Analytics & Reporting (`swarm_core/analyze_mission.py`)**:
  - Computes 3D/2D flight distances, velocity profiles, neighbor connectivity, and near-miss metrics.
  - Supports `--report <file.md>` for automated Markdown reports and `--export-summary <file.json>`.
- **Comprehensive Unit Test Suite**:
  - 19 automated tests covering vector mathematics, flocking forces, formations, potential fields, anomaly detection, failsafes, and telemetry analytics.
- **Dependency Manifest**:
  - Added official `requirements.txt`.

### Fixed & Improved
- **Local Pose Integration**: Fixed bug in `node_commander.py` where drone's local position was never subscribed from `mavros/local_position/pose` and self-position broadcasting was missing.
- **Parameter Duplication**: Removed duplicate `enable_logging` parameter declaration.
- **Launch Configurations**: Updated `swarm.launch.py` with dynamic launch arguments (`num_drones`, `formation_type`, `mission_mode`).
- **CI/CD Pipeline**: Upgraded `.github/workflows/ci.yml` with proper `PYTHONPATH` configuration and automated pytest execution.
- **Documentation**: Replaced unsupported Gantt diagram with Mermaid flowchart in `README.md`.

## [1.2.0] - 2026-02-28
### Added
- **Global Swarm Ecosystem**: Comprehensive list of competitions, research labs, and open-source projects.
- **Technical Benchmarking**: Deep comparison between major swarm platforms (Tello, Crazyflie, PX4).
- **SOTA Algorithms**: Documentation on bio-inspired, decentralized, and neural swarm techniques.
- **Mathematical Foundations**: Formalized Laplacian consensus and Potential Fields equations.
- **Cyber-Physical Security**: Mitigation strategies for Jamming, Spoofing, and Anomaly detection.
- **Communication Architecture**: Detailed comparison and hybrid use-case for MAVLink 2 and ROS 2 DDS.
- **Business Model**: SWOT analysis and startup value proposition for Teknofest.
- **Project Management**: GitHub Issue templates for professional collaboration.

### Improved
- README.md structure and professional technical depth.
- Global alignment with international standards (DARPA OFFSET, MBZIRC).
