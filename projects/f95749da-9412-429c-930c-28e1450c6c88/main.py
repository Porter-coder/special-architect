"""
Timer Application
A multi-functional timer software with stopwatch, countdown, and history tracking.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List

# File to store timer data and history
DATA_FILE = "timer_data.json"


class DataManager:
    """Manages persistent storage of timer data and history."""

    def __init__(self, filename: str = DATA_FILE):
        self.filename = filename
        self.data = {
            "timers": [],
            "history": []
        }
        self.load_data()

    def load_data(self) -> None:
        """Load data from JSON file if it exists."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self.data["timers"] = loaded_data.get("timers", [])
                    self.data["history"] = loaded_data.get("history", [])
            except (json.JSONDecodeError, IOError):
                self.data = {"timers": [], "history": []}

    def save_data(self) -> None:
        """Save current data to JSON file."""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving data: {e}")

    def add_timer(self, timer_data: Dict) -> int:
        """Add a new timer and save."""
        self.data["timers"].append(timer_data)
        self.save_data()
        return len(self.data["timers"]) - 1

    def update_timer(self, index: int, timer_data: Dict) -> None:
        """Update an existing timer."""
        if 0 <= index < len(self.data["timers"]):
            self.data["timers"][index] = timer_data
            self.save_data()

    def delete_timer(self, index: int) -> None:
        """Delete a timer by index."""
        if 0 <= index < len(self.data["timers"]):
            del self.data["timers"][index]
            self.save_data()

    def add_history(self, history_data: Dict) -> None:
        """Add a history record."""
        self.data["history"].append(history_data)
        self.save_data()

    def get_history(self) -> List[Dict]:
        """Return all history records."""
        return self.data["history"][:]

    def clear_history(self) -> None:
        """Clear all history records."""
        self.data["history"] = []
        self.save_data()


