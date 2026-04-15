#include <memory>
#include <string>
#include <algorithm>
#include <fcntl.h> // ½Ã¸®¾ó Á¦¾î¿ë
#include <termios.h>
#include <unistd.h>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"

using std::placeholders::_1;

class PersonFollowerNode : public rclcpp::Node
{
public:
  PersonFollowerNode() : Node("person_follower_node")
  {
    // 1. ¶óÀÌ´Ù ÇÊÅÍ µ¥ÀÌÅÍ ±¸µ¶
    subscription_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
      "/scan_filtered", 10, std::bind(&PersonFollowerNode::scan_callback, this, _1));

    // 2. ¾ÆµÎÀÌ³ë¿Í ¿¬°áµÈ ½Ã¸®¾ó Æ÷Æ® ¿­±â
    // ÁÖÀÇ: º»ÀÎÀÇ ¾ÆµÎÀÌ³ë Æ÷Æ® ÀÌ¸§(ttyACM0 ¶Ç´Â ttyUSB0)À¸·Î º¯°æÇÏ¼¼¿ä.
    serial_fd_ = open("/dev/ttyACM0", O_RDWR | O_NOCTTY | O_NDELAY);
    
    if (serial_fd_ == -1) {
      RCLCPP_ERROR(this->get_logger(), "½Ã¸®¾ó Æ÷Æ®¸¦ ¿­ ¼ö ¾ø½À´Ï´Ù! Æ÷Æ® ÀÌ¸§ÀÌ³ª ±ÇÇÑÀ» È®ÀÎÇÏ¼¼¿ä.");
    } else {
      setup_serial(serial_fd_);
      RCLCPP_INFO(this->get_logger(), "¾ÆµÎÀÌ³ë ½Ã¸®¾ó ¿¬°á ¼º°ø!");
    }
  }

  ~PersonFollowerNode() {
    if (serial_fd_ != -1) close(serial_fd_);
  }

private:
  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr subscription_;
  int serial_fd_;

  // ½Ã¸®¾ó Åë½Å ¼¼ÆÃ (115200bps)
  void setup_serial(int fd) {
    struct termios options;
    tcgetattr(fd, &options);
    cfsetispeed(&options, B115200);
    cfsetospeed(&options, B115200);
    options.c_cflag |= (CLOCAL | CREAD);
    tcsetattr(fd, TCSANOW, &options);
  }

  void scan_callback(const sensor_msgs::msg::LaserScan::SharedPtr msg)
  {
    // 3. °¡Àå °¡±î¿î ¹°Ã¼(Å¸°Ù) Ã£±â
    float min_distance = msg->range_max;
    int target_index = -1;

    for (size_t i = 0; i < msg->ranges.size(); ++i) {
      float r = msg->ranges[i];
      if (r > msg->range_min && r < msg->range_max) {
        if (r < min_distance) {
          min_distance = r;
          target_index = i;
        }
      }
    }

    // Å¸°ÙÀ» Ã£Áö ¸øÇß°Å³ª 3m ¹Û¿¡ ÀÖÀ¸¸é Á¤Áö ¸í·É
    if (target_index == -1 || min_distance > 3.0) { 
      send_command(90, 90); // Á¶Çâ Áß¸³(90), ¼Óµµ Á¤Áö(90)
      return;
    }

    // 4. Á¦¾î°ª °è»ê
    float target_angle_rad = msg->angle_min + target_index * msg->angle_increment;
    float target_angle_deg = target_angle_rad * 180.0 / M_PI;

    // Á¶Çâ°ª °è»ê: Áß¾Ó(90)À» ±âÁØÀ¸·Î ¿ÀÂ÷¸¸Å­ ²ªÀ½
    // ¾ÆµÎÀÌ³ë Á¦¾î ¹üÀ§: 45(¿ì) ~ 90(Áß) ~ 140(ÁÂ)
    int steer_cmd = 90 + static_cast<int>(target_angle_deg * 0.5); 
    steer_cmd = std::max(45, std::min(140, steer_cmd)); 

    // ÁÖÇà ¼Óµµ °è»ê: ¸ñÇ¥ À¯Áö °Å¸® 1.0m
    int throttle_cmd = 90;
    if (min_distance > 1.2) {
      // °Å¸®°¡ 1.2m ÀÌ»ó ¸Ö¾îÁö¸é ÀüÁø (96ºÎÅÍ ½ÃÀÛ)
      throttle_cmd = 96 + static_cast<int>((min_distance - 1.0) * 10);
      throttle_cmd = std::min(throttle_cmd, 120); // ÃÖ´ë ¼Óµµ Á¦ÇÑ
    } else if (min_distance < 0.8) {
      // °Å¸®°¡ 0.8m ÀÌ³»·Î ³Ê¹« °¡±î¿öÁö¸é Á¤Áö
      throttle_cmd = 90; 
    }

    // 5. ¾ÆµÎÀÌ³ë·Î ÃÖÁ¾ Á¦¾î ¸í·É Àü¼Û
    send_command(steer_cmd, throttle_cmd);
  }

  void send_command(int steer, int throttle) {
    if (serial_fd_ != -1) {
      // "120,105\n" Æ÷¸ËÀ¸·Î ¹®ÀÚ¿­ º¯È¯ ÈÄ Àü¼Û
      std::string cmd = std::to_string(steer) + "," + std::to_string(throttle) + "\n";
      write(serial_fd_, cmd.c_str(), cmd.length());
      
      // ÅÍ¹Ì³Î¿¡¼­ ½Ç½Ã°£ °ª È®ÀÎ¿ë (·Î±×°¡ ³Ê¹« ±æ¾îÁö¸é ÁÖ¼® Ã³¸® °¡´É)
      RCLCPP_INFO(this->get_logger(), "Àü¼ÛµÈ ¸í·É -> Á¶Çâ: %d, ¼Óµµ: %d", steer, throttle);
    }
  }
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<PersonFollowerNode>());
  rclcpp::shutdown();
  return 0;
}