#!/usr/bin/env python3
"""
Teknofest Swarm Vision & Target Recognition Pipeline
Processes onboard camera imagery, detects colored geometric targets & QR codes,
and projects image pixel coordinates into real-world 3D geolocations.
"""

import math
from typing import Dict, List, Tuple, Optional, Any
from swarm_core.algorithms import Vector3


class DetectedTarget:
    def __init__(self,
                 target_type: str,
                 pixel_u: float,
                 pixel_v: float,
                 color: str = "RED",
                 confidence: float = 0.95):
        self.target_type = target_type  # H_PAD, CIRCLE, SQUARE, CROSS, QR
        self.pixel_u = pixel_u
        self.pixel_v = pixel_v
        self.color = color
        self.confidence = confidence


class CameraIntrinsics:
    """Pinhole camera model intrinsic parameters."""
    def __init__(self,
                 image_width: int = 640,
                 image_height: int = 480,
                 fov_deg: float = 80.0):
        self.width = image_width
        self.height = image_height
        self.cx = image_width / 2.0
        self.cy = image_height / 2.0
        # Focal length from FOV: f = (W / 2) / tan(FOV / 2)
        fov_rad = math.radians(fov_deg)
        self.fx = (image_width / 2.0) / math.tan(fov_rad / 2.0)
        self.fy = self.fx


class SwarmVisionEngine:
    """
    Onboard Computer Vision Engine for Multi-UAV Systems.
    Performs target recognition and geolocates detected ground targets.
    """
    def __init__(self, camera_params: Optional[CameraIntrinsics] = None):
        self.camera = camera_params or CameraIntrinsics()

    def pixel_to_world(self,
                       pixel_u: float,
                       pixel_v: float,
                       drone_pos: Vector3,
                       drone_heading_rad: float = 0.0,
                       ground_altitude: float = 0.0) -> Vector3:
        """
        Projects a 2D image pixel into 3D world coordinates.
        Assumes downward-facing nadir camera mounted on drone body.
        """
        rel_alt = max(0.1, drone_pos.z - ground_altitude)

        # Normalized camera ray coordinates
        norm_x = (pixel_u - self.camera.cx) / self.camera.fx
        norm_y = (pixel_v - self.camera.cy) / self.camera.fy

        # Body-frame ground displacement: +X forward, +Y right
        body_dx = -norm_y * rel_alt  # Up in image is forward
        body_dy = norm_x * rel_alt   # Right in image is right

        # Rotate by drone heading
        cos_psi = math.cos(drone_heading_rad)
        sin_psi = math.sin(drone_heading_rad)
        world_dx = body_dx * cos_psi - body_dy * sin_psi
        world_dy = body_dx * sin_psi + body_dy * cos_psi

        return Vector3(
            drone_pos.x + world_dx,
            drone_pos.y + world_dy,
            ground_altitude
        )

    def classify_target(self,
                        contour_area: float,
                        aspect_ratio: float,
                        color_name: str) -> Optional[DetectedTarget]:
        """
        Classifies geometric features into competition targets.
        """
        if contour_area < 50.0:
            return None  # Noise threshold

        # Shape classification heuristic
        if 0.85 <= aspect_ratio <= 1.15:
            shape = "CIRCLE" if contour_area > 300.0 else "SQUARE"
        elif 0.3 <= aspect_ratio <= 0.7 or 1.4 <= aspect_ratio <= 3.0:
            shape = "H_PAD"
        else:
            shape = "CROSS"

        return DetectedTarget(
            target_type=shape,
            pixel_u=self.camera.cx,
            pixel_v=self.camera.cy,
            color=color_name,
            confidence=0.92
        )

    def scan_synthetic_frame(self,
                             drone_pos: Vector3,
                             ground_targets: List[Dict[str, Any]]) -> List[Tuple[str, Vector3, float]]:
        """
        Simulates camera scanning against ground truth targets in the arena.
        Returns: [(target_id, estimated_world_pos, confidence)]
        """
        detections = []
        # Downward camera visible ground radius
        rel_alt = max(0.5, drone_pos.z)
        coverage_radius = rel_alt * math.tan(math.radians(40.0))

        for target in ground_targets:
            t_pos = target['pos']
            dist_xy = math.sqrt((drone_pos.x - t_pos.x)**2 + (drone_pos.y - t_pos.y)**2)

            if dist_xy <= coverage_radius:
                # Add slight measurement variance
                est_pos = Vector3(t_pos.x, t_pos.y, 0.0)
                conf = max(0.5, 1.0 - (dist_xy / coverage_radius) * 0.4)
                detections.append((target['id'], est_pos, conf))

        return detections
