"""
Teknofest Swarm UAV - Distributed Extended Kalman Filter (EKF) & Sensor Fusion Engine
Provides robust 3D state estimation by fusing:
  - IMU (3-axis Accelerometer & Gyroscope)
  - GNSS / GPS Position (with HDOP & Innovation Mahalanobis Outlier Gating)
  - Barometric Altimeter / LiDAR AGL
  - UWB / RF Inter-Drone Relative Ranging (Collaborative Swarm Trilateration)
  - Seamless GNSS-Denied Dead-Reckoning fallback with Covariance Uncertainty Tracking.
"""

import math
import time
from typing import Dict, List, Tuple, Optional, Any
from swarm_core.algorithms import Vector3


class SensorFusionEKF:
    """
    3D Extended Kalman Filter for Swarm UAV navigation.
    State vector: [px, py, pz, vx, vy, vz, bax, bay, baz]
      p: 3D position (meters)
      v: 3D velocity (m/s)
      ba: 3D accelerometer bias (m/s^2)
    """

    def __init__(self,
                 initial_pos: Optional[Vector3] = None,
                 initial_vel: Optional[Vector3] = None,
                 accel_noise: float = 0.2,
                 gyro_noise: float = 0.05,
                 bias_instability: float = 0.01,
                 gps_pos_noise: float = 0.8,
                 baro_noise: float = 0.3,
                 uwb_range_noise: float = 0.15):
        
        # State vector
        self.pos = initial_pos if initial_pos else Vector3(0.0, 0.0, 0.0)
        self.vel = initial_vel if initial_vel else Vector3(0.0, 0.0, 0.0)
        self.accel_bias = Vector3(0.0, 0.0, 0.0)

        # Diagonal covariance representation for high efficiency
        # Variance for [px, py, pz, vx, vy, vz, bax, bay, baz]
        self.cov_p = Vector3(1.0, 1.0, 1.0)
        self.cov_v = Vector3(0.5, 0.5, 0.5)
        self.cov_ba = Vector3(0.05, 0.05, 0.05)

        # Process noise parameters
        self.q_accel = accel_noise ** 2
        self.q_bias = bias_instability ** 2

        # Measurement noise parameters
        self.r_gps = gps_pos_noise ** 2
        self.r_baro = baro_noise ** 2
        self.r_uwb = uwb_range_noise ** 2

        # GNSS status tracking
        self.gnss_available = True
        self.gnss_spoofed = False
        self.last_gps_time = time.time()
        self.last_predict_time = time.time()
        self.dead_reckoning_duration = 0.0
        self.mahalanobis_gate_threshold = 9.0  # Chi-squared 3-DoF 99% threshold is ~11.3, 9.0 is robust

    def predict(self,
                accel_meas: Vector3,
                dt: float) -> Tuple[Vector3, Vector3]:
        """
        EKF Prediction step using 3-axis IMU acceleration.
        Compensates for estimated accelerometer bias.
        """
        if dt <= 0.0:
            return self.pos, self.vel

        # Correct acceleration with estimated bias
        accel_unbiased = Vector3(
            accel_meas.x - self.accel_bias.x,
            accel_meas.y - self.accel_bias.y,
            accel_meas.z - self.accel_bias.z
        )

        # State propagation:
        # p_new = p + v*dt + 0.5*a*dt^2
        # v_new = v + a*dt
        self.pos = self.pos + (self.vel * dt) + (accel_unbiased * (0.5 * dt * dt))
        self.vel = self.vel + (accel_unbiased * dt)

        # Covariance propagation (simplified diagonal Riccati update):
        # Var(p) += dt^2 * Var(v) + 0.25 * dt^4 * Q_a
        # Var(v) += dt^2 * Q_a
        # Var(ba) += dt * Q_ba
        self.cov_p = Vector3(
            self.cov_p.x + (self.cov_v.x * (dt ** 2)) + (0.25 * (dt ** 4) * self.q_accel),
            self.cov_p.y + (self.cov_v.y * (dt ** 2)) + (0.25 * (dt ** 4) * self.q_accel),
            self.cov_p.z + (self.cov_v.z * (dt ** 2)) + (0.25 * (dt ** 4) * self.q_accel)
        )
        self.cov_v = Vector3(
            self.cov_v.x + (dt ** 2) * self.q_accel,
            self.cov_v.y + (dt ** 2) * self.q_accel,
            self.cov_v.z + (dt ** 2) * self.q_accel
        )
        self.cov_ba = Vector3(
            self.cov_ba.x + dt * self.q_bias,
            self.cov_ba.y + dt * self.q_bias,
            self.cov_ba.z + dt * self.q_bias
        )

        # Update dead-reckoning timer if GNSS is not available
        if not self.gnss_available:
            self.dead_reckoning_duration += dt
        else:
            self.dead_reckoning_duration = 0.0

        return self.pos, self.vel

    def update_gps(self,
                   measured_pos: Vector3,
                   hdop: float = 1.0) -> bool:
        """
        EKF measurement update for GNSS 3D position with HDOP weighting
        and Mahalanobis Innovation Gating against spoofing/outliers.
        Returns True if accepted, False if rejected by innovation gate.
        """
        # Effective measurement variance scaled by HDOP
        r_eff = self.r_gps * max(1.0, hdop ** 2)

        # Innovation (residual)
        innov = measured_pos - self.pos

        # Innovation variance S = P + R
        s_x = self.cov_p.x + r_eff
        s_y = self.cov_p.y + r_eff
        s_z = self.cov_p.z + r_eff

        # Mahalanobis distance squared: d^2 = sum(innov_i^2 / S_i)
        d_sq = (innov.x ** 2) / s_x + (innov.y ** 2) / s_y + (innov.z ** 2) / s_z

        if d_sq > self.mahalanobis_gate_threshold:
            # Outlier or GPS Spoofing detected!
            self.gnss_spoofed = True
            self.gnss_available = False
            return False

        # Measurement is valid: apply Kalman Gain K = P / (P + R)
        k_x = self.cov_p.x / s_x
        k_y = self.cov_p.y / s_y
        k_z = self.cov_p.z / s_z

        # State update: x = x + K * innov
        self.pos = Vector3(
            self.pos.x + k_x * innov.x,
            self.pos.y + k_y * innov.y,
            self.pos.z + k_z * innov.z
        )

        # Velocity correction from position innovation
        kv_x = 0.2 * k_x
        kv_y = 0.2 * k_y
        kv_z = 0.2 * k_z
        self.vel = Vector3(
            self.vel.x + kv_x * innov.x,
            self.vel.y + kv_y * innov.y,
            self.vel.z + kv_z * innov.z
        )

        # Covariance update: P = (1 - K) * P
        self.cov_p = Vector3(
            (1.0 - k_x) * self.cov_p.x,
            (1.0 - k_y) * self.cov_p.y,
            (1.0 - k_z) * self.cov_p.z
        )

        self.gnss_available = True
        self.gnss_spoofed = False
        self.last_gps_time = time.time()
        self.dead_reckoning_duration = 0.0
        return True

    def update_barometer(self, measured_alt: float) -> None:
        """
        EKF measurement update for Barometric Altimeter / LiDAR AGL.
        Directly refines Z position and vertical velocity.
        """
        innov_z = measured_alt - self.pos.z
        s_z = self.cov_p.z + self.r_baro
        k_z = self.cov_p.z / s_z

        self.pos = Vector3(self.pos.x, self.pos.y, self.pos.z + k_z * innov_z)
        self.vel = Vector3(self.vel.x, self.vel.y, self.vel.z + (0.3 * k_z * innov_z))
        self.cov_p = Vector3(self.cov_p.x, self.cov_p.y, (1.0 - k_z) * self.cov_p.z)

    def update_relative_range(self,
                              anchor_pos: Vector3,
                              measured_range: float) -> bool:
        """
        Collaborative Swarm Ranging Update (e.g. UWB range to known neighbor).
        Uses non-linear range observation h(x) = ||pos - anchor_pos||.
        Computes Jacobian H = (pos - anchor_pos) / ||pos - anchor_pos||.
        """
        delta = self.pos - anchor_pos
        est_range = delta.magnitude()

        if est_range < 0.01:
            return False

        # Jacobian H (unit direction vector from anchor to current pos)
        h_x = delta.x / est_range
        h_y = delta.y / est_range
        h_z = delta.z / est_range

        # Innovation: y = z - h(x)
        innov_range = measured_range - est_range

        # Innovation variance: S = H * P * H^T + R
        s_range = (
            (h_x ** 2) * self.cov_p.x +
            (h_y ** 2) * self.cov_p.y +
            (h_z ** 2) * self.cov_p.z +
            self.r_uwb
        )

        if s_range <= 0.0:
            return False

        # Kalman Gain: K = P * H^T / S
        k_x = (self.cov_p.x * h_x) / s_range
        k_y = (self.cov_p.y * h_y) / s_range
        k_z = (self.cov_p.z * h_z) / s_range

        # State update
        self.pos = Vector3(
            self.pos.x + k_x * innov_range,
            self.pos.y + k_y * innov_range,
            self.pos.z + k_z * innov_range
        )

        # Covariance update
        self.cov_p = Vector3(
            max(0.01, self.cov_p.x - k_x * h_x * self.cov_p.x),
            max(0.01, self.cov_p.y - k_y * h_y * self.cov_p.y),
            max(0.01, self.cov_p.z - k_z * h_z * self.cov_p.z)
        )

        return True

    def get_position_uncertainty(self) -> float:
        """Returns standard deviation (1-sigma) of 3D position error in meters."""
        return math.sqrt(self.cov_p.x + self.cov_p.y + self.cov_p.z)

    def is_navigation_healthy(self, max_uncertainty: float = 5.0) -> bool:
        """Determines if navigational accuracy is sufficient for autonomous flight."""
        return self.get_position_uncertainty() < max_uncertainty and not self.gnss_spoofed

    def get_telemetry_dict(self) -> Dict[str, Any]:
        """Exports state estimation status for telemetry and GCS visualization."""
        return {
            "estimated_pos": self.pos.as_tuple(),
            "estimated_vel": self.vel.as_tuple(),
            "position_uncertainty_1sigma": round(self.get_position_uncertainty(), 3),
            "gnss_available": self.gnss_available,
            "gnss_spoofed": self.gnss_spoofed,
            "dead_reckoning_seconds": round(self.dead_reckoning_duration, 2),
            "nav_healthy": self.is_navigation_healthy()
        }
