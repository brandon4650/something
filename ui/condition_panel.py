import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Callable, Dict, Any, Tuple
from conditions import ConditionBuilder, ConditionValidator
from .widgets import ModernFrame, ModernLabel, ModernButton, ModernCombobox

class ConditionPanel(ModernFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.condition_builder = ConditionBuilder()
        self.current_spell: Optional[str] = None
        self.on_condition_created: Optional[Callable[[str], None]] = None
        
        self._setup_variables()
        self._create_widgets()
        self._create_condition_templates()
        self._bind_events()

    def _setup_variables(self):
        """Setup tkinter variables"""
        self.category_var = tk.StringVar()
        self.subcategory_var = tk.StringVar()
        self.operator_var = tk.StringVar(value="==")
        self.value_var = tk.StringVar()
        self.logical_op_var = tk.StringVar(value="AND")
        self.template_var = tk.StringVar()
        
        # Track condition parts
        self.condition_parts: List[str] = []

    def _create_widgets(self):
        """Create and setup widgets"""
        # Title frame
        title_frame = ModernFrame(self)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        ModernLabel(title_frame, text="Condition Builder", 
                   font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)

        # Current spell frame
        spell_frame = ModernFrame(self)
        spell_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.spell_label = ModernLabel(spell_frame, text="No spell selected")
        self.spell_label.pack(side=tk.LEFT)

        # Template frame
        template_frame = ModernFrame(self)
        template_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ModernLabel(template_frame, text="Templates:").pack(side=tk.LEFT)
        self.template_combo = ModernCombobox(
            template_frame,
            textvariable=self.template_var,
            state="readonly",
            width=30
        )
        self.template_combo.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        ModernButton(
            template_frame,
            text="Use",
            command=self._use_template
        ).pack(side=tk.LEFT, padx=(5, 0))

        # Builder frame
        builder_frame = ModernFrame(self)
        builder_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # Category selection
        category_frame = ModernFrame(builder_frame)
        category_frame.pack(fill=tk.X, pady=(0, 5))
        
        ModernLabel(category_frame, text="Category:").pack(side=tk.LEFT)
        self.category_combo = ModernCombobox(
            category_frame,
            textvariable=self.category_var,
            state="readonly",
            width=20
        )
        self.category_combo.pack(side=tk.LEFT, padx=(5, 0))

        # Subcategory selection
        subcategory_frame = ModernFrame(builder_frame)
        subcategory_frame.pack(fill=tk.X, pady=(0, 5))
        
        ModernLabel(subcategory_frame, text="Condition:").pack(side=tk.LEFT)
        self.subcategory_combo = ModernCombobox(
            subcategory_frame,
            textvariable=self.subcategory_var,
            state="readonly",
            width=25
        )
        self.subcategory_combo.pack(side=tk.LEFT, padx=(5, 0))

        # Operator and value frame
        operator_frame = ModernFrame(builder_frame)
        operator_frame.pack(fill=tk.X, pady=(0, 5))
        
        ModernLabel(operator_frame, text="Operator:").pack(side=tk.LEFT)
        self.operator_combo = ModernCombobox(
            operator_frame,
            textvariable=self.operator_var,
            values=["==", "!=", ">", "<", ">=", "<="],
            state="readonly",
            width=5
        )
        self.operator_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        ModernLabel(operator_frame, text="Value:").pack(side=tk.LEFT, padx=(10, 0))
        self.value_entry = ttk.Entry(
            operator_frame,
            textvariable=self.value_var,
            width=10
        )
        self.value_entry.pack(side=tk.LEFT, padx=(5, 0))

        # Logical operator frame
        logical_frame = ModernFrame(builder_frame)
        logical_frame.pack(fill=tk.X, pady=(0, 5))
        
        ModernLabel(logical_frame, text="Connect with:").pack(side=tk.LEFT)
        self.logical_combo = ModernCombobox(
            logical_frame,
            textvariable=self.logical_op_var,
            values=["AND", "OR"],
            state="readonly",
            width=5
        )
        self.logical_combo.pack(side=tk.LEFT, padx=(5, 0))

        # Buttons frame
        button_frame = ModernFrame(builder_frame)
        button_frame.pack(fill=tk.X, pady=(0, 5))
        
        ModernButton(
            button_frame,
            text="Add Part",
            command=self._add_condition_part
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ModernButton(
            button_frame,
            text="Clear",
            command=self._clear_condition
        ).pack(side=tk.LEFT)

        # Current condition frame
        condition_frame = ModernFrame(self)
        condition_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        ModernLabel(condition_frame, text="Current Condition:").pack(anchor=tk.W)
        
        # Condition display
        self.condition_text = tk.Text(
            condition_frame,
            height=4,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.condition_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Make text widget read-only
        self.condition_text.bind("<Key>", lambda e: "break")

        # Final buttons frame
        final_button_frame = ModernFrame(self)
        final_button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.create_button = ModernButton(
            final_button_frame,
            text="Create Condition",
            command=self._create_condition,
            state=tk.DISABLED
        )
        self.create_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.validate_button = ModernButton(
            final_button_frame,
            text="Validate",
            command=self._validate_condition
        )
        self.validate_button.pack(side=tk.LEFT)

    def _create_condition_templates(self):
        """Create predefined condition templates"""
        self.templates = {
            "Always Cast": "true",
            "Low Health (<30%)": "player.health < 30",
            "High Health (>80%)": "player.health > 80",
            "Moving": "player.moving",
            "Standing Still": "!player.moving",
            "Has Buff": "player.buff(BuffName)",
            "No Buff": "!player.buff(BuffName)",
            "Target Has Debuff": "target.debuff(DebuffName)",
            "Target No Debuff": "!target.debuff(DebuffName)",
            "Target Below 20%": "target.health < 20",
            "Multiple Targets (3+)": "area.enemies >= 3",
            "Low Mana (<40%)": "player.mana < 40",
            "High Mana (>60%)": "player.mana > 60",
            "Target is Boss": "target.boss",
            "Player in Combat": "player.incombat",
            "Cooldowns Enabled": "toggle.cooldowns",
            "AoE Enabled": "toggle.aoe",
            "Interrupts Enabled": "toggle.interrupts",
            "With Shift Key": "modifier.shift",
            "With Control Key": "modifier.control",
            "With Alt Key": "modifier.alt"
        }
        
        self.template_combo['values'] = list(self.templates.keys())

    def _bind_events(self):
        """Bind event handlers"""
        self.category_combo.bind('<<ComboboxSelected>>', self._on_category_selected)
        self.subcategory_combo.bind('<<ComboboxSelected>>', self._on_subcategory_selected)
        self.template_combo.bind('<<ComboboxSelected>>', self._on_template_selected)

    def set_class(self, class_name: str):
        """Set the current class and update available conditions"""
        self.condition_builder.set_class(class_name)
        self._update_categories()

    def set_spell(self, spell_name: str):
        """Set the current spell"""
        self.current_spell = spell_name
        self.spell_label.configure(text=f"Spell: {spell_name}")
        self.create_button.configure(state=tk.NORMAL)

    def _update_categories(self):
        """Update available condition categories"""
        categories = self.condition_builder.get_available_categories()
        self.category_combo['values'] = categories
        if categories:
            self.category_combo.set(categories[0])
            self._on_category_selected(None)

    def _on_category_selected(self, event):
        """Handle category selection"""
        category = self.category_var.get()
        conditions = self.condition_builder.get_conditions_for_category(category)
        self.subcategory_combo['values'] = list(conditions.keys())
        if conditions:
            self.subcategory_combo.set(next(iter(conditions.keys())))

    def _on_subcategory_selected(self, event):
        """Handle subcategory selection"""
        # Update UI based on selected condition
        subcategory = self.subcategory_var.get()
        if "buff" in subcategory or "debuff" in subcategory:
            self.value_entry.configure(state=tk.NORMAL)
        else:
            self.value_entry.configure(state=tk.DISABLED)

    def _on_template_selected(self, event):
        """Handle template selection"""
        template_name = self.template_var.get()
        if template_name in self.templates:
            self.condition_text.delete('1.0', tk.END)
            self.condition_text.insert('1.0', self.templates[template_name])
            self.condition_parts = [self.templates[template_name]]

    def _use_template(self):
        """Use selected template"""
        template_name = self.template_var.get()
        if template_name in self.templates:
            self._clear_condition()
            self.condition_parts = [self.templates[template_name]]
            self._update_condition_display()

    def _add_condition_part(self):
        """Add a part to the condition"""
        category = self.category_var.get()
        subcategory = self.subcategory_var.get()
        operator = self.operator_var.get()
        value = self.value_var.get()

        # Build condition part
        condition_part = f"{category}.{subcategory}"
        if value:
            condition_part += f" {operator} {value}"

        # Add to condition parts
        if self.condition_parts:
            logical_op = "&&" if self.logical_op_var.get() == "AND" else "||"
            self.condition_parts.append(logical_op)
        self.condition_parts.append(condition_part)

        self._update_condition_display()
        self.value_var.set("")  # Clear value entry

    def _update_condition_display(self):
        """Update the condition display"""
        self.condition_text.delete('1.0', tk.END)
        condition_str = " ".join(self.condition_parts)
        self.condition_text.insert('1.0', condition_str)

    def _clear_condition(self):
        """Clear the current condition"""
        self.condition_parts = []
        self.condition_text.delete('1.0', tk.END)
        self.value_var.set("")

    def _validate_condition(self):
        """Validate the current condition"""
        condition = self.condition_text.get('1.0', 'end-1c')
        is_valid, error = ConditionValidator.validate_condition(condition)
        
        if is_valid:
            messagebox.showinfo("Validation", "Condition is valid!")
        else:
            messagebox.showerror("Validation Error", f"Invalid condition: {error}")

    def _create_condition(self):
        """Create and emit the condition"""
        if not self.current_spell:
            messagebox.showwarning("Warning", "No spell selected!")
            return

        condition = self.condition_text.get('1.0', 'end-1c')
        if not condition:
            condition = "true"

        # Validate condition
        is_valid, error = ConditionValidator.validate_condition(condition)
        if not is_valid:
            messagebox.showerror("Error", f"Invalid condition: {error}")
            return

        # Emit condition
        if self.on_condition_created:
            self.on_condition_created(condition)

        # Clear after creation
        self._clear_condition()

    def clear(self):
        """Clear the panel"""
        self.current_spell = None
        self.spell_label.configure(text="No spell selected")
        self._clear_condition()
        self.create_button.configure(state=tk.DISABLED)