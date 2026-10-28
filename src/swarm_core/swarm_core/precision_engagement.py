#!/usr/bin/env python3
"""
Teknofest Precision Target Engagement & Payload Drop Controller.
Implements autonomous multi-stage visual servoing, vertical descent,
target engagement / QR payload release, and formation rejoining.
"""

from typing import Tuple, Optional
from swarm_core.algorithms import Vector3


class PrecisionEngagementController:
    """
    Finite State Machine for target interception and precision payload drop.
    States:
      IDLE -> CRUISE_APPROACH -> VISUAL_ALIGN -> CONTROLLED_DESCENT -> ENGAGE -> CLIMB_REJOIN -> COMPLETED
    """
    STATES = ['IDLE', 'CRUISE_APPROACH', 'VISUAL_ALIGN', 'CONTROLLED_DESCENT', 'ENGAGE', 'CLIMB_REJOIN', 'COMPLETED']

    def __init__(self,
                 cruise_alt: float = 10.0,
                 drop_alt: float = 2.0,
                 approach_speed: float = 4.0,
                 descent_speed: float = 1.0,
                 alignment_tolerance: float = 0.5):
        self.cruise_alt = cruise_alt
        self.drop_alt = drop_alt
        self.approach_speed = approach_speed
        self.descent_speed = descent_speed
        self.alignment_tolerance = alignment_tolerance

        self.current_state = 'IDLE'
        self.target_pos: Optional[Vector3] = None
        self.engage_start_time = 0.0
        self.engage_dwell_sec = 1.5
        self.payload_released = False

    def assign_target(self, target_pos: Vector3):
        self.target_pos = target_pos
        self.current_state = 'CRUISE_APPROACH'
        self.payload_released = False

    def update(self, current_pos: Vector3, timestamp: float) -> Tuple[Vector3, str, bool]:
        """
        Calculates command velocity for current stage.
        Returns: (cmd_vel: Vector3, state_name: str, is_completed: bool)
        """
        if self.current_state == 'IDLE' or self.target_pos is None:
            return Vector3(0.0, 0.0, 0.0), 'IDLE', False

        cmd_vel = Vector3(0.0, 0.0, 0.0)
        is_completed = False

        # Horizontal error
        dx = self.target_pos.x - current_pos.x
        dy = self.target_pos.y - current_pos.y
        dist_xy = (dx**2 + dy**2)**0.5

        # 1. State Transitions
        if self.current_state == 'CRUISE_APPROACH':
            if dist_xy <= self.alignment_tolerance:
                self.current_state = 'CONTROLLED_DESCENT'
            elif dist_xy <= self.alignment_tolerance * 2.0:
                self.current_state = 'VISUAL_ALIGN'

        if self.current_state == 'VISUAL_ALIGN':
            if dist_xy <= self.alignment_tolerance:
                self.current_state = 'CONTROLLED_DESCENT'

        if self.current_state == 'CONTROLLED_DESCENT':
            if current_pos.z <= self.drop_alt + 0.15:
                self.current_state = 'ENGAGE'
                self.engage_start_time = timestamp

        if self.current_state == 'ENGAGE':
            if (timestamp - self.engage_start_time) >= self.engage_dwell_sec:
                self.payload_released = True
                self.current_state = 'CLIMB_REJOIN'

        if self.current_state == 'CLIMB_REJOIN':
            if current_pos.z >= self.cruise_alt - 0.2:
                self.current_state = 'COMPLETED'

        # 2. Velocity Command Generation
        if self.current_state == 'CRUISE_APPROACH':
            scale = min(self.approach_speed, dist_xy * 0.8)
            cmd_vel.x = (dx / dist_xy) * scale if dist_xy > 0.01 else 0.0
            cmd_vel.y = (dy / dist_xy) * scale if dist_xy > 0.01 else 0.0
            alt_err = self.cruise_alt - current_pos.z
            cmd_vel.z = max(-1.0, min(1.0, alt_err * 0.5))

        elif self.current_state == 'VISUAL_ALIGN':
            cmd_vel.x = dx * 0.5
            cmd_vel.y = dy * 0.5
            alt_err = self.cruise_alt - current_pos.z
            cmd_vel.z = max(-0.5, min(0.5, alt_err * 0.5))

        elif self.current_state == 'CONTROLLED_DESCENT':
            cmd_vel.x = dx * 0.4
            cmd_vel.y = dy * 0.4
            cmd_vel.z = -self.descent_speed

        elif self.current_state == 'ENGAGE':
            cmd_vel.x = dx * 0.3
            cmd_vel.y = dy * 0.3
            cmd_vel.z = (self.drop_alt - current_pos.z) * 0.4

        elif self.current_state == 'CLIMB_REJOIN':
            cmd_vel.z = self.descent_speed * 1.2

        elif self.current_state == 'COMPLETED':
            is_completed = True
            cmd_vel = Vector3(0.0, 0.0, 0.0)

        return cmd_vel, self.current_state, is_completed