class Timer:
    """Core timer logic for individual timer instances."""

    def __init__(self, name: str, timer_type: str = "stopwatch", duration_seconds: int = 0):
        self.name = name
        self.timer_type = timer_type  # "stopwatch" or "countdown"
        self.duration_seconds = duration_seconds
        self.reset()

    def reset(self) -> None:
        """Reset timer to initial state."""
        self.start_time: Optional[datetime] = None
        self.elapsed_seconds: float = 0
        self.is_running: bool = False
        self.is_paused: bool = False
        self.pause_time: Optional[datetime] = None
        self.total_paused_seconds: float = 0

    def start(self) -> None:
        """Start the timer."""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.start_time = datetime.now()
            if self.timer_type == "countdown":
                self.elapsed_seconds = self.duration_seconds

    def pause(self) -> None:
        """Pause the timer."""
        if self.is_running and not self.is_paused:
            self.is_paused = True
            self.pause_time = datetime.now()

    def resume(self) -> None:
        """Resume a paused timer."""
        if self.is_running and self.is_paused:
            self.is_paused = False
            pause_duration = (datetime.now() - self.pause_time).total_seconds()
            self.total_paused_seconds += pause_duration

    def stop(self) -> float:
        """Stop the timer and return elapsed time."""
        if self.is_running:
            self.update_elapsed()
            self.is_running = False
            self.is_paused = False
        return self.elapsed_seconds

    def update_elapsed(self) -> None:
        """Update elapsed time based on current state."""
        if self.is_running and not self.is_paused and self.start_time:
            current = datetime.now()
            self.elapsed_seconds = (current - self.start_time).total_seconds() - self.total_paused_seconds
            if self.timer_type == "countdown":
                self.elapsed_seconds = self.duration_seconds - self.elapsed_seconds
                if self.elapsed_seconds < 0:
                    self.elapsed_seconds = 0

    def get_display_time(self) -> str:
        """Get formatted time string for display."""
        self.update_elapsed()
        total_seconds = self.elapsed_seconds
        if total_seconds < 0:
            total_seconds = 0

        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((total_seconds * 100) % 100)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:02d}"

    def get_elapsed_seconds(self) -> float:
        """Get elapsed time in seconds."""
        self.update_elapsed()
        return self.elapsed_seconds

    def is_finished(self) -> bool:
        """Check if countdown timer has finished."""
        if self.timer_type == "countdown" and self.is_running:
            self.update_elapsed()
            return self.elapsed_seconds <= 0
        return False

    def to_dict(self) -> Dict:
        """Serialize timer data."""
        return {
            "name": self.name,
            "type": self.timer_type,
            "duration_seconds": self.duration_seconds,
            "elapsed_seconds": self.elapsed_seconds,
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "total_paused_seconds": self.total_paused_seconds
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Timer":
        """Deserialize timer data."""
        timer = cls(data["name"], data["type"], data.get("duration_seconds", 0))
        timer.elapsed_seconds = data.get("elapsed_seconds", 0)
        timer.is_running = data.get("is_running", False)
        timer.is_paused = data.get("is_paused", False)
        timer.total_paused_seconds = data.get("total_paused_seconds", 0)
        start_time_str = data.get("start_time")
        if start_time_str:
            timer.start_time = datetime.fromisoformat(start_time_str)
        return timer


class TimerManager:
    """Manages multiple timer instances."""

    def __init__(self):
        self.timers: List[Timer] = []
        self.data_manager = DataManager()
        self.load_saved_timers()

    def load_saved_timers(self) -> None:
        """Load saved timers from data manager."""
        timer_data_list = self.data_manager.get_history()[-10:]  # Load recent timers
        # For simplicity, we reload timers from history as saved timers
        # In a full implementation, this would be more sophisticated

    def create_timer(self, name: str, timer_type: str = "stopwatch", 
                     duration_seconds: int = 0) -> Timer:
        """Create and add a new timer."""
        timer = Timer(name, timer_type, duration_seconds)
        self.timers.append(timer)
        return timer

    def delete_timer(self, index: int) -> None:
        """Delete a timer by index."""
        if 0 <= index < len(self.timers):
            del self.timers[index]

    def get_timer(self, index: int) -> Optional[Timer]:
        """Get timer by index."""
        if 0 <= index < len(self.timers):
            return self.timers[index]
        return None

    def get_all_timers(self) -> List[Timer]:
        """Return all timers."""
        return self.timers[:]

    def clear_all(self) -> None:
        """Clear all timers."""
        self.timers = []


class TimerApp:
    """Main GUI application for the timer software."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Timer Application")
        self.root.geometry("500x600")
        self.root.resizable(True, True)

        self.manager = TimerManager()
        self.selected_timer_index: Optional[int] = None
        self.update_thread: Optional[threading.Thread] = None
        self.running = True

        self.setup_styles()
        self.create_widgets()
        self.start_update_loop()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_styles(self) -> None:
        """Configure GUI styles."""
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.configure("TLabel", padding=2)
        style.configure("Header.TLabel", font=("Arial", 12, "bold"))

    def create_widgets(self) -> None:
        """Create all GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="Multi-Function Timer", 
                                style="Header.TLabel")
        title_label.pack(pady=(0, 10))

        # Timer list frame
        list_frame = ttk.LabelFrame(main_frame, text="Active Timers", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Timer listbox with scrollbar
        list_scroll = ttk.Scrollbar(list_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.timer_listbox = tk.Listbox(list_frame, height=6, width=40,
                                         yscrollcommand=list_scroll.set,
                                         font=("Consolas", 10))
        self.timer_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.timer_listbox.yview)

        self.timer_listbox.bind("<<ListboxSelect>>", self.on_timer_select)

        # Button frame for timer operations
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)

        self.btn_start = ttk.Button(button_frame, text="Start", 
                                     command=self.start_timer, state=tk.DISABLED)
        self.btn_start.pack(side=tk.LEFT, padx=2)

        self.btn_pause = ttk.Button(button_frame, text="Pause", 
                                     command=self.pause_timer, state=tk.DISABLED)
        self.btn_pause.pack(side=tk.LEFT, padx=2)

        self.btn_stop = ttk.Button(button_frame, text="Stop & Save", 
                                    command=self.stop_timer, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=2)

        self.btn_reset = ttk.Button(button_frame, text="Reset", 
                                     command=self.reset_timer, state=tk.DISABLED)
        self.btn_reset.pack(side=tk.LEFT, padx=2)

        self.btn_delete = ttk.Button(button_frame, text="Delete", 
                                      command=self.delete_timer, state=tk.DISABLED)
        self.btn_delete.pack(side=tk.LEFT, padx=2)

        # Display frame for selected timer
        display_frame = ttk.LabelFrame(main_frame, text="Timer Display", padding="10")
        display_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.timer_name_label = ttk.Label(display_frame, text="No timer selected", 
                                           font=("Arial", 14, "bold"))
        self.timer_name_label.pack(pady=(0, 5))

        self.time_display = ttk.Label(display_frame, text="00:00:00.00", 
                                       font=("Consolas", 24))
        self.time_display.pack(pady=10)

        self.timer_type_label = ttk.Label(display_frame, text="", font=("Arial", 10))
        self.timer_type_label.pack(pady=5)

        # Create new timer frame
        create_frame = ttk.LabelFrame(main_frame, text="Create New Timer", padding="10")
        create_frame.pack(fill=tk.X, pady=5)

        # Timer name input
        name_frame = ttk.Frame(create_frame)
        name_frame.pack(fill=tk.X, pady=2)
        ttk.Label(name_frame, text="Name:").pack(side=tk.LEFT)
        self.entry_name = ttk.Entry(name_frame, width=25)
        self.entry_name.pack(side=tk.LEFT, padx=(5, 0))

        # Timer type selection
        type_frame = ttk.Frame(create_frame)
        type_frame.pack(fill=tk.X, pady=2)
        ttk.Label(type_frame, text="Type:").pack(side=tk.LEFT)

        self.timer_type_var = tk.StringVar(value="stopwatch")
        ttk.Radiobutton(type_frame, text="Stopwatch", 
                        variable=self.timer_type_var, value="stopwatch").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="Countdown", 
                        variable=self.timer_type_var, value="countdown").pack(side=tk.LEFT, padx=5)

        # Duration input (for countdown)
        duration_frame = ttk.Frame(create_frame)
        duration_frame.pack(fill=tk.X, pady=2)
        ttk.Label(duration_frame, text="Duration (minutes):").pack(side=tk.LEFT)
        self.entry_duration = ttk.Entry(duration_frame, width=10)
        self.entry_duration.insert(0, "5")
        self.entry_duration.pack(side=tk.LEFT, padx=(5, 0))

        self.btn_create = ttk.Button(create_frame, text="Create Timer", 
                                      command=self.create_timer)
        self.btn_create.pack(pady=(10, 0))

        # History frame
        history_frame = ttk.LabelFrame(main_frame, text="History", padding="5")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        history_scroll = ttk.Scrollbar(history_frame)
        history_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_listbox = tk.Listbox(history_frame, height=4, width=40,
                                           yscrollcommand=history_scroll.set,
                                           font=("Consolas", 9))
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scroll.config(command=self.history_listbox.yview)

        self.load_history_display()

    def create_timer(self) -> None:
        """Create a new timer based on user input."""
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a timer name.")
            return

        timer_type = self.timer_type_var.get()
        duration_minutes = 5
        duration_seconds = 0

        if timer_type == "countdown":
            try:
                duration_minutes = int(self.entry_duration.get().strip())
                duration_seconds = duration_minutes * 60
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number for duration.")
                return

        timer = self.manager.create_timer(name, timer_type, duration_seconds)
        index = len(self.manager.timers) - 1
        self.timer_listbox.insert(index, f"{name} ({timer_type})")
        self.entry_name.delete(0, tk.END)
        self.update_buttons()

    def on_timer_select(self, event) -> None:
        """Handle timer selection from listbox."""
        selection = self.timer_listbox.curselection()
        if selection:
            self.selected_timer_index = selection[0]
            self.update_timer_display()
            self.update_buttons()

    def update_timer_display(self) -> None:
        """Update the display for selected timer."""
        if self.selected_timer_index is not None:
            timer = self.manager.get_timer(self.selected_timer_index)
            if timer:
                self.timer_name_label.config(text=timer.name)
                self.time_display.config(text=timer.get_display_time())
                type_text = "Countdown" if timer.timer_type == "countdown" else "Stopwatch"
                if timer.timer_type == "countdown":
                    type_text += f" ({timer.duration_seconds // 60} min)"
                self.timer_type_label.config(text=type_text)
                return

        self.timer_name_label.config(text="No timer selected")
        self.time_display.config(text="00:00:00.00")
        self.timer_type_label.config(text="")

    def update_buttons(self) -> None:
        """Update button states based on selected timer."""
        has_selection = self.selected_timer_index is not None

        if has_selection:
            timer = self.manager.get_timer(self.selected_timer_index)
            if timer:
                self.btn_start.config(state=tk.NORMAL)
                self.btn_delete.config(state=tk.NORMAL)

                if timer.is_running:
                    self.btn_start.config(state=tk.DISABLED)
                    if timer.is_paused:
                        self.btn_pause.config(state=tk.DISABLED)
                        self.btn_stop.config(state=tk.NORMAL)
                        self.btn_reset.config(state=tk.NORMAL)
                    else:
                        self.btn_pause.config(state=tk.NORMAL)
                        self.btn_stop.config(state=tk.NORMAL)
                        self.btn_reset.config(state=tk.DISABLED)
                else:
                    self.btn_pause.config(state=tk.DISABLED)
                    self.btn_stop.config(state=tk.DISABLED)
                    self.btn_reset.config(state=tk.NORMAL)
                return

        self.btn_start.config(state=tk.DISABLED)
        self.btn_pause.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_reset.config(state=tk.DISABLED)
        self.btn_delete.config(state=tk.DISABLED)

    def start_timer(self) -> None:
        """Start the selected timer."""
        if self.selected_timer_index is not None:
            timer = self.manager.get_timer(self.selected_timer_index)
            if timer:
                timer.start()
                self.update_buttons()

    def pause_timer(self) -> None:
        """Pause the selected timer."""
        if self.selected_timer_index is not None:
            timer = self.manager.get_timer(self.selected_timer_index)
            if timer:
                if timer.is_paused:
                    timer.resume()
                else:
                    timer.pause()
                self.update_buttons()

    def stop_timer(self) -> None:
        """Stop and save the selected timer."""
        if self.selected_timer_index is not None:
            timer = self.manager.get_timer(self.selected_timer_index)
            if timer and timer.is_running:
                elapsed = timer.stop()
                hours = int(elapsed // 3600)
                minutes = int((elapsed % 3600) // 60)
                seconds = int(elapsed % 60)

                history_entry = {
                    "name": timer.name,
                    "type": timer.timer_type,
                    "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "duration": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
                    "elapsed_seconds": elapsed
                }
                self.manager.data_manager.add_history(history_entry)
                self.load_history_display()
                self.update_buttons()

    def reset_timer(self) -> None:
        """Reset the selected timer."""
        if self.selected_timer_index is not None:
            timer = self.manager.get_timer(self.selected_timer_index)
            if timer:
                timer.reset()
                self.update_timer_display()
                self.update_buttons()

    def delete_timer(self) -> None:
        """Delete the selected timer."""
        if self.selected_timer_index is not None:
            timer = self.manager.get_timer(self.selected_timer_index)
            if timer:
                confirm = messagebox.askyesno("Confirm", 
                                              f"Delete timer '{timer.name}'?")
                if confirm:
                    self.manager.delete_timer(self.selected_timer_index)
                    self.timer_listbox.delete(self.selected_timer_index)
                    self.selected_timer_index = None
                    self.update_timer_display()
                    self.update_buttons()

    def load_history_display(self) -> None:
        """Load history records into the listbox."""
        self.history_listbox.delete(0, tk.END)
        history = self.manager.data_manager.get_history()
        for entry in reversed(history[-20:]):
            display_text = f"{entry['start_time']} - {entry['name']}: {entry['duration']}"
            self.history_listbox.insert(tk.END, display_text)

    def start_update_loop(self) -> None:
        """Start the background update loop for timer displays."""
        def update_loop():
            while self.running:
                try:
                    if self.selected_timer_index is not None:
                        timer = self.manager.get_timer(self.selected_timer_index)
                        if timer and timer.is_running:
                            self.root.after(0, self.update_timer_display)
                    time.sleep(0.05)  # Update every 50ms for smooth display
                except Exception:
                    pass

        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()

    def on_close(self) -> None:
        """Handle window close event."""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=1)
        self.root.destroy()

    def run(self) -> None:
        """Start the application."""
        self.root.mainloop()


def main():
    """Main entry point for the timer application."""
    print("=== Timer Application ===")
    print("Starting timer application with GUI interface...")
    print("If no window appears, please check your display settings.")
    print()
    print("Features:")
    print("- Create stopwatch or countdown timers")
    print("- Start, pause, resume, and stop timers")
    print("- Automatic history tracking")
    print("- Multiple simultaneous timers")
    print()
    print("Creating application window...")

    app = TimerApp()
    app.run()


if __name__ == "__main__":
    main()