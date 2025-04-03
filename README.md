# Deep Coding Mode for Slack

Automatically updates your Slack status and enables Do Not Disturb when you're in the coding zone.

## Features
- Detects when you're coding in VSCode, RStudio, and other editors
- Automatically updates Slack status after a configurable time
- Enables Do Not Disturb to minimize distractions
- Works on macOS (Intel)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/deep-coding-mode.git
   cd deep-coding-mode
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the script once to generate the config file:
   ```bash
   python coding_monitor.py
   ```
7. Add your Slack token to the config file:
   ```bash
   nano ~/.coding_monitor.json
   ```

## Configuration 

Edit `~/.coding_monitor.json` to customize:
- Slack token
- Tracked coding applications
- Time thresholds
- Status message

## Usage

Run the script: 
```bash
python coding_monitor.py
```

## Running in the background:
To run the script in the background so it continues working even when you close your terminal:
```bash
nohup python coding_monitor.py &
```

## License
MIT License
