# Changelog

All notable changes to this project will be documented in this file.

## [1.5.0] - 2026-10-28
### Added
- **Computer Vision & Target Geolocation Pipeline (`vision_pipeline.py`)**:
  - `SwarmVisionEngine`: Implemented geometric shape classification (`CIRCLE`, `SQUARE`, `H_PAD`, `CROSS`), color segmentation, and synthetic ground target scanner.
  - `CameraIntrinsics` & Pinhole Model: Calculates 2D image pixel to real-world 3D coordinates $(X_w, Y_w, Z_w)$ projection with camera focal length, principal point, and UAV heading rotation.
- **Market-Based Multi-Agent Task Allocation (`AuctionTaskAllocator`)**:
  - Distributed auction engine assigning discovered ground targets to the optimal UAV factoring in Euclidean distance and remaining battery percentage.
- **Quintic Polynomial Trajectory Smoothing (`TrajectoryGenerator`)**:
  - Generates $C^2$ continuous minimum-jerk position and velocity profiles with zero initial/terminal jerk.
- **Swarm Command-Line Interface (`cli.py`)**:
  - Unified administration tool for live fleet status, formation switching, mission dispatching, and high-speed algorithm benchmarking.
- **Extended Test Suite**:
  - 34 unit tests (up from 27) covering task auctions, quintic spline trajectories, camera pinhole projections, and target classifications with 100% pass rate.

## [1.4.0] - 2026-10-28
### Added
- **Dynamic Leader Election (`LeaderElectionEngine`)**:
  - Decentralized consensus mechanism allowing the swarm to autonomously elect a new leader if the primary leader drops out or is compromised.
- **3D Geofence & NFZ Manager (`GeofenceManager`)**:
  - Enforces competition boundary constraints with restorative barrier potential forces and keep-out cylinder No-Fly Zones.
- **Cooperative Target Recognition (`TargetTracker`)**:
  - Multi-agent target detection and consensus engine to confirm ground targets and eliminate false positives.
- **Interactive Web Ground Control Station (`web_gcs.py`)**:
  - Zero-dependency HTTP/HTML5 tactical GCS with live 2D canvas radar, fleet health telemetry cards, formation control buttons, and event logs on port 8080.
- **TEKNOFEST Referee Bridge (`referee_bridge.py`)**:
  - Competition-compliant telemetry and target detection UDP/JSON packet generation and bridge interface.
- **Fast Multi-UAV SITL Engine (`mock_sitl_bridge.py`)**:
  - Lightweight 6-DoF kinematics and 2D LiDAR raycaster allowing instant swarm simulation without requiring Gazebo.
- **Competition Arena World (`teknofest_arena.world`)**:
  - 3D Gazebo competition world with perimeter pylons, obstacle towers, and QR target markers.
- **Expanded Test Suite**:
  - 27 unit tests (up from 19) covering all algorithmic engines, referee packets, geofence barriers, and physics kinematics.

### Improved
- **Swarm Commander Integration**:
  - Dynamic leader failover and 3D boundary forces directly embedded in `node_commander.py` control loop.
- **Launch Configurations**:
  - `swarm.launch.py` and `simulation.launch.py` updated with `use_mock`, `world`, and safety parameters.

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
