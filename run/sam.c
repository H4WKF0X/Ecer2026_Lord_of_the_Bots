#include <stdio.h>
#include <stdlib.h>
#include <kipr/wombat.h>

#include "drive.h"
#include "config_parser.h"

/** 
 * This is the code running on the simple bot, that was pushing items off the black tape.
 * Refer to the lib folder for more information on functions
 */

// Manual robot configuration 
static RobotConfig robot_cfg = {
    .left_motor         = 2,
    .right_motor        = 0,

    .left_sensor_port   = 1,
    .right_sensor_port  = 0,

    .left_threshold     = 3602,
    .right_threshold    = 2010,

    .left_black_is_low  = 0,   // 0 = black is HIGH (val > threshold)
    .right_black_is_low = 0,
};

#define FAST_FWD        100
#define HARD_TURN        80
#define HARD_TURN_BACK   50

#define TARGET_INTERSECTIONS 2


int main(void) {
    // Initialize the drive library with our manual config
    drive_init(&robot_cfg);

    // Drive until black line, then white, then black again
    drive_until_black(80, 1);
    printf("I saw black\n");

    drive_until_white(80, 1);
    printf("I saw white\n");

    drive_until_black(80, 1);
    printf("I saw black\n");

    // Short forward burst
    drive_ramped(20, 20, 0);
    msleep(500);
    stop_driving(0);

    // Turn right ~180°
    turn_manual(80, -80, 1850, 1, 1);

    // Follow line until 2 intersections
    follow_line(FAST_FWD, HARD_TURN, HARD_TURN_BACK, TARGET_INTERSECTIONS);
    stop_driving(0);

    // Final left turn
    turn_manual(-80, 80, 1100, 1, 1);

    return 0;
}