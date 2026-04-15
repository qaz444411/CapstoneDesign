import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

# ºñÁ¤Çü ÇèÁö ³» Çùµ¿ ¹°·ù¸¦ À§ÇÑ Physical AI ±â¹Ý ½Ç½Ã°£ »ç¶÷ ÃßÁ¾ Á¦¾î ½Ã½ºÅÛ
# ¶óÀÌ´Ù(LiDAR) ³ëÀÌÁî ¹× »ç°¢Áö´ë ÇÊÅÍ¸µ Launch ÆÄÀÏ

def generate_launch_description():
    config_dir = os.path.join(
        get_package_share_directory('my_lidar_pkg'),
        'config',
        'laser_filter_params.yaml'
    )

    return LaunchDescription([
        Node(
            package='laser_filters',
            executable='scan_to_scan_filter_chain',
            name='scan_filter_node',
            parameters=[config_dir],
            remappings=[
                ('scan', '/scan'),
                ('scan_filtered', '/scan_filtered')
            ],
            output='screen'
        )
    ])
