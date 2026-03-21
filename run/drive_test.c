#include <stdio.h>
#include <kipr/wombat.h>
#include "drive.h"

static RobotConfig robot_cfg = {
    .left_motor         = 2,
    .right_motor        = 0,
    .left_sensor_port   = 1,
    .right_sensor_port  = 0,
    .left_threshold     = 3440,
    .right_threshold    = 1835,
    .left_black_is_low  = 0,
    .right_black_is_low = 0,
};

int main(void) {
    drive_init(&robot_cfg);

    printf("Driving forward for 5 seconds...\n");
    drive(80, 80);
    msleep(5000);

    printf("Stopping.\n");
    stop_driving(0);

    return 0;
}
