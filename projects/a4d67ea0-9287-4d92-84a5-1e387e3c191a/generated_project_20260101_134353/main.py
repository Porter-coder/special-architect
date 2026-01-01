"""
Text Editor - A simple but functional text editor built with Python tkinter.
Supports file operations, text editing, undo/redo, line numbers, and more.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
import os

class TextEditor:
    """A simple text editor with common editing features."""

    def __init__(self, root):
        """Initialize the text editor application."""
        self.root = root
        self.root.title("Untitled - Text Editor")
        self.root.geometry("900x650")

        # Track current file path
        self.current_file = None

        # Track modification state
        self.modified = False

        # Create all UI components
        self.create_menu_bar()
        self.create_toolbar()
        self.create_text_area()
        self.create_status_bar()

        # Bind events and shortcuts
        self.bind_events()
        self.bind_shortcuts()

        # Set up close protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_menu_bar(self):
        """Create the application menu bar."""
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.new_file,
                                   accelerator="Ctrl+N")
        self.file_menu.add_command(label="Open", command=self.open_file,
                                   accelerator="Ctrl+O")
        self.file_menu.add_command(label="Save", command=self.save_file,
                                   accelerator="Ctrl+S")
        self.file_menu.add_command(label="Save As", command=self.save_as_file,
                                   accelerator="Ctrl+Shift+S")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.on_close)

        # Edit menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Undo", command=self.undo,
                                   accelerator="Ctrl+Z")
        self.edit_menu.add_command(label="Redo", command=self.redo,
                                   accelerator="Ctrl+Y")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut", command=self.cut_text,
                                   accelerator="Ctrl+X")
        self.edit_menu.add_command(label="Copy", command=self.copy_text,
                                   accelerator="Ctrl+C")
        self.edit_menu.add_command(label="Paste", command=self.paste_text,
                                   accelerator="Ctrl+V")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Select All", command=self.select_all,
                                   accelerator="Ctrl+A")

        # View menu
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_checkbutton(label="Show Line Numbers",
                                       variable=tk.BooleanVar(value=True),
                                       command=self.toggle_line_numbers)
        self.view_menu.add_checkbutton(label="Show Status Bar",
                                       variable=tk.BooleanVar(value=True),
                                       command=self.toggle_status_bar)

        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)

    def create_toolbar(self):
        """Create the toolbar with action buttons."""
        self.toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED, bg="#f0f0f0")

        # Toolbar buttons data: (label, command, tooltip)
        buttons = [
            ("New", self.new_file, "New File"),
            ("Open", self.open_file, "Open File"),
            ("Save", self.save_file, "Save File"),
            ("Save As", self.save_as_file, "Save As"),
            (None, None, None),  # Separator
            ("Cut", self.cut_text, "Cut"),
            ("Copy", self.copy_text, "Copy"),
            ("Paste", self.paste_text, "Paste"),
            (None, None, None),  # Separator
            ("Undo", self.undo, "Undo"),
            ("Redo", self.redo, "Redo"),
        ]

        for label, command, tooltip in buttons:
            if label is None:
                tk.Frame(self.toolbar, width=2, bd=0, bg="#f0f0f0").pack(
                    side=tk.LEFT, padx=2)
            else:
                btn = tk.Button(
                    self.toolbar,
                    text=label,
                    command=command,
                    relief=tk.FLAT,
                    bg="#f0f0f0",
                    font=("Arial", 9)
                )
                btn.pack(side=tk.LEFT, padx=2, pady=2)
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#e0e0e0"))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#f0f0f0"))

        self.toolbar.pack(side=tk.TOP, fill=tk.X)

    def create_text_area(self):
        """Create the main text editing area with line numbers."""
        # Main container for text area and line numbers
        self.text_frame = tk.Frame(self.root)

        # Line number canvas
        self.line_numbers = tk.Canvas(
            self.text_frame,
            width=45,
            bg="#f5f5f5",
            highlightthickness=0,
            takefocus=0
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Scrolled text area
        self.text_area = ScrolledText(
            self.text_frame,
            wrap=tk.WORD,
            undo=True,
            autoseparators=True,
            maxundo=50,
            font=("Consolas", 11),
            bg="white",
            fg="black",
            insertbackground="black",
            selectbackground="#0078d7",
            selectforeground="white"
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.text_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Configure text area tags for selection
        self.text_area.tag_config("sel", background="#0078d7",
                                  foreground="white")

        # Update line numbers on scroll
        self.text_area.bind("<Configure>", self.update_line_numbers)
        self.text_area.bind("<<Modified>>", self.on_text_modified)
        self.text_area.bind("<KeyRelease>", self.on_key_release)
        self.text_area.bind("<ButtonRelease-1>", self.on_key_release)

        # Mouse wheel scrolling for line numbers
        self.line_numbers.bind("<MouseWheel>", self.on_mouse_wheel)
        self.text_area.bind("<MouseWheel>", self.on_mouse_wheel)

    def create_status_bar(self):
        """Create the status bar at the bottom."""
        self.status_bar = tk.Label(
            self.root,
            text="Ln 1, Col 1 | UTF-8 | Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 9),
            padx=5
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def bind_events(self):
        """Bind various events to handlers."""
        self.text_area.bind("<<Modified>>", self.on_text_modified)
        self.text_area.bind("<<Selection>>", self.on_selection_change)

    def bind_shortcuts(self):
        """Bind keyboard shortcuts."""
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-S>", lambda e: self.save_as_file())
        self.root.bind("<Control-a>", lambda e: self.select_all())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())

    def update_line_numbers(self, event=None):
        """Update the line number display."""
        # Get line count
        line_count = self.text_area.index('end-1c').split('.')[0]
        line_count = int(line_count)

        # Calculate line height
        line_height = self.text_area.dlineinfo("1.0")
        if line_height:
            line_height = line_height[3]
        else:
            line_height = 20

        # Clear existing line numbers
        self.line_numbers.delete("all")

        # Draw line numbers
        for i in range(1, line_count + 1):
            y_pos = (i - 1) * line_height + 3
            self.line_numbers.create_text(
                40, y_pos,
                text=str(i),
                anchor="ne",
                font=("Consolas", 10),
                fill="#666666"
            )

        # Update canvas size
        self.line_numbers.config(height=self.text_area.winfo_height())

    def on_mouse_wheel(self, event):
        """Handle mouse wheel scrolling."""
        self.text_area.yview_scroll(-int(event.delta / 120), "units")
        self.update_line_numbers()
        return "break"

    def on_text_modified(self, event):
        """Handle text modification."""
        if self.text_area.edit_modified():
            self.modified = True
            self.update_title()
            self.text_area.edit_modified(False)

    def on_key_release(self, event=None):
        """Handle key release events."""
        self.update_line_numbers()
        self.update_cursor_position()
        self.text_area.edit_modified(False)

    def on_selection_change(self, event=None):
        """Handle selection change events."""
        self.update_cursor_position()

    def update_cursor_position(self):
        """Update the status bar with current cursor position."""
        cursor_pos = self.text_area.index(tk.INSERT)
        parts = cursor_pos.split(".")
        line_num = parts[0]
        col_num = parts[1]

        # Calculate column number properly
        current_line = self.text_area.get(f"{line_num}.0", cursor_pos)
        col_num = len(current_line)

        self.status_bar.config(
            text=f"Ln {line_num}, Col {col_num + 1} | UTF-8"
        )

    def update_title(self):
        """Update the window title with file name and modified state."""
        if self.current_file:
            file_name = os.path.basename(self.current_file)
        else:
            file_name = "Untitled"

        if self.modified:
            self.root.title(f"{file_name}* - Text Editor")
        else:
            self.root.title(f"{file_name} - Text Editor")

    def new_file(self):
        """Create a new file."""
        if self.modified:
            response = self.confirm_discard()
            if response == "cancel":
                return

        self.text_area.delete(1.0, tk.END)
        self.text_area.edit_reset()
        self.current_file = None
        self.modified = False
        self.update_title()
        self.update_line_numbers()

    def open_file(self):
        """Open an existing file."""
        if self.modified:
            response = self.confirm_discard()
            if response == "cancel":
                return

        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("All Files", "*.*"),
                ("Text Files", "*.txt"),
                ("Python Files", "*.py"),
                ("HTML Files", "*.html"),
                ("CSS Files", "*.css"),
                ("JavaScript Files", "*.js"),
            ]
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, content)
                self.text_area.edit_reset()
                self.current_file = file_path
                self.modified = False
                self.update_title()
                self.update_line_numbers()

            except UnicodeDecodeError:
                # Try with different encoding
                try:
                    with open(file_path, "r", encoding="latin-1") as f:
                        content = f.read()

                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(1.0, content)
                    self.text_area.edit_reset()
                    self.current_file = file_path
                    self.modified = False
                    self.update_title()
                    self.update_line_numbers()

                except Exception as e:
                    messagebox.showerror("Error", f"Cannot open file: {e}")

            except Exception as e:
                messagebox.showerror("Error", f"Cannot open file: {e}")

    def save_file(self):
        """Save the current file."""
        if self.current_file:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(content)
                self.modified = False
                self.update_title()

            except Exception as e:
                messagebox.showerror("Error", f"Cannot save file: {e}")
        else:
            self.save_as_file()

    def save_as_file(self):
        """Save the current file with a new name."""
        file_path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".txt",
            filetypes=[
                ("All Files", "*.*"),
                ("Text Files", "*.txt"),
                ("Python Files", "*.py"),
                ("HTML Files", "*.html"),
                ("CSS Files", "*.css"),
                ("JavaScript Files", "*.js"),
            ]
        )

        if file_path:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.current_file = file_path
                self.modified = False
                self.update_title()

            except Exception as e:
                messagebox.showerror("Error", f"Cannot save file: {e}")

    def confirm_discard(self):
        """Confirm if user wants to discard unsaved changes."""
        response = messagebox.askyesnocancel(
            "Unsaved Changes",
            "You have unsaved changes. Do you want to save them?"
        )
        if response is None:
            return "cancel"
        elif response:
            if self.current_file:
                self.save_file()
            else:
                self.save_as_file()
        return "discard"

    def on_close(self):
        """Handle window close event."""
        if self.modified:
            response = self.confirm_discard()
            if response == "cancel":
                return

        self.root.destroy()

    def undo(self):
        """Undo the last action."""
        try:
            self.text_area.edit_undo()
        except tk.TclError:
            pass

    def redo(self):
        """Redo the last undone action."""
        try:
            self.text_area.edit_redo()
        except tk.TclError:
            pass

    def cut_text(self):
        """Cut selected text to clipboard."""
        self.copy_text()
        self.text_area.delete("sel.first", "sel.last")

    def copy_text(self):
        """Copy selected text to clipboard."""
        try:
            selected = self.text_area.get("sel.first", "sel.last")
            self.root.clipboard_clear()
            self.root.clipboard_append(selected)
        except tk.TclError:
            pass

    def paste_text(self):
        """Paste text from clipboard."""
        try:
            clipboard_text = self.root.clipboard_get()
            self.text_area.insert(tk.INSERT, clipboard_text)
        except tk.TclError:
            pass

    def select_all(self):
        """Select all text in the editor."""
        self.text_area.tag_add("sel", "1.0", tk.END)
        self.text_area.mark_set("insert", "1.0")
        self.text_area.see("1.0")

    def toggle_line_numbers(self):
        """Toggle line number visibility."""
        if self.line_numbers.winfo_ismapped():
            self.line_numbers.pack_forget()
        else:
            self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
            self.update_line_numbers()

    def toggle_status_bar(self):
        """Toggle status bar visibility."""
        if self.status_bar.winfo_ismapped():
            self.status_bar.pack_forget()
        else:
            self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def show_about(self):
        """Show the about dialog."""
        messagebox.showinfo(
            "About Text Editor",
            "Text Editor\n\n"
            "A simple but functional text editor\n"
            "built with Python and tkinter.\n\n"
            "Features:\n"
            "- File operations (New, Open, Save, Save As)\n"
            "- Undo/Redo\n"
            "- Cut/Copy/Paste\n"
            "- Line numbers\n"
            "- Status bar\n\n"
            "Version: 1.0"
        )

def main():
    """Main entry point for the text editor application."""
    print("=== Text Editor ===")
    print("Starting Text Editor...")
    print("Features: New, Open, Save, Save As, Undo/Redo, Cut/Copy/Paste, Line Numbers")
    print("Keyboard Shortcuts:")
    print("  Ctrl+N - New File")
    print("  Ctrl+O - Open File")
    print("  Ctrl+S - Save File")
    print("  Ctrl+Shift+S - Save As")
    print("  Ctrl+Z - Undo")
    print("  Ctrl+Y - Redo")
    print("  Ctrl+A - Select All")
    print("")

    # Create the main window
    root = tk.Tk()

    # Set app icon (optional, uses default tk icon)
    root.option_add("*Font", "Arial 10")

    # Create the text editor
    app = TextEditor(root)

    # Demo: Create a sample file to show editor capabilities
    sample_text = """# Welcome to Text Editor!

This is a simple but functional text editor built with Python and tkinter.

## Features:
- File operations (New, Open, Save, Save As)
- Undo and Redo functionality
- Cut, Copy, and Paste
- Line numbers
- Status bar with cursor position
- Keyboard shortcuts

## Keyboard Shortcuts:
  Ctrl+N - New File
  Ctrl+O - Open File  
  Ctrl+S - Save File
  Ctrl+Shift+S - Save As
  Ctrl+Z - Undo
  Ctrl+Y - Redo
  Ctrl+A - Select All

Try editing this text or open a new file using the File menu!
"""

    app.text_area.insert(1.0, sample_text)
    app.text_area.edit_reset()
    app.modified = False
    app.update_title()
    app.update_line_numbers()

    # Start the main event loop
    root.mainloop()
    print("Text Editor closed.")

if __name__ == "__main__":
    main()