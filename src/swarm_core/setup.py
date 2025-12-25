from setuptools import setup
import os
from glob import glob

package_name = 'swarm_core'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Bahattin Yunus Çetin',
    maintainer_email='bahattinyunus@example.com',
    description='Sürünün beyni: Dağıtık mantık ve kontrol düğümleri.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'commander = swarm_core.node_commander:main',
        ],
    },
)
