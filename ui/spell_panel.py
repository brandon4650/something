import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Callable, Dict, Any
import spell_data
from .widgets import ModernFrame, ModernLabel, ModernButton, SearchEntry

class SpellPanel(ModernFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_spell: Optional[str] = None
        self.on_spell_selected: Optional[Callable[[str], None]] = None
        self.spells: List[str] = []
        self.filtered_spells: List[str] = []
        
        self._create_widgets()
        self._create_context_menu()
        self._bind_events()

    def _create_widgets(self):
        """Create and setup widgets"""
        # Panel title
        title_frame = ModernFrame(self)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        ModernLabel(title_frame, text="Available Spells", 
                   font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)

        # Search frame
        search_frame = ModernFrame(self)
        search_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        
        self.search_entry = SearchEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder="Search spells..."
        )
        self.search_entry.pack(fill=tk.X)

        # Category filters
        filter_frame = ModernFrame(self)
        filter_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.filter_var = tk.StringVar(value="All")
        categories = ["All", "Damage", "Healing", "Cooldown", "Utility"]
        
        for category in categories:
            ttk.Radiobutton(
                filter_frame,
                text=category,
                value=category,
                variable=self.filter_var,
                command=self._apply_filters
            ).pack(side=tk.LEFT, padx=2)

        # Spell list
        list_frame = ModernFrame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # Create Treeview with scrollbar
        self.spell_tree = ttk.Treeview(
            list_frame,
            columns=("name", "type"),
            show="headings",
            selectmode="browse"
        )
        
        scrollbar = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=self.spell_tree.yview
        )
        
        self.spell_tree.configure(yscrollcommand=scrollbar.set)

        # Setup columns
        self.spell_tree.heading("name", text="Spell Name")
        self.spell_tree.heading("type", text="Type")
        
        self.spell_tree.column("name", width=150)
        self.spell_tree.column("type", width=80)

        # Pack Treeview and scrollbar
        self.spell_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Information frame
        self.info_frame = ModernFrame(self)
        self.info_frame.pack(fill=tk.X, padx=5, pady=5)

        self.info_label = ModernLabel(
            self.info_frame,
            text="Select a spell to view details",
            wraplength=250
        )
        self.info_label.pack(fill=tk.X)

        # Action buttons
        button_frame = ModernFrame(self)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        self.add_button = ModernButton(
            button_frame,
            text="Add to Rotation",
            command=self._add_selected_spell,
            state=tk.DISABLED
        )
        self.add_button.pack(side=tk.LEFT, padx=2)

        self.clear_button = ModernButton(
            button_frame,
            text="Clear Selection",
            command=self._clear_selection
        )
        self.clear_button.pack(side=tk.LEFT, padx=2)

    def _create_context_menu(self):
        """Create right-click context menu"""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(
            label="Add to Rotation",
            command=self._add_selected_spell
        )
        self.context_menu.add_command(
            label="View Details",
            command=self._show_spell_details
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Copy Name",
            command=self._copy_spell_name
        )

    def _bind_events(self):
        """Bind event handlers"""
        self.spell_tree.bind("<<TreeviewSelect>>", self._on_spell_selected)
        self.spell_tree.bind("<Double-1>", self._on_double_click)
        self.spell_tree.bind("<Button-3>", self._show_context_menu)
        self.spell_tree.bind("<Return>", lambda e: self._add_selected_spell())

    def update_spells(self, spells: List[str]):
        """Update the spell list"""
        self.spells = spells
        self.filtered_spells = spells.copy()
        self._update_spell_list()
        self._clear_selection()

    def _update_spell_list(self):
        """Update the Treeview with current spells"""
        # Clear existing items
        for item in self.spell_tree.get_children():
            self.spell_tree.delete(item)

        # Add filtered spells
        for spell in self.filtered_spells:
            spell_type = self._get_spell_type(spell)
            self.spell_tree.insert(
                "",
                tk.END,
                values=(spell, spell_type)
            )

    def _get_spell_type(self, spell_name: str) -> str:
        """Determine spell type based on name/mechanics"""
        # This is a simplified version - you would want to expand this
        # based on actual spell data
        spell_name_lower = spell_name.lower()
        
        if any(word in spell_name_lower for word in 
               ["bolt", "blast", "strike", "shot", "smite"]):
            return "Damage"
        elif any(word in spell_name_lower for word in 
                ["heal", "renew", "mend", "rejuv"]):
            return "Healing"
        elif any(word in spell_name_lower for word in 
                ["shield", "protect", "guard", "barrier"]):
            return "Defense"
        elif any(word in spell_name_lower for word in 
                ["power", "fury", "rage", "wrath"]):
            return "Cooldown"
        else:
            return "Utility"

    def _on_spell_selected(self, event):
        """Handle spell selection"""
        selection = self.spell_tree.selection()
        if selection:
            item = selection[0]
            spell_name = self.spell_tree.item(item)["values"][0]
            self.selected_spell = spell_name
            self.add_button.configure(state=tk.NORMAL)
            
            # Update info label with spell details
            spell_info = self._get_spell_info(spell_name)
            self.info_label.configure(text=spell_info)
            
            # Notify listeners
            if self.on_spell_selected:
                self.on_spell_selected(spell_name)
        else:
            self.selected_spell = None
            self.add_button.configure(state=tk.DISABLED)
            self.info_label.configure(text="Select a spell to view details")

    def _get_spell_info(self, spell_name: str) -> str:
        """Get detailed spell information"""
        # This is a placeholder - you would want to add actual spell data
        spell_type = self._get_spell_type(spell_name)
        return f"Spell: {spell_name}\nType: {spell_type}\n\nClick 'Add to Rotation' to use this spell."

    def _on_double_click(self, event):
        """Handle double click on spell"""
        self._add_selected_spell()

    def _show_context_menu(self, event):
        """Show right-click context menu"""
        if self.selected_spell:
            self.context_menu.post(event.x_root, event.y_root)

    def _add_selected_spell(self):
        """Add selected spell to rotation"""
        if self.selected_spell and self.on_spell_selected:
            self.on_spell_selected(self.selected_spell)

    def _copy_spell_name(self):
        """Copy selected spell name to clipboard"""
        if self.selected_spell:
            self.clipboard_clear()
            self.clipboard_append(self.selected_spell)

    def _show_spell_details(self):
        """Show detailed spell information window"""
        if not self.selected_spell:
            return

        details_window = tk.Toplevel(self)
        details_window.title(f"Spell Details: {self.selected_spell}")
        details_window.geometry("400x300")
        details_window.transient(self)
        details_window.grab_set()

        content = ModernFrame(details_window)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Spell name
        ModernLabel(
            content,
            text=self.selected_spell,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor=tk.W)

        # Spell type
        spell_type = self._get_spell_type(self.selected_spell)
        ModernLabel(
            content,
            text=f"Type: {spell_type}",
            font=("Segoe UI", 10)
        ).pack(anchor=tk.W, pady=(5, 10))

        # Spell description
        description_frame = ModernFrame(content)
        description_frame.pack(fill=tk.BOTH, expand=True)

        description_text = tk.Text(
            description_frame,
            wrap=tk.WORD,
            height=10,
            font=("Segoe UI", 10)
        )
        description_text.pack(fill=tk.BOTH, expand=True)
        description_text.insert("1.0", self._get_spell_description(self.selected_spell))
        description_text.configure(state="disabled")

        # Close button
        ModernButton(
            content,
            text="Close",
            command=details_window.destroy
        ).pack(pady=(10, 0))

    def _get_spell_description(self, spell_name: str) -> str:
        """Get detailed spell description"""
        # This is a placeholder - you would want to add actual spell descriptions
        return (
            f"Description for {spell_name}\n\n"
            "This is where the detailed spell description would go, including:\n"
            "- Spell effects\n"
            "- Damage/healing values\n"
            "- Cooldown\n"
            "- Resource cost\n"
            "- Additional effects"
        )

    def _clear_selection(self):
        """Clear current selection"""
        self.spell_tree.selection_remove(*self.spell_tree.selection())
        self.selected_spell = None
        self.add_button.configure(state=tk.DISABLED)
        self.info_label.configure(text="Select a spell to view details")

    def _on_search(self, *args):
        """Handle search input changes"""
        search_text = self.search_var.get().lower()
        self.filtered_spells = [
            spell for spell in self.spells
            if search_text in spell.lower()
        ]
        self._apply_filters()

    def _apply_filters(self):
        """Apply category filters"""
        category = self.filter_var.get()
        if category == "All":
            self._update_spell_list()
            return

        filtered = []
        for spell in self.filtered_spells:
            spell_type = self._get_spell_type(spell)
            if spell_type == category:
                filtered.append(spell)

        self.filtered_spells = filtered
        self._update_spell_list()

    def clear(self):
        """Clear the panel"""
        self.spells = []
        self.filtered_spells = []
        self._update_spell_list()
        self._clear_selection()
        self.search_var.set("")

class SearchEntry(ttk.Entry):
    """Custom Entry widget with placeholder text"""
    def __init__(self, parent, placeholder="", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.placeholder = placeholder
        self.placeholder_color = 'grey'
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

        self._add_placeholder()

    def _clear_placeholder(self, e=None):
        """Clear placeholder text"""
        if self['fg'] == self.placeholder_color:
            self.delete(0, tk.END)
            self['fg'] = self.default_fg_color

    def _add_placeholder(self, e=None):
        """Add placeholder text if empty"""
        if not self.get():
            self.insert(0, self.placeholder)
            self['fg'] = self.placeholder_color