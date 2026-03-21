# ECER 2026 Robotics Codebase

This repository contains the C codebase for the ECER 2026 robotics competition, developed for the KIPR Wombat controller. The software architecture is designed with a strict focus on modularity, hardware abstraction, and dynamic on-device calibration.

## Project Structure

The codebase is separated into distinct functional directories to separate reusable library code from executable routines:

* `config/`: Contains the standalone calibration program used to set up the robot before a run.
* `data/`: The target directory for the generated hardware configuration files (e.g., `robot_config.txt`). This directory is typically git-ignored to prevent merge conflicts between different physical robots.
* `lib/`: The core reusable libraries.
    * `include/`: Header files defining the public APIs (`drive.h`, `servo.h`, `config_parser.h`).
    * `src/`: C implementations of the libraries.
* `run/`: Contains the executable main programs (the actual contest routines) that utilise the libraries.

## Video Reference

The specific programs and contest routines demonstrated in our technical video can be found in the `run/` directory. These files contain the high-level logic that utilizes our modular libraries to perform the pipe collection and dispensing tasks shown.

## Core Features and Modularity

The system avoids hardcoded hardware parameters in the main execution logic. Instead, it relies on a modular library system:

1.  **Config Parser:** Reads a configuration file at runtime to dynamically assign motor ports, sensor ports, hardware limits, and light thresholds.
2.  **Drive Library:** Handles all locomotion. Features include constant acceleration (ramping) to prevent wheel slip, modular sensor-based movement (e.g., driving until specific line detections), and state-machine-based rotation for precise line-hugging. Functions are decoupled from hardcoded stopping commands, allowing for seamless movement chaining.
3.  **Servo Library:** Provides clamped, safe movement ranges and smooth, incremental sweeping functions to prevent mechanical strain or abrupt jerking of the manipulator arms.

## On-Device Calibration

To account for changing ambient lighting conditions and potential hardware swaps during the competition, calibration is performed directly with information from the Wombat controller. 

Executing the `main_calibrate` program initiates an interactive setup routine on the device. The user is prompted to input current hardware ports, read live sensor values for black/white thresholds, and define the sensor offset geometry. This data is exported to `data/robot_config.txt`. 

When the main contest program is executed, it parses this text file via the `config_parser` library. This ensures that sensor degradation, port changes, or lighting variations can be resolved in seconds without requiring the code to be recompiled.

## Build and Deployment

Cross-compilation is set up using the `wombat-cross` Docker toolchain, allowing the entire codebase to be compiled on a standard PC and deployed directly to the Wombat controller over the network — no manual copy-paste into the KIPR IDE required.

### 1. Compile

Pull the cross-compilation image:
```bash
docker pull sillyfreak/wombat-cross
```

Then run the build from the repository root:
```bash
docker run --rm -v "${PWD}:/home/kipr" sillyfreak/wombat-cross bash /home/kipr/build.sh
```

This compiles the C code for the Wombat's ARM target and produces the output binary.

### 2. Deploy

The binary must meet two requirements to be recognized by the Wombat:
- **No file extension**
- **Named exactly** `botball_user_program`

Transfer it to the controller via SFTP into the project's `bin/` folder. Due to SFTP write permission restrictions on the Wombat, an SSH step is required beforehand to grant write access, and a second SSH step afterwards to mark the file as executable (the `-x` flag is not preserved by SFTP the first time):
```bash
# 1. Grant write permissions on the target directory
ssh root@<wombat-ip> "chmod 777 /path/to/project/bin"

# 2. Transfer the binary
sftp root@<wombat-ip>
> put botball_user_program /<User>/<your_project>/bin/botball_user_program

# 3. Make the binary executable
ssh root@<wombat-ip> "chmod +x /<User>/<your_project>/project/bin/botball_user_program"
```

> **Note:** Automation of this deploy process (wrapping the SSH/SFTP steps into a single script) is planned as a next step.

For reference on the cross-compilation environment, see:
[PRIArobotics/wombat-cross](https://github.com/PRIArobotics/wombat-cross)
