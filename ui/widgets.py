import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Any
import re

class ModernFrame(ttk.Frame):
    """Modern styled frame"""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, style="Modern.TFrame", **kwargs)

class ModernLabel(ttk.Label):
    """Modern styled label"""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, style="Modern.TLabel", **kwargs)

class ModernButton(ttk.Button):
    """Modern styled button with hover effects"""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, style="Modern.TButton", **kwargs)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        """Handle mouse enter"""
        if self["state"] != "disabled":
            self.configure(style="Modern.TButton.Hover")

    def _on_leave(self, event):
        """Handle mouse leave"""
        if self["state"] != "disabled":
            self.configure(style="Modern.TButton")

class ModernCombobox(ttk.Combobox):
    """Modern styled combobox with search functionality"""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, style="Modern.TCombobox", **kwargs)
        
        self._original_values = []
        self._filtered_values = []
        self._last_search = ""
        
        self.bind("<KeyRelease>", self._on_key_release)
        self.bind("<<ComboboxSelected>>", self._on_select)

    def configure(self, **kwargs):
        """Override configure to capture values"""
        if "values" in kwargs:
            self._original_values = list(kwargs["values"])
        super().configure(**kwargs)

    def _on_key_release(self, event):
        """Handle key release for search"""
        if self["state"] == "readonly":
            return

        current_text = self.get().lower()
        if current_text == self._last_search:
            return

        self._last_search = current_text
        self._filtered_values = [
            value for value in self._original_values
            if current_text in str(value).lower()
        ]
        
        self["values"] = self._filtered_values
        
        if self._filtered_values:
            self.event_generate("<Down>")

    def _on_select(self, event):
        """Handle selection"""
        self._last_search = ""
        self["values"] = self._original_values

class SearchEntry(ttk.Entry):
    """Search entry with placeholder text and clear button"""
    def __init__(self, master=None, placeholder="", **kwargs):
        super().__init__(master, style="Search.TEntry", **kwargs)
        
        self.placeholder = placeholder
        self.placeholder_color = "gray"
        self.default_fg_color = self["foreground"]
        self.showing_placeholder = False

        # Create clear button
        self.clear_button = ModernButton(
            master,
            text="×",
            width=2,
            command=self.clear
        )
        
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<KeyRelease>", self._on_key_release)
        
        self._show_placeholder()

    def _show_placeholder(self):
        """Show placeholder text"""
        if not self.get() and not self.showing_placeholder:
            self.showing_placeholder = True
            self["foreground"] = self.placeholder_color
            self.insert(0, self.placeholder)

    def _hide_placeholder(self):
        """Hide placeholder text"""
        if self.showing_placeholder:
            self.showing_placeholder = False
            self["foreground"] = self.default_fg_color
            self.delete(0, tk.END)

    def _on_focus_in(self, event):
        """Handle focus in"""
        if self.showing_placeholder:
            self._hide_placeholder()

    def _on_focus_out(self, event):
        """Handle focus out"""
        if not self.get():
            self._show_placeholder()

    def _on_key_release(self, event):
        """Handle key release"""
        if self.get():
            self.clear_button.place(
                relx=1.0,
                rely=0.5,
                anchor="e",
                x=-5,
                y=0
            )
        else:
            self.clear_button.place_forget()

    def clear(self):
        """Clear the entry"""
        self.delete(0, tk.END)
        self.clear_button.place_forget()
        self._show_placeholder()

    def get(self) -> str:
        """Override get to handle placeholder"""
        if self.showing_placeholder:
            return ""
        return super().get()

