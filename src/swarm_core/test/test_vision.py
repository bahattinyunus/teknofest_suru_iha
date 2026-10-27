import pytest
import math
from swarm_core.algorithms import Vector3
from swarm_core.vision_pipeline import SwarmVisionEngine, CameraIntrinsics


def test_camera_intrinsics():
    cam = CameraIntrinsics(image_width=640, image_height=480, fov_deg=80.0)
    assert cam.width == 640
    assert cam.height == 480
    assert cam.cx == 320.0
    assert cam.cy == 240.0
    assert cam.fx > 0.0


def test_pixel_to_world_nadir():
    engine = SwarmVisionEngine()
    drone_pos = Vector3(10.0, 20.0, 10.0)

    # Pixel at center (cx, cy) should project exactly beneath drone (10, 20, 0)
    world_pos = engine.pixel_to_world(
        pixel_u=engine.camera.cx,
        pixel_v=engine.camera.cy,
        drone_pos=drone_pos,
        drone_heading_rad=0.0,
        ground_altitude=0.0
    )

    assert math.isclose(world_pos.x, 10.0, abs_tol=1e-4)
    assert math.isclose(world_pos.y, 20.0, abs_tol=1e-4)
    assert math.isclose(world_pos.z, 0.0, abs_tol=1e-4)


def test_target_classification():
    engine = SwarmVisionEngine()

    # Square / Circle aspect ratio
    target = engine.classify_target(contour_area=400.0, aspect_ratio=1.0, color_name="RED")
    assert target is not None
    assert target.target_type in ["CIRCLE", "SQUARE"]
    assert target.color == "RED"

    # Too small / noise
    noise = engine.classify_target(contour_area=20.0, aspect_ratio=1.0, color_name="BLUE")
    assert noise is None


def test_synthetic_frame_scan():
    engine = SwarmVisionEngine()
    drone_pos = Vector3(0.0, 0.0, 10.0)

    ground_targets = [
        {'id': 'TARGET_CLOSE', 'pos': Vector3(2.0, 2.0, 0.0)},
        {'id': 'TARGET_FAR', 'pos': Vector3(100.0, 100.0, 0.0)}
    ]

    detections = engine.scan_synthetic_frame(drone_pos, ground_targets)
    assert len(detections) == 1
    assert detections[0][0] == 'TARGET_CLOSE'
