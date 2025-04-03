# Deep Coding Mode for Slack

Automatically updates your Slack status and enables Do Not Disturb when you're in the coding zone.

## Features
- Detects when you're coding in VSCode, RStudio, and other editors
- Automatically updates Slack status after a configurable time
- Enables Do Not Disturb to minimize distractions
- Works on macOS (Intel)

## Installation

1. Clone this repository: git clone https://github.com/sw-ds-proj/deep-coding-mode.git
cd deep-coding-mode
2. Install dependencies: pip install -r requirements.txt
3. Run the script once to generate the config file: python coding_monitor.py
4. Add your Slack token to the config file: nano ~/.coding_monitor.json

## Configuration 

Edit `~/.coding_monitor.json` to customize:
- Slack token
- Tracked coding applications
- Time thresholds
- Status message

## Usage

Run the script: python coding_monitor.py
To run in the background: nohup python coding_monitor.py &

## License
MIT License
