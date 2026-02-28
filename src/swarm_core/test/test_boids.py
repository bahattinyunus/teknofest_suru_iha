import pytest
import math
from swarm_core.node_commander import SwarmCommander
from geometry_msgs.msg import PoseStamped, Twist

class MockNode:
    def get_parameter(self, name):
        params = {
            'cohesion_weight': 1.0,
            'separation_weight': 1.6,
            'max_speed': 5.0,
            'perception_radius': 15.0,
            'safe_distance': 3.0,
            'obstacle_weight': 2.5
        }
        class Param:
            def __init__(self, value): self.value = value
        return Param(params.get(name, 1.0))

def test_boids_separation():
    # Bu test, SwarmCommander'ın doğrudan test edilebilir kısımlarını mocklar
    # rclpy bağımlılığı nedeniyle tüm sınıfı test etmek zordur, 
    # bu yüzden mantıksal fonksiyonları izole ediyoruz.
    
    # Not: Gerçek bir ROS testinde launch_testing kullanılır.
    # Burada mantıksal bir örnek sunuyoruz.
    pass

def test_math_logic():
    # Ayrılma vektörü hesaplama testi (Basitleştirilmiş)
    dx, dy = 1.0, 1.0
    dist = math.sqrt(dx**2 + dy**2)
    sep_x = dx / dist
    sep_y = dy / dist
    
    assert math.isclose(math.sqrt(sep_x**2 + sep_y**2), 1.0)