class ModernTreeview(ttk.Treeview):
    """Modern styled treeview with enhanced features"""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, style="Modern.Treeview", **kwargs)
        
        # Setup alternating row colors
        self.tag_configure("oddrow", background="#f5f5f5")
        self.tag_configure("evenrow", background="#ffffff")
        
        self.bind("<<TreeviewSelect>>", self._on_select)
        self._last_selected = None

    def insert(self, parent, index, **kwargs):
        """Override insert to add alternating row colors"""
        item = super().insert(parent, index, **kwargs)
        
        # Add alternating row tags
        items = self.get_children(parent)
        for i, item in enumerate(items):
            self.item(item, tags=("evenrow" if i % 2 == 0 else "oddrow",))
            
        return item

    def delete(self, *items):
        """Override delete to maintain alternating row colors"""
        super().delete(*items)
        
        # Reapply alternating row tags
        items = self.get_children("")
        for i, item in enumerate(items):
            self.item(item, tags=("evenrow" if i % 2 == 0 else "oddrow",))

    def move(self, item, parent, index):
        """Override move to maintain alternating row colors"""
        super().move(item, parent, index)
        
        # Reapply alternating row tags
        items = self.get_children(parent)
        for i, item in enumerate(items):
            self.item(item, tags=("evenrow" if i % 2 == 0 else "oddrow",))

    def _on_select(self, event):
        """Handle selection"""
        selection = self.selection()
        if selection:
            self._last_selected = selection[0]
        else:
            self._last_selected = None

class ModernNotebook(ttk.Notebook):
    """Modern styled notebook with tab features"""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, style="Modern.TNotebook", **kwargs)
        
        self.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self._active_tab = None

    def _on_tab_changed(self, event):
        """Handle tab changes"""
        self._active_tab = self.select()

    def add_closeable_tab(self, child, **kwargs):
        """Add a tab with close button"""
        self.add(child, **kwargs)
        
        # Create close button
        close_button = ModernButton(
            child,
            text="×",
            width=2,
            command=lambda: self.remove_tab(child)
        )
        close_button.pack(side="right", padx=2, pady=2)

    def remove_tab(self, tab):
        """Remove a tab"""
        self.forget(tab)

class ModernSpinbox(ttk.Spinbox):
    """Modern styled spinbox with validation"""
    def __init__(self, master=None, **kwargs):
        validate_command = kwargs.pop("validate_command", None)
        
        super().__init__(
            master,
            style="Modern.TSpinbox",
            validate="key",
            validatecommand=(self.register(self._validate), "%P"),
            **kwargs
        )
        
        self._validate_command = validate_command

    def _validate(self, value):
        """Validate input"""
        if not value:
            return True

        try:
            if self._validate_command:
                return self._validate_command(value)
            return True
        except:
            return False

class ModernProgressbar(ttk.Progressbar):
    """Modern styled progressbar with text"""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, style="Modern.Horizontal.TProgressbar", **kwargs)
        
        self._text_var = tk.StringVar()
        self._text_label = ModernLabel(
            master,
            textvariable=self._text_var,
            background=self["background"]
        )

    def start(self, interval=None):
        """Start progress animation"""
        super().start(interval)
        self._update_text()

    def stop(self):
        """Stop progress animation"""
        super().stop()
        self._update_text()

    def step(self, amount=None):
        """Step progress"""
        super().step(amount)
        self._update_text()

    def _update_text(self):
        """Update progress text"""
        value = self["value"]
        maximum = self["maximum"]
        
        if maximum > 0:
            percentage = int((value / maximum) * 100)
            self._text_var.set(f"{percentage}%")
        else:
            self._text_var.set("")

class ModernScale(ttk.Scale):
    """Modern styled scale with value display"""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, style="Modern.Horizontal.TScale", **kwargs)
        
        self._value_var = tk.StringVar()
        self._value_label = ModernLabel(
            master,
            textvariable=self._value_var
        )
        
        self.bind("<Motion>", self._update_value_label)
        self.bind("<Button-1>", self._update_value_label)

    def _update_value_label(self, event):
        """Update value label"""
        value = self.get()
        self._value_var.set(f"{value:.1f}")
        
        # Position label above thumb
        width = self.winfo_width()
        slider_value = (value - self["from"]) / (self["to"] - self["from"])
        x = width * slider_value
        
        self._value_label.place(
            x=x,
            y=-20,
            anchor="s"
        )

