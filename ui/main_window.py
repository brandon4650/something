import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import time
from typing import Dict, List, Optional, Any, Tuple

# Use absolute imports
from ui.spell_panel import SpellPanel
from ui.condition_panel import ConditionPanel
from ui.rotation_panel import RotationPanel
from ui.widgets import ModernFrame, ModernButton, ModernLabel, ModernCombobox
from core.rotation import Rotation, RotationManager
from core.validator import RotationValidator
from core.exporter import RotationExporter, RotationImporter
import spell_data

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("SOE Rotation Builder")
        self.geometry("1400x900")
        self.minsize(1200, 800)

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure modern styles
        self._configure_styles()

        # State variables
        self.current_class = tk.StringVar()
        self.current_spec = tk.StringVar()
        self.current_rotation: Optional[Rotation] = None
        self.rotation_manager = RotationManager()
        self.last_save_path: Optional[str] = None

        # Setup UI components
        self._create_menu()
        self._create_main_layout()
        self._bind_events()

        # Load recent files
        self.recent_files = self._load_recent_files()

        # Update recent files menu
        self._update_recent_files_menu()

    def _configure_styles(self):
        """Configure custom styles for the application"""
        # Main frame style
        self.style.configure(
            "Modern.TFrame",
            background="#f0f0f0",
            relief="flat"
        )

        # Button styles
        self.style.configure(
            "Modern.TButton",
            padding=6,
            relief="flat",
            background="#007bff",
            foreground="white"
        )
        
        self.style.map(
            "Modern.TButton",
            background=[("active", "#0056b3")],
            relief=[("pressed", "sunken")]
        )

        # Label styles
        self.style.configure(
            "Modern.TLabel",
            padding=4,
            background="#f0f0f0",
            font=("Segoe UI", 10)
        )

        # Combobox styles
        self.style.configure(
            "Modern.TCombobox",
            padding=4,
            relief="flat"
        )

        # Separator styles
        self.style.configure(
            "Modern.TSeparator",
            background="#d0d0d0"
        )

    def _create_menu(self):
        """Create the main menu bar"""
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New Rotation", command=self._new_rotation)
        self.file_menu.add_command(label="Open...", command=self._open_rotation)
        self.file_menu.add_command(label="Save", command=self._save_rotation)
        self.file_menu.add_command(label="Save As...", command=self._save_rotation_as)
        self.file_menu.add_separator()
        
        # Recent files submenu
        self.recent_menu = tk.Menu(self.file_menu, tearoff=0)
        self.file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit)

        # Edit menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Validate Rotation", command=self._validate_rotation)
        self.edit_menu.add_command(label="Analyze Rotation", command=self._analyze_rotation)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Preferences", command=self._show_preferences)

        # Export menu
        self.export_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Export", menu=self.export_menu)
        self.export_menu.add_command(label="Export as SOE...", 
                                   command=lambda: self._export_rotation('soe'))
        self.export_menu.add_command(label="Export as JSON...", 
                                   command=lambda: self._export_rotation('json'))
        self.export_menu.add_command(label="Export as XML...", 
                                   command=lambda: self._export_rotation('xml'))
        self.export_menu.add_command(label="Export as Lua...", 
                                   command=lambda: self._export_rotation('lua'))

        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="Documentation", command=self._show_documentation)
        self.help_menu.add_command(label="About", command=self._show_about)

    def _create_main_layout(self):
        """Create the main application layout"""
        # Main container
        self.main_container = ModernFrame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Top bar with class/spec selection
        self.top_bar = ModernFrame(self.main_container)
        self.top_bar.pack(fill=tk.X, padx=5, pady=5)

        ModernLabel(self.top_bar, text="Class:").pack(side=tk.LEFT, padx=(0, 5))
        self.class_combo = ModernCombobox(
            self.top_bar,
            textvariable=self.current_class,
            values=spell_data.get_available_classes(),
            state="readonly",
            width=20
        )
        self.class_combo.pack(side=tk.LEFT, padx=5)

        ModernLabel(self.top_bar, text="Specialization:").pack(side=tk.LEFT, padx=(10, 5))
        self.spec_combo = ModernCombobox(
            self.top_bar,
            textvariable=self.current_spec,
            state="readonly",
            width=20
        )
        self.spec_combo.pack(side=tk.LEFT, padx=5)

        # Main content area
        self.content_frame = ModernFrame(self.main_container)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel (Spell Selection)
        self.spell_panel = SpellPanel(self.content_frame)
        self.spell_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Center panel (Condition Builder)
        self.condition_panel = ConditionPanel(self.content_frame)
        self.condition_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Right panel (Rotation Builder)
        self.rotation_panel = RotationPanel(self.content_frame)
        self.rotation_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Status bar
        self.status_bar = ModernFrame(self.main_container)
        self.status_bar.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_label = ModernLabel(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT)

    def _bind_events(self):
        """Bind event handlers"""
        self.class_combo.bind('<<ComboboxSelected>>', self._on_class_selected)
        self.spec_combo.bind('<<ComboboxSelected>>', self._on_spec_selected)
        
        # Bind panels events
        self.spell_panel.on_spell_selected = self._on_spell_selected
        self.condition_panel.on_condition_created = self._on_condition_created
        self.rotation_panel.on_spell_moved = self._on_rotation_spell_moved
        self.rotation_panel.on_spell_removed = self._on_rotation_spell_removed

        # Bind window close event
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_class_selected(self, event):
        """Handle class selection"""
        class_name = self.current_class.get()
        specs = spell_data.get_specs_for_class(class_name)
        self.spec_combo['values'] = specs
        if specs:
            self.spec_combo.set(specs[0])
            self._on_spec_selected(None)

    def _on_spec_selected(self, event):
        """Handle specialization selection"""
        class_name = self.current_class.get()
        spec_name = self.current_spec.get()
        
        if class_name and spec_name:
            # Update spell panel
            spells = spell_data.get_spells_for_spec(class_name, spec_name)
            self.spell_panel.update_spells(spells)
            
            # Update condition panel
            self.condition_panel.set_class(class_name)
            
            # Create new rotation if none exists
            if not self.current_rotation:
                self.current_rotation = Rotation(class_name, spec_name)
                self.rotation_panel.set_rotation(self.current_rotation)

    def _on_spell_selected(self, spell_name: str):
        """Handle spell selection"""
        self.condition_panel.set_spell(spell_name)

    def _on_condition_created(self, condition: str):
        """Handle condition creation"""
        if self.spell_panel.selected_spell:
            self.rotation_panel.add_spell(
                self.spell_panel.selected_spell,
                condition
            )

    def _on_rotation_spell_moved(self, from_index: int, to_index: int):
        """Handle spell movement in rotation"""
        if self.current_rotation:
            self.current_rotation.move_spell(from_index, to_index)
            self.rotation_panel.refresh()

    def _on_rotation_spell_removed(self, index: int):
        """Handle spell removal from rotation"""
        if self.current_rotation:
            self.current_rotation.remove_spell(index)
            self.rotation_panel.refresh()

    def _new_rotation(self):
        """Create a new rotation"""
        if self.current_rotation and not self._confirm_discard_changes():
            return

        self.current_rotation = None
        self.last_save_path = None
        self.current_class.set('')
        self.current_spec.set('')
        self.spell_panel.clear()
        self.condition_panel.clear()
        self.rotation_panel.clear()
        self.status_label.config(text="New rotation created")

    def _open_rotation(self):
        """Open a rotation file"""
        if self.current_rotation and not self._confirm_discard_changes():
            return

        filename = filedialog.askopenfilename(
            filetypes=[
                ("JSON files", "*.json"),
                ("SOE files", "*.soe"),
                ("All files", "*.*")
            ]
        )

        if filename:
            try:
                # Determine format from extension
                ext = os.path.splitext(filename)[1].lower()
                if ext == '.json':
                    with open(filename, 'r') as f:
                        self.current_rotation = RotationImporter.from_json(f.read())
                elif ext == '.soe':
                    with open(filename, 'r') as f:
                        self.current_rotation = RotationImporter.from_soe(f.read())
                else:
                    raise ValueError("Unsupported file format")

                # Update UI
                self.current_class.set(self.current_rotation.metadata.class_name)
                self._on_class_selected(None)
                self.current_spec.set(self.current_rotation.metadata.spec_name)
                self._on_spec_selected(None)
                
                self.rotation_panel.set_rotation(self.current_rotation)
                self.last_save_path = filename
                
                # Add to recent files
                self._add_recent_file(filename)
                
                self.status_label.config(text=f"Opened {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open rotation: {str(e)}")

    def _save_rotation(self):
        """Save the current rotation"""
        if not self.current_rotation:
            messagebox.showwarning("Warning", "No rotation to save")
            return

        if self.last_save_path:
            self._save_rotation_to_file(self.last_save_path)
        else:
            self._save_rotation_as()

    def _save_rotation_as(self):
        """Save the current rotation with a new filename"""
        if not self.current_rotation:
            messagebox.showwarning("Warning", "No rotation to save")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("SOE files", "*.soe"),
                ("All files", "*.*")
            ]
        )

        if filename:
            self._save_rotation_to_file(filename)

    def _save_rotation_to_file(self, filename: str):
        """Save rotation to a specific file"""
        try:
            # Determine format from extension
            ext = os.path.splitext(filename)[1].lower()
            if ext == '.json':
                content = RotationExporter.to_json(self.current_rotation)
            elif ext == '.soe':
                content = RotationExporter.to_soe(self.current_rotation)
            else:
                raise ValueError("Unsupported file format")

            with open(filename, 'w') as f:
                f.write(content)

            self.last_save_path = filename
            self._add_recent_file(filename)
            self.status_label.config(text=f"Saved {os.path.basename(filename)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save rotation: {str(e)}")

    def _confirm_discard_changes(self) -> bool:
        """Confirm discarding changes to current rotation"""
        if self.current_rotation and self.rotation_panel.has_changes():
            response = messagebox.askyesno(
                "Unsaved Changes",
                "There are unsaved changes. Do you want to continue and discard them?"
            )
            return response
        return True

    def _validate_rotation(self):
        """Validate the current rotation"""
        if not self.current_rotation:
            messagebox.showwarning("Warning", "No rotation to validate")
            return

        result = RotationValidator.validate_rotation(self.current_rotation)
        
        if result.is_valid:
            if result.warnings:
                messagebox.showinfo(
                    "Validation Result",
                    "Rotation is valid with warnings:\n\n" + "\n".join(result.warnings)
                )
            else:
                messagebox.showinfo(
                    "Validation Result",
                    "Rotation is valid!"
                )
        else:
            messagebox.showerror(
                "Validation Result",
                "Rotation has errors:\n\n" + "\n".join(result.errors)
            )

    def _analyze_rotation(self):
        """Analyze the current rotation"""
        if not self.current_rotation:
            messagebox.showwarning("Warning", "No rotation to analyze")
            return

        analysis = RotationValidator.analyze_rotation(self.current_rotation)
        
        # Create analysis window
        analysis_window = tk.Toplevel(self)
        analysis_window.title("Rotation Analysis")
        analysis_window.geometry("600x400")
        
        # Add analysis content
        content = ttk.Frame(analysis_window)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Coverage section
        ttk.Label(content, text="Coverage Analysis", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)
        for aspect, value in analysis.coverage.items():
            ttk.Label(content, text=f"{aspect.title()}: {value*100:.1f}%").pack(anchor=tk.W)
        
        ttk.Separator(content, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Gaps section
        ttk.Label(content, text="Identified Gaps", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)
        for gap in analysis.gaps:
            ttk.Label(content, text=f"• {gap}").pack(anchor=tk.W)
        
        ttk.Separator(content, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Suggestions section
        ttk.Label(content, text="Suggestions", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)
        for suggestion in analysis.suggestions:
            ttk.Label(content, text=f"• {suggestion}").pack(anchor=tk.W)
        
        ttk.Separator(content, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Metrics section
        ttk.Label(content, text="Metrics", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)
        ttk.Label(content, text=f"Complexity Score: {analysis.complexity*100:.1f}%").pack(anchor=tk.W)
        ttk.Label(content, text=f"Efficiency Score: {analysis.efficiency*100:.1f}%").pack(anchor=tk.W)

    def _export_rotation(self, format_type: str):
        """Export the current rotation"""
        if not self.current_rotation:
            messagebox.showwarning("Warning", "No rotation to export")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=f".{format_type}",
            filetypes=[(f"{format_type.upper()} files", f"*.{format_type}")])

        if filename:
            try:
                if format_type == 'soe':
                    content = RotationExporter.to_soe(self.current_rotation)
                elif format_type == 'json':
                    content = RotationExporter.to_json(self.current_rotation)
                elif format_type == 'xml':
                    content = RotationExporter.to_xml(self.current_rotation)
                elif format_type == 'lua':
                    content = RotationExporter.to_lua(self.current_rotation)
                else:
                    raise ValueError(f"Unsupported export format: {format_type}")

                with open(filename, 'w') as f:
                    f.write(content)

                self.status_label.config(text=f"Exported as {format_type.upper()}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")

    def _show_preferences(self):
        """Show preferences dialog"""
        # Create preferences window
        pref_window = tk.Toplevel(self)
        pref_window.title("Preferences")
        pref_window.geometry("400x300")
        pref_window.transient(self)
        pref_window.grab_set()

        # Add preferences content
        content = ttk.Frame(pref_window)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add preference options here
        # This is a placeholder for future implementation
        ttk.Label(content, text="Preferences will be implemented in a future update").pack()

    def _show_documentation(self):
        """Show documentation window"""
        doc_window = tk.Toplevel(self)
        doc_window.title("Documentation")
        doc_window.geometry("800x600")
        
        # Add documentation content
        content = ttk.Frame(doc_window)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create text widget with scrollbar
        text_widget = tk.Text(content, wrap=tk.WORD, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(content, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add documentation text
        doc_text = """
SOE Rotation Builder Documentation

1. Getting Started
-----------------
The SOE Rotation Builder allows you to create and manage spell rotations for World of Warcraft
using the SOE Engine format. Here's how to get started:

1.1. Creating a New Rotation
- Select your class and specialization from the dropdown menus
- Add spells from the spell list on the left
- Configure conditions for each spell
- Arrange spells in priority order

1.2. Managing Rotations
- Use File > New to create a new rotation
- Use File > Save to save your work
- Use File > Open to load existing rotations

2. Building Rotations
--------------------
2.1. Adding Spells
- Select a spell from the spell list
- Configure conditions in the condition builder
- Click "Add to Rotation" to add the spell

2.2. Conditions
- Use the condition builder to create complex conditions
- Combine multiple conditions using AND/OR operators
- Test conditions before adding them

3. Validation and Analysis
-------------------------
3.1. Validation
- Use Edit > Validate Rotation to check for errors
- Fix any reported issues before using the rotation

3.2. Analysis
- Use Edit > Analyze Rotation for detailed insights
- Review suggestions for improvement
- Check coverage of different situations

4. Exporting
-----------
4.1. Export Formats
- SOE Engine format (.soe)
- JSON format (.json)
- XML format (.xml)
- Lua format (.lua)

4.2. Using Exported Rotations
- Copy SOE format directly into WoW
- Use JSON/XML for backup and sharing
- Use Lua for advanced customization

5. Tips and Best Practices
-------------------------
5.1. Rotation Structure
- Start with core abilities
- Add situational abilities
- Include defensive cooldowns
- Configure movement abilities

5.2. Condition Building
- Use simple conditions when possible
- Test complex conditions thoroughly
- Consider all combat situations
- Include proper fallback options

6. Troubleshooting
-----------------
6.1. Common Issues
- Verify spell names match exactly
- Check condition syntax
- Validate rotation before testing
- Test with different scenarios

6.2. Getting Help
- Check error messages
- Review documentation
- Use the analysis tool
- Report bugs if found

7. Keyboard Shortcuts
--------------------
Ctrl+N: New Rotation
Ctrl+O: Open Rotation
Ctrl+S: Save Rotation
Ctrl+Shift+S: Save As
Ctrl+V: Validate Rotation
Ctrl+A: Analyze Rotation
F1: Show Documentation
"""
        text_widget.insert('1.0', doc_text)
        text_widget.configure(state='disabled')

    def _show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About SOE Rotation Builder",
            "SOE Rotation Builder\n"
            "Version 1.0\n\n"
            "A tool for creating and managing World of Warcraft spell rotations "
            "using the SOE Engine format.\n\n"
            "Created using Python and Tkinter."
        )

    def _load_recent_files(self) -> List[str]:
        """Load recent files list from settings"""
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                return settings.get('recent_files', [])
        except:
            return []

    def _save_recent_files(self):
        """Save recent files list to settings"""
        try:
            settings = {'recent_files': self.recent_files}
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
        except:
            pass

    def _add_recent_file(self, filename: str):
        """Add a file to recent files list"""
        if filename in self.recent_files:
            self.recent_files.remove(filename)
        self.recent_files.insert(0, filename)
        self.recent_files = self.recent_files[:10]  # Keep only 10 most recent
        self._save_recent_files()
        self._update_recent_files_menu()

    def _update_recent_files_menu(self):
        """Update the recent files menu"""
        # Clear existing menu items
        self.recent_menu.delete(0, tk.END)
        
        if self.recent_files:
            for filename in self.recent_files:
                self.recent_menu.add_command(
                    label=os.path.basename(filename),
                    command=lambda f=filename: self._open_recent_file(f)
                )
        else:
            self.recent_menu.add_command(
                label="No recent files",
                state=tk.DISABLED
            )

    def _open_recent_file(self, filename: str):
        """Open a file from the recent files list"""
        if os.path.exists(filename):
            if self.current_rotation and not self._confirm_discard_changes():
                return
            self._open_rotation_file(filename)
        else:
            messagebox.showerror(
                "Error",
                f"File not found: {filename}"
            )
            self.recent_files.remove(filename)
            self._save_recent_files()
            self._update_recent_files_menu()

    def _on_close(self):
        """Handle window close event"""
        if self.current_rotation and not self._confirm_discard_changes():
            return
        self.quit()

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()