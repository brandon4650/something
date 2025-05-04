import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, Callable, Dict, Any
from core.rotation import Rotation, SpellEntry
from .widgets import ModernFrame, ModernLabel, ModernButton, ModernCombobox

class RotationPanel(ModernFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.rotation: Optional[Rotation] = None
        self.on_spell_moved: Optional[Callable[[int, int], None]] = None
        self.on_spell_removed: Optional[Callable[[int], None]] = None
        self.has_unsaved_changes = False
        
        self._create_widgets()
        self._bind_events()
        self._create_context_menu()

    def _create_widgets(self):
        """Create and setup widgets"""
        # Title frame
        title_frame = ModernFrame(self)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ModernLabel(
            title_frame,
            text="Rotation Builder",
            font=("Segoe UI", 12, "bold")
        ).pack(side=tk.LEFT)

        # Rotation metadata frame
        meta_frame = ModernFrame(self)
        meta_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # Name field
        name_frame = ModernFrame(meta_frame)
        name_frame.pack(fill=tk.X, pady=(0, 2))
        
        ModernLabel(name_frame, text="Name:").pack(side=tk.LEFT)
        self.name_entry = ttk.Entry(name_frame)
        self.name_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # Author field
        author_frame = ModernFrame(meta_frame)
        author_frame.pack(fill=tk.X, pady=(0, 2))
        
        ModernLabel(author_frame, text="Author:").pack(side=tk.LEFT)
        self.author_entry = ttk.Entry(author_frame)
        self.author_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # Description field
        desc_frame = ModernFrame(meta_frame)
        desc_frame.pack(fill=tk.X, pady=(0, 2))
        
        ModernLabel(desc_frame, text="Description:").pack(anchor=tk.W)
        self.desc_text = tk.Text(desc_frame, height=2, width=30)
        self.desc_text.pack(fill=tk.X, expand=True)

        # Rotation list frame
        list_frame = ModernFrame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # Create Treeview with scrollbar
        self.rotation_tree = ttk.Treeview(
            list_frame,
            columns=("priority", "spell", "condition", "enabled"),
            show="headings",
            selectmode="browse"
        )
        
        scrollbar = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=self.rotation_tree.yview
        )
        
        self.rotation_tree.configure(yscrollcommand=scrollbar.set)

        # Setup columns
        self.rotation_tree.heading("priority", text="Priority")
        self.rotation_tree.heading("spell", text="Spell")
        self.rotation_tree.heading("condition", text="Condition")
        self.rotation_tree.heading("enabled", text="Enabled")
        
        self.rotation_tree.column("priority", width=60, anchor=tk.CENTER)
        self.rotation_tree.column("spell", width=150)
        self.rotation_tree.column("condition", width=200)
        self.rotation_tree.column("enabled", width=60, anchor=tk.CENTER)

        # Pack Treeview and scrollbar
        self.rotation_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Button frame
        button_frame = ModernFrame(self)
        button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        # Move buttons
        move_frame = ModernFrame(button_frame)
        move_frame.pack(side=tk.LEFT)
        
        self.move_up_btn = ModernButton(
            move_frame,
            text="↑",
            width=3,
            command=self._move_up
        )
        self.move_up_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        self.move_down_btn = ModernButton(
            move_frame,
            text="↓",
            width=3,
            command=self._move_down
        )
        self.move_down_btn.pack(side=tk.LEFT)

        # Action buttons
        action_frame = ModernFrame(button_frame)
        action_frame.pack(side=tk.RIGHT)
        
        self.edit_btn = ModernButton(
            action_frame,
            text="Edit",
            command=self._edit_spell
        )
        self.edit_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        self.remove_btn = ModernButton(
            action_frame,
            text="Remove",
            command=self._remove_spell
        )
        self.remove_btn.pack(side=tk.LEFT)

        # Notes frame
        notes_frame = ModernFrame(self)
        notes_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ModernLabel(notes_frame, text="Notes:").pack(anchor=tk.W)
        self.notes_text = tk.Text(notes_frame, height=3, width=30)
        self.notes_text.pack(fill=tk.X)

    def _create_context_menu(self):
        """Create right-click context menu"""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(
            label="Edit",
            command=self._edit_spell
        )
        self.context_menu.add_command(
            label="Toggle Enabled",
            command=self._toggle_spell_enabled
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Move Up",
            command=self._move_up
        )
        self.context_menu.add_command(
            label="Move Down",
            command=self._move_down
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Remove",
            command=self._remove_spell
        )

    def _bind_events(self):
        """Bind event handlers"""
        self.rotation_tree.bind("<<TreeviewSelect>>", self._on_spell_selected)
        self.rotation_tree.bind("<Double-1>", self._on_double_click)
        self.rotation_tree.bind("<Button-3>", self._show_context_menu)
        self.rotation_tree.bind("<Delete>", lambda e: self._remove_spell())
        self.rotation_tree.bind("<space>", lambda e: self._toggle_spell_enabled())
        
        # Bind metadata change events
        self.name_entry.bind("<KeyRelease>", self._on_metadata_changed)
        self.author_entry.bind("<KeyRelease>", self._on_metadata_changed)
        self.desc_text.bind("<KeyRelease>", self._on_metadata_changed)

    def set_rotation(self, rotation: Rotation):
        """Set the current rotation"""
        self.rotation = rotation
        self._update_metadata_display()
        self.refresh()
        self.has_unsaved_changes = False

    def add_spell(self, spell_name: str, condition: str = "true"):
        """Add a spell to the rotation"""
        if not self.rotation:
            return

        try:
            self.rotation.add_spell(spell_name, condition)
            self.refresh()
            self.has_unsaved_changes = True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add spell: {str(e)}")

    def refresh(self):
        """Refresh the rotation display"""
        # Clear existing items
        for item in self.rotation_tree.get_children():
            self.rotation_tree.delete(item)

        if not self.rotation:
            return

        # Add spells
        for spell in self.rotation.spells:
            self.rotation_tree.insert(
                "",
                tk.END,
                values=(
                    spell.priority,
                    spell.name,
                    spell.condition,
                    "Yes" if spell.enabled else "No"
                )
            )

    def _update_metadata_display(self):
        """Update metadata display fields"""
        if not self.rotation:
            self.name_entry.delete(0, tk.END)
            self.author_entry.delete(0, tk.END)
            self.desc_text.delete('1.0', tk.END)
            return

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, self.rotation.metadata.name)
        
        self.author_entry.delete(0, tk.END)
        self.author_entry.insert(0, self.rotation.metadata.author)
        
        self.desc_text.delete('1.0', tk.END)
        self.desc_text.insert('1.0', self.rotation.metadata.description)

    def _on_metadata_changed(self, event):
        """Handle metadata changes"""
        if not self.rotation:
            return

        self.rotation.metadata.name = self.name_entry.get()
        self.rotation.metadata.author = self.author_entry.get()
        self.rotation.metadata.description = self.desc_text.get('1.0', 'end-1c')
        self.has_unsaved_changes = True

    def _on_spell_selected(self, event):
        """Handle spell selection"""
        selection = self.rotation_tree.selection()
        if selection:
            item = selection[0]
            spell_data = self.rotation_tree.item(item)["values"]
            
            # Update notes display
            spell = self._get_spell_by_priority(spell_data[0])
            if spell:
                self.notes_text.delete('1.0', tk.END)
                self.notes_text.insert('1.0', spell.notes)
        else:
            self.notes_text.delete('1.0', tk.END)

    def _get_spell_by_priority(self, priority: int) -> Optional[SpellEntry]:
        """Get spell entry by priority"""
        if not self.rotation:
            return None
            
        for spell in self.rotation.spells:
            if spell.priority == priority:
                return spell
        return None

    def _on_double_click(self, event):
        """Handle double click on spell"""
        self._edit_spell()

    def _show_context_menu(self, event):
        """Show right-click context menu"""
        if self.rotation_tree.selection():
            self.context_menu.post(event.x_root, event.y_root)

    def _edit_spell(self):
        """Edit selected spell"""
        selection = self.rotation_tree.selection()
        if not selection:
            return

        item = selection[0]
        spell_data = self.rotation_tree.item(item)["values"]
        spell = self._get_spell_by_priority(spell_data[0])
        if not spell:
            return

        # Create edit window
        edit_window = tk.Toplevel(self)
        edit_window.title(f"Edit Spell: {spell.name}")
        edit_window.geometry("400x300")
        edit_window.transient(self)
        edit_window.grab_set()

        # Create edit form
        content = ModernFrame(edit_window)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Condition
        ModernLabel(content, text="Condition:").pack(anchor=tk.W)
        condition_text = tk.Text(content, height=3)
        condition_text.pack(fill=tk.X)
        condition_text.insert('1.0', spell.condition)

        # Enabled checkbox
        enabled_var = tk.BooleanVar(value=spell.enabled)
        ttk.Checkbutton(
            content,
            text="Enabled",
            variable=enabled_var
        ).pack(anchor=tk.W, pady=5)

        # Notes
        ModernLabel(content, text="Notes:").pack(anchor=tk.W)
        notes_text = tk.Text(content, height=5)
        notes_text.pack(fill=tk.X)
        notes_text.insert('1.0', spell.notes)

        # Save button
        def save_changes():
            try:
                # Update spell
                spell.condition = condition_text.get('1.0', 'end-1c')
                spell.enabled = enabled_var.get()
                spell.notes = notes_text.get('1.0', 'end-1c')
                
                self.refresh()
                self.has_unsaved_changes = True
                edit_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update spell: {str(e)}")

        ModernButton(
            content,
            text="Save Changes",
            command=save_changes
        ).pack(pady=10)

    def _toggle_spell_enabled(self):
        """Toggle selected spell enabled state"""
        selection = self.rotation_tree.selection()
        if not selection:
            return

        item = selection[0]
        spell_data = self.rotation_tree.item(item)["values"]
        spell = self._get_spell_by_priority(spell_data[0])
        if spell:
            spell.enabled = not spell.enabled
            self.refresh()
            self.has_unsaved_changes = True

    def _move_up(self):
        """Move selected spell up"""
        selection = self.rotation_tree.selection()
        if not selection:
            return

        item = selection[0]
        spell_data = self.rotation_tree.item(item)["values"]
        priority = spell_data[0]

        if priority > 1:
            if self.on_spell_moved:
                self.on_spell_moved(priority, priority - 1)
            self.has_unsaved_changes = True

    def _move_down(self):
        """Move selected spell down"""
        selection = self.rotation_tree.selection()
        if not selection:
            return

        item = selection[0]
        spell_data = self.rotation_tree.item(item)["values"]
        priority = spell_data[0]

        if self.rotation and priority < len(self.rotation.spells):
            if self.on_spell_moved:
                self.on_spell_moved(priority, priority + 1)
            self.has_unsaved_changes = True

    def _remove_spell(self):
        """Remove selected spell"""
        selection = self.rotation_tree.selection()
        if not selection:
            return

        if messagebox.askyesno("Confirm", "Remove selected spell from rotation?"):
            item = selection[0]
            spell_data = self.rotation_tree.item(item)["values"]
            priority = spell_data[0]
            
            if self.on_spell_removed:
                self.on_spell_removed(priority)
            self.has_unsaved_changes = True

    def clear(self):
        """Clear the panel"""
        self.rotation = None
        self._update_metadata_display()
        self.refresh()
        self.has_unsaved_changes = False

    def has_changes(self) -> bool:
        """Check if there are unsaved changes"""
        return self.has_unsaved_changes