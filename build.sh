#!/bin/bash
set -e

COMPILER=aarch64-linux-gnu-gcc
OUTPUT_DIR=/home/kipr/output
LIB_FLAGS="-lkipr -lm -lz -lpthread"
INCLUDES="-Ilib/include"

# Source files for your library
LIB_SRCS="lib/src/config_parser.c lib/src/drive.c lib/src/servo.c"

mkdir -p $OUTPUT_DIR

cd /home/kipr

echo "Building drive_test -> botball_user_program..."
$COMPILER -Wall $INCLUDES $LIB_SRCS run/frodo.c $LIB_FLAGS -o /home/kipr/output/botball_user_program

echo "✅ Done! Binaries in output/"