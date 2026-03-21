#include <stdio.h>
#include <stdlib.h>
#include <kipr/wombat.h>

#include "drive.h"
#include "servo.h"
#include "config_parser.h"

/** 
 * This is the code running on the sero bot in the mechanical video, 
 * that was collecting pipes from the dispenser.
 * Refer to the lib folder for more information on functions
 */


// Manual robot configuration
static RobotConfig robot_cfg = {
    .left_motor         = 0,
    .right_motor        = 2,
    .aux_motor          = 3,

    .left_sensor_port   = 0,
    .right_sensor_port  = 1,

    .left_threshold     = 3608,
    .right_threshold    = 3800,

    .left_black_is_low  = 0,
    .right_black_is_low = 0,

    .sensor_offset      = -1,

    .arm_servo_port     = 3,
    .arm_servo_min      = 104,
    .arm_servo_max      = 1830,
};

// Arm helpers 
// arm_up/down wrap servo calls so main() stays readable

static void arm_up() {
    servo_set(robot_cfg.arm_servo_port, robot_cfg.arm_servo_max,
              robot_cfg.arm_servo_min, robot_cfg.arm_servo_max);
}

static void arm_down() {
    servo_move_smooth(robot_cfg.arm_servo_port, robot_cfg.arm_servo_min,
                      15, robot_cfg.arm_servo_min, robot_cfg.arm_servo_max);
}

static void arm_mid() {
    servo_move_smooth(robot_cfg.arm_servo_port, 1000,
                      15, robot_cfg.arm_servo_min, robot_cfg.arm_servo_max);
}

int main(void) {
    drive_init(&robot_cfg);
    servo_enable_all();

    // Start position: arm fully up
    arm_up();

    // Drive to line sequence
    drive_until_black(80, 1);
    printf("I saw black\n");
    drive_until_white(80, 1);
    printf("I saw white\n");
    drive_until_black(80, 1);
    printf("I saw black\n");

    // Short forward nudge to position under dispenser
    drive_ramped(20, 20, 0);
    msleep(1610);
    stop_driving(0);

    // Lower arm to collect pipe, then release servos
    arm_down();
    msleep(1000);
    servo_disable_all();
    ao();

    // Wait for dispenser cycle
    msleep(35000);

    // Aux motor pulses (dispenser mechanism)
    for (int i = 0; i < 3; i++) {
        motor(robot_cfg.aux_motor, 50);
        msleep(500);
        ao();
        msleep(250);
    }
    msleep(7000);
    motor(robot_cfg.aux_motor, 50);
    msleep(500);
    ao();

    // Raise arm to mid position to grip collected pipe
    servo_enable_all();
    arm_mid();
    msleep(1000);
    servo_disable_all();

    // Reverse back to drop-off
    msleep(850);
    drive_until_black(-80, 0);
    drive_until_white(-80, 0);
    msleep(1200);
    stop_driving(0);
    ao();

    // Final aux motor push
    motor(robot_cfg.aux_motor, 50);
    msleep(5950);
    ao();

    // Return arm to top for next run
    servo_enable_all();
    arm_up();

    return 0;
}