class ModernCheckbutton(ttk.Checkbutton):
    """Modern styled checkbutton"""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, style="Modern.TCheckbutton", **kwargs)

class ModernRadiobutton(ttk.Radiobutton):
    """Modern styled radiobutton"""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, style="Modern.TRadiobutton", **kwargs)

class ModernScrollbar(ttk.Scrollbar):
    """Modern styled scrollbar with auto-hide"""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, style="Modern.Vertical.TScrollbar", **kwargs)
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        self._timer = None
        self._visible = True

    def _on_enter(self, event):
        """Handle mouse enter"""
        if self._timer:
            self.after_cancel(self._timer)
        self.show()

    def _on_leave(self, event):
        """Handle mouse leave"""
        self._timer = self.after(1000, self.hide)

    def show(self):
        """Show scrollbar"""
        if not self._visible:
            self._visible = True
            self.configure(width=16)

    def hide(self):
        """Hide scrollbar"""
        if self._visible:
            self._visible = False
            self.configure(width=4)

def setup_styles():
    """Setup modern styles for all widgets"""
    style = ttk.Style()
    
    # Frame style
    style.configure(
        "Modern.TFrame",
        background="#ffffff",
        relief="flat"
    )
    
    # Label style
    style.configure(
        "Modern.TLabel",
        background="#ffffff",
        foreground="#333333",
        font=("Segoe UI", 10)
    )
    
    # Button styles
    style.configure(
        "Modern.TButton",
        background="#007bff",
        foreground="#ffffff",
        padding=(10, 5),
        font=("Segoe UI", 10),
        relief="flat"
    )
    
    style.map(
        "Modern.TButton",
        background=[
            ("active", "#0056b3"),
            ("disabled", "#cccccc")
        ],
        foreground=[
            ("disabled", "#666666")
        ]
    )
    
    # Combobox styles
    style.configure(
        "Modern.TCombobox",
        background="#ffffff",
        fieldbackground="#ffffff",
        foreground="#333333",
        arrowcolor="#333333",
        padding=(5, 2),
        font=("Segoe UI", 10)
    )
    
    # Entry styles
    style.configure(
        "Search.TEntry",
        padding=(5, 2),
        font=("Segoe UI", 10)
    )
    
    # Treeview styles
    style.configure(
        "Modern.Treeview",
        background="#ffffff",
        foreground="#333333",
        fieldbackground="#ffffff",
        font=("Segoe UI", 10),
        rowheight=25
    )
    
    style.map(
        "Modern.Treeview",
        background=[
            ("selected", "#007bff")
        ],
        foreground=[
            ("selected", "#ffffff")
        ]
    )
    
    # Notebook styles
    style.configure(
        "Modern.TNotebook",
        background="#ffffff",
        tabmargins=(2, 5, 2, 0)
    )
    
    style.configure(
        "Modern.TNotebook.Tab",
        padding=(10, 5),
        font=("Segoe UI", 10)
    )
    
    # Scrollbar styles
    style.configure(
        "Modern.Vertical.TScrollbar",
        background="#cccccc",
        troughcolor="#ffffff",
        width=16,
        arrowsize=13
    )
    
    # Scale styles
    style.configure(
        "Modern.Horizontal.TScale",
        background="#ffffff",
        troughcolor="#007bff",
        sliderwidth=15,
        sliderlength=15
    )
    
    # Progressbar styles
    style.configure(
        "Modern.Horizontal.TProgressbar",
        background="#007bff",
        troughcolor="#e9ecef",
        bordercolor="#ffffff",
        lightcolor="#ffffff",
        darkcolor="#ffffff"
    )
    
    # Checkbutton styles
    style.configure(
        "Modern.TCheckbutton",
        background="#ffffff",
        font=("Segoe UI", 10)
    )
    
    # Radiobutton styles
    style.configure(
        "Modern.TRadiobutton",
        background="#ffffff",
        font=("Segoe UI", 10)
    )

# Initialize styles
setup_styles()