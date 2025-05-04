import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import json
import time

# Add parent directory to path if running main.py directly
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Use absolute imports
from ui.main_window import MainWindow
from core.rotation import RotationManager
import spell_data

class Application:
    def __init__(self):
        """Initialize the application"""
        self.check_dependencies()
        self.load_settings()
        self.start_application()

    def check_dependencies(self):
        """Check if all required dependencies are available"""
        try:
            import tkinter
            import json
            # Add any other dependency checks here
        except ImportError as e:
            messagebox.showerror(
                "Dependency Error",
                f"Missing required dependency: {str(e)}\n"
                "Please install all required dependencies and try again."
            )
            sys.exit(1)

    def load_settings(self):
        """Load application settings"""
        self.settings = {
            "window_size": "1400x900",
            "theme": "modern",
            "recent_files": [],
            "auto_save": True,
            "backup_enabled": True,
            "backup_interval": 300,  # 5 minutes
            "max_recent_files": 10
        }

        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
        except Exception as e:
            messagebox.showwarning(
                "Settings Warning",
                f"Could not load settings: {str(e)}\n"
                "Using default settings instead."
            )

    def save_settings(self):
        """Save application settings"""
        try:
            with open("settings.json", "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            messagebox.showwarning(
                "Settings Warning",
                f"Could not save settings: {str(e)}"
            )

    def setup_logging(self):
        """Setup application logging"""
        import logging
        
        # Create logs directory if it doesn't exist
        if not os.path.exists("logs"):
            os.makedirs("logs")

        # Setup logging configuration
        logging.basicConfig(
            filename=os.path.join("logs", "soe_builder.log"),
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        logging.getLogger('').addHandler(console_handler)

    def setup_exception_handling(self):
        """Setup global exception handling"""
        def handle_exception(exc_type, exc_value, exc_traceback):
            """Handle uncaught exceptions"""
            if issubclass(exc_type, KeyboardInterrupt):
                # Handle normal exit
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            import logging
            logging.error(
                "Uncaught exception",
                exc_info=(exc_type, exc_value, exc_traceback)
            )

            messagebox.showerror(
                "Error",
                f"An unexpected error occurred:\n{str(exc_value)}\n\n"
                "The error has been logged. Please check the log file for details."
            )

        sys.excepthook = handle_exception

    def create_backup_directory(self):
        """Create backup directory if it doesn't exist"""
        backup_dir = os.path.join(os.path.dirname(__file__), "backups")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        return backup_dir

    def start_application(self):
        """Start the main application"""
        try:
            # Setup logging and exception handling
            self.setup_logging()
            self.setup_exception_handling()

            # Create backup directory
            self.create_backup_directory()

            # Initialize the main window
            self.window = MainWindow()

            # Configure window from settings
            self.window.geometry(self.settings["window_size"])
            
            # Set window icon if available
            icon_path = os.path.join(
                os.path.dirname(__file__),
                "resources",
                "icons",
                "app_icon.png"
            )
            if os.path.exists(icon_path):
                self.window.iconphoto(True, tk.PhotoImage(file=icon_path))

            # Load recent files
            if self.settings["recent_files"]:
                self.window._load_recent_files()

            # Setup auto-save if enabled
            if self.settings["auto_save"]:
                self.setup_auto_save()

            # Setup backup if enabled
            if self.settings["backup_enabled"]:
                self.setup_backup()

            # Bind closing event
            self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

            # Start the application
            self.window.mainloop()

        except Exception as e:
            messagebox.showerror(
                "Startup Error",
                f"Failed to start application: {str(e)}"
            )
            sys.exit(1)

    def setup_auto_save(self):
        """Setup auto-save functionality"""
        def auto_save():
            if self.window.current_rotation and self.window.last_save_path:
                self.window._save_rotation_to_file(self.window.last_save_path)
            self.window.after(60000, auto_save)  # Auto-save every minute

        self.window.after(60000, auto_save)

    def setup_backup(self):
        """Setup backup functionality"""
        def create_backup():
            if self.window.current_rotation:
                backup_dir = self.create_backup_directory()
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                backup_file = os.path.join(
                    backup_dir,
                    f"backup_{timestamp}.json"
                )
                self.window._save_rotation_to_file(backup_file)
            
            # Schedule next backup
            self.window.after(
                self.settings["backup_interval"] * 1000,
                create_backup
            )

        self.window.after(
            self.settings["backup_interval"] * 1000,
            create_backup
        )

    def on_closing(self):
        """Handle application closing"""
        # Save window size
        self.settings["window_size"] = self.window.geometry()
        
        # Save settings
        self.save_settings()
        
        # Close application
        self.window.destroy()

def main():
    """Main entry point"""
    app = Application()

if __name__ == "__main__":
    main()