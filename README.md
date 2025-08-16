# Raspberry Pi 5 Home CCTV Monitoring Project

## Features
- Real-time face recognition
- Motion detection
- Event logging (images when motion/unknown face detected)
- Email notifications (for motion/unknown face)
- Pan-Tilt camera tracking (servo motor control)
- UPS HAT integration for power backup and battery monitoring

## Hardware Required
- Raspberry Pi 5
- UPS HAT (e.g., Geekworm UPS Plus, PiJuice)
- 18650 Li-ion battery (per HAT specs)
- Pan-Tilt servo kit (2x SG90 servos)
- Servo control wires (GPIO17 - pan, GPIO18 - tilt)
- Camera (Pi Camera v3 or USB webcam)
- MicroSD card (32GB+)
- Power supply (5V/3A USB-C)
- Jumper wires

## Wiring
- Mount UPS HAT on Pi GPIO header, connect battery and power adapter to HAT.
- Connect servos:
    - Pan servo signal → GPIO17
    - Tilt servo signal → GPIO18
    - Servo power/ground → Pi 5V/GND or external supply
- Connect camera to Pi camera port or USB.

## Setup
1. Clone this repo to your Pi.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   sudo apt-get install libopenblas-dev liblapack-dev
   ```
3. Add images of known people to `known_faces/` (filenames = names).
4. Edit email settings in `face_recognition_cctv.py`.
5. Run main script:
   ```bash
   python3 face_recognition_cctv.py
   ```
6. Optionally, run UPS monitor:
   ```bash
   python3 ups_monitor.py
   ```

## How UPS HAT Works
- Power adapter connects to HAT (not Pi directly).
- Pi powered through HAT.
- On power loss, HAT automatically switches to battery to keep Pi running.

## Schematic & Block Diagram
(Include images here once added to repo)

## Notes
- For best servo performance, use external 5V supply for servos if possible.
- For other UPS HATs, update I2C address/registers as per datasheet.
