#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Intel Mac (x86_64) Coding Time Monitor
Monitors time spent in coding applications and manages Slack status
"""

import time
import subprocess
import logging
import os
import json
# Add this at the top of your script
try:
    import requests
except ImportError:
    import subprocess
    import sys
    print("Installing missing 'requests' module...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("coding_monitor.log"), logging.StreamHandler()]
)
logger = logging.getLogger("CodingMonitor")

# Configuration file path
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".coding_monitor.json")

class CodingTimeMonitor:
    def __init__(self):
        # Initialize state variables
        self.current_app = ""
        self.app_start_time = None
        self.continuous_coding_time = 0
        self.total_coding_time = 0
        self.deep_mode_active = False
        self.last_status_update = 0
        
        # Load configuration
        self.config = self.load_config()
        
        # Print startup information
        logger.info("Starting Coding Time Monitor for Intel Mac (x86_64)")
        logger.info(f"Monitoring for apps: {', '.join(self.config['coding_apps'])}")
        logger.info(f"Deep mode threshold: {self.config['deep_mode_threshold_seconds']} seconds")
        
    def load_config(self):
        """Load configuration from file or create default"""
        default_config = {
            "slack_token": "",
            "coding_apps": [
                "Code", "Visual Studio Code", "VSCode", "Electron",  # VS Code
                "RStudio", "R Console", "R Graphics",    # R
                "PyCharm", "IntelliJ", "Eclipse",        # JetBrains and others
                "Sublime Text", "Atom", "Vim", "Emacs"   # Text editors
            ],
            "deep_mode_threshold_seconds": 120,  # 20 minutes
            "check_interval_seconds": 1,
            "dnd_duration_minutes": 60,
            "status_update_interval_seconds": 1800  # 30 minutes
        }
        
        # Create default config if file doesn't exist
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default configuration at {CONFIG_FILE}")
            return default_config
        
        # Load existing config
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {CONFIG_FILE}")
            return config
        except Exception as e:
            logger.error(f"Error loading config: {e}, using defaults")
            return default_config
    
    def get_active_app(self):
        """Get the currently active application using AppleScript"""
        try:
            # Get application name (more reliable than window title)
            cmd = "osascript -e 'tell application \"System Events\" to get name of first application process whose frontmost is true'"
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            app_name, error = process.communicate()
            
            if error:
                logger.warning(f"Error getting app name: {error.decode('utf-8').strip()}")
                return "Unknown"
            
            return app_name.decode('utf-8').strip()
        except Exception as e:
            logger.error(f"Exception getting active app: {e}")
            return "Unknown"
    
    def is_coding_app(self, app_name):
        """Check if the application is a coding app"""
        return any(app.lower() in app_name.lower() for app in self.config['coding_apps'])
    
    def format_time(self, seconds):
        """Format seconds into HH:MM:SS"""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    
    def set_slack_dnd(self):
        """Set Slack Do Not Disturb mode"""
        if not self.config['slack_token']:
            logger.warning("Slack token not configured. Skipping DND update.")
            return False
        
        try:
            url = "https://slack.com/api/dnd.setSnooze"
            headers = {
                "Authorization": f"Bearer {self.config['slack_token']}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {
                "num_minutes": self.config['dnd_duration_minutes']
            }
            
            response = requests.post(url, headers=headers, data=data)
            result = response.json()
            
            if result.get("ok"):
                logger.info(f"Set Slack DND mode for {self.config['dnd_duration_minutes']} minutes")
                return True
            else:
                logger.error(f"Failed to set Slack DND: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting Slack DND: {e}")
            return False
    
    def set_slack_status(self):
        """Set Slack status to Deep Coding Mode"""
        if not self.config['slack_token']:
            logger.warning("Slack token not configured. Skipping status update.")
            return False
        
        try:
            url = "https://slack.com/api/users.profile.set"
            headers = {
                "Authorization": f"Bearer {self.config['slack_token']}",
                "Content-Type": "application/json; charset=utf-8"
            }
            
            # Status with expiration
            data = {
                "profile": {
                    "status_text": "Deep Coding Mode",
                    "status_emoji": ":computer:",
                    "status_expiration": int(time.time()) + (self.config['dnd_duration_minutes'] * 60)
                }
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(data))
            result = response.json()
            
            if result.get("ok"):
                logger.info("Set Slack status to 'Deep Coding Mode'")
                return True
            else:
                logger.error(f"Failed to set Slack status: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting Slack status: {e}")
            return False
    
    def enable_deep_mode(self):
        """Enable Deep Coding Mode (DND + Status)"""
        current_time = time.time()
        
        # Only update if not already in deep mode or past update interval
        if not self.deep_mode_active or (current_time - self.last_status_update > self.config['status_update_interval_seconds']):
            logger.info("Enabling deep coding mode...")
            
            # Set DND mode
            dnd_success = self.set_slack_dnd()
            
            # Set status
            status_success = self.set_slack_status()
            
            if dnd_success or status_success:
                self.deep_mode_active = True
                self.last_status_update = current_time
                logger.info(f"Deep coding mode active for {self.config['dnd_duration_minutes']} minutes")
                return True
            else:
                logger.warning("Failed to enable deep coding mode")
                return False
        
        return True  # Already in deep mode
    
    def start_monitoring(self):
        """Main monitoring loop"""
        logger.info("Starting monitoring. Press Ctrl+C to exit.")
        last_app_check = time.time()
        last_status_print = time.time()
        
        try:
            while True:
                current_time = time.time()
                
                # Check active app (at configured interval)
                if current_time - last_app_check >= self.config['check_interval_seconds']:
                    app_name = self.get_active_app()
                    is_coding = self.is_coding_app(app_name)
                    last_app_check = current_time
                    
                    # Update times
                    if is_coding:
                        # If app changed but still coding
                        if self.current_app != app_name:
                            # Add time from previous coding app
                            if self.app_start_time is not None and self.is_coding_app(self.current_app):
                                session_time = current_time - self.app_start_time
                                self.total_coding_time += session_time
                                logger.debug(f"App change: {self.current_app} → {app_name}")
                            
                            # Reset session with new app
                            self.current_app = app_name
                            self.app_start_time = current_time
                            
                            # Log if starting new coding session
                            if self.continuous_coding_time == 0:
                                logger.info(f"Started coding session in {app_name}")
                        
                        # Increment continuous coding time
                        self.continuous_coding_time += self.config['check_interval_seconds']
                        
                        # Check if we should enable deep mode
                        if self.continuous_coding_time >= self.config['deep_mode_threshold_seconds'] and not self.deep_mode_active:
                            logger.info(f"Reached deep mode threshold: {self.format_time(self.continuous_coding_time)}")
                            self.enable_deep_mode()
                    else:
                        # No longer coding
                        if self.continuous_coding_time > 0:
                            # End of coding session
                            logger.info(f"Coding session ended. Duration: {self.format_time(self.continuous_coding_time)}")
                            
                            # Add to total time
                            if self.app_start_time is not None:
                                session_time = current_time - self.app_start_time
                                self.total_coding_time += session_time
                                self.app_start_time = None
                            
                            self.continuous_coding_time = 0
                        
                        self.current_app = app_name
                
                # Print status (once per second)
                if current_time - last_status_print >= 1:
                    status_line = f"\rApp: {self.current_app[:25]:<25} | "
                    status_line += f"Coding: {'Yes' if (self.continuous_coding_time > 0) else 'No'} | "
                    status_line += f"Session: {self.format_time(self.continuous_coding_time)} | "
                    status_line += f"Total: {self.format_time(self.total_coding_time)} | "
                    status_line += f"Deep Mode: {'Active' if self.deep_mode_active else 'Inactive'}"
                    status_line += " " * 10  # Extra space to overwrite previous output
                    
                    print(status_line, end="")
                    last_status_print = current_time
                
                # Small sleep to prevent CPU spike
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            # Clean exit on Ctrl+C
            print("\nMonitoring stopped.")
            logger.info(f"Monitoring stopped. Total coding time: {self.format_time(self.total_coding_time)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    monitor = CodingTimeMonitor()
    monitor.start_monitoring()