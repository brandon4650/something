from typing import Dict, List, Optional, Tuple, Any
import re

class ConditionValidator:
    """Validates and processes rotation conditions"""
    
    BASIC_CONDITIONS = {
        "player": {
            "health": "Player's health percentage",
            "health.actual": "Player's actual health value",
            "health.max": "Player's maximum health",
            "mana": "Player's mana percentage",
            "rage": "Player's rage amount",
            "energy": "Player's energy amount",
            "focus": "Player's focus amount",
            "runicpower": "Player's runic power amount",
            "holypower": "Player's holy power amount",
            "chi": "Player's chi amount",
            "soulshards": "Player's soul shards amount",
            "eclipse": "Player's eclipse value",
            "combopoints": "Player's combo points",
            "buff": "Check if player has a specific buff",
            "buff.any": "Check if player has any of several buffs",
            "buff.count": "Stack count of a buff",
            "buff.duration": "Remaining duration of a buff",
            "debuff": "Check if player has a specific debuff",
            "debuff.any": "Check if player has any of several debuffs",
            "debuff.count": "Stack count of a debuff",
            "debuff.duration": "Remaining duration of a debuff",
            "moving": "Check if player is moving",
            "movingfor": "Time player has been moving",
            "casting": "Check if player is casting",
            "casting.percent": "Percentage of cast completed",
            "casting.delta": "Time left on current cast",
            "channeling": "Check if player is channeling",
            "stance": "Current stance (Warrior)",
            "form": "Current form (Druid)",
            "seal": "Current seal (Paladin)",
            "lastcast": "Last spell cast",
            "level": "Player's level",
            "spec": "Current specialization",
            "talent": "Check if player has a specific talent",
            "glyph": "Check if player has a specific glyph"
        },
        "target": {
            "health": "Target's health percentage",
            "health.actual": "Target's actual health value",
            "health.max": "Target's maximum health",
            "exists": "Check if target exists",
            "enemy": "Check if target is hostile",
            "friend": "Check if target is friendly",
            "name": "Target's name",
            "distance": "Distance to target in yards",
            "range": "Check if target is in range",
            "debuff": "Check if target has a specific debuff",
            "debuff.any": "Check if target has any of several debuffs",
            "debuff.count": "Stack count of a debuff",
            "debuff.duration": "Remaining duration of a debuff",
            "casting": "Check if target is casting",
            "casting.percent": "Percentage of cast completed",
            "casting.delta": "Time left on current cast",
            "interruptsat": "Percentage when cast can be interrupted",
            "moving": "Check if target is moving",
            "level": "Target's level",
            "classification": "Target's classification (normal, elite, rare, etc.)",
            "creatureType": "Target's creature type",
            "boss": "Check if target is a boss",
            "id": "Target's ID",
            "threat": "Threat percentage on target",
            "isplayer": "Check if target is a player"
        },
        "spell": {
            "cooldown": "Cooldown time remaining",
            "charges": "Number of charges available",
            "usable": "Check if spell is usable",
            "exists": "Check if spell exists in spellbook",
            "range": "Check if target is in range of spell",
            "casted": "Check if spell was cast recently"
        },
        "area": {
            "enemies": "Number of enemies in an area",
            "friendly": "Number of friendly units in an area"
        },
        "group": {
            "members": "Number of group members",
            "avghealth": "Average health percentage of the group",
            "raid": "Check if in a raid",
            "party": "Check if in a party"
        },
        "toggle": {
            "cooldowns": "Check if cooldowns are enabled",
            "aoe": "Check if AoE is enabled",
            "interrupt": "Check if interrupts are enabled",
            "custom": "Check custom toggle state"
        },
        "modifier": {
            "shift": "Check if shift is held",
            "control": "Check if control is held",
            "alt": "Check if alt is held",
            "lshift": "Check if left shift is held",
            "lcontrol": "Check if left control is held",
            "lalt": "Check if left alt is held",
            "rshift": "Check if right shift is held",
            "rcontrol": "Check if right control is held",
            "ralt": "Check if right alt is held"
        }
    }

    # Class-specific conditions
    CLASS_CONDITIONS = {
        "Druid": {
            "solar": "Solar energy amount",
            "lunar": "Lunar energy amount",
            "eclipse": "Eclipse direction/value",
            "balance.sun": "In Solar Eclipse",
            "balance.moon": "In Lunar Eclipse",
            "mushrooms": "Active mushrooms count"
        },
        "Death Knight": {
            "runes.count": "Available runes count",
            "runes.frac": "Fractional runes",
            "runes.depleted": "Depleted runes count"
        },
        "Warlock": {
            "embers": "Burning Embers count",
            "demonicfury": "Demonic Fury amount"
        }
    }

    OPERATORS = ['>', '<', '>=', '<=', '==', '!=', '&&', '||', '!']
    
    @staticmethod
    def validate_condition(condition: str) -> Tuple[bool, str]:
        """
        Validates a condition string
        Returns (is_valid, error_message)
        """
        if not condition or condition.strip() == "true":
            return True, ""
            
        try:
            # Remove whitespace
            condition = condition.strip()
            
            # Basic syntax validation
            if not ConditionValidator._check_basic_syntax(condition):
                return False, "Invalid condition syntax"
            
            # Validate operators
            if not ConditionValidator._validate_operators(condition):
                return False, "Invalid operator usage"
            
            # Validate parentheses
            if not ConditionValidator._validate_parentheses(condition):
                return False, "Mismatched parentheses"
            
            # Validate condition components
            if not ConditionValidator._validate_components(condition):
                return False, "Invalid condition components"
            
            return True, ""
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    @staticmethod
    def _check_basic_syntax(condition: str) -> bool:
        """Check basic condition syntax"""
        # Ensure no double spaces
        if "  " in condition:
            return False
            
        # Check for valid characters
        valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                         "0123456789._()!&|<>= ")
        if not all(c in valid_chars for c in condition):
            return False
            
        return True

    @staticmethod
    def _validate_operators(condition: str) -> bool:
        """Validate operator usage"""
        # Check for valid operator combinations
        invalid_combinations = ['&&&&', '||||', '!!', '<<', '>>', '==>', '<==']
        for combo in invalid_combinations:
            if combo in condition:
                return False
                
        # Ensure operators have spaces around them
        for op in ConditionValidator.OPERATORS:
            if op in condition and not (f" {op} " in condition or condition.startswith(f"{op} ")):
                return False
                
        return True

    @staticmethod
    def _validate_parentheses(condition: str) -> bool:
        """Validate parentheses matching"""
        stack = []
        for char in condition:
            if char == '(':
                stack.append(char)
            elif char == ')':
                if not stack:
                    return False
                stack.pop()
        return len(stack) == 0

    @staticmethod
    def _validate_components(condition: str) -> bool:
        """Validate individual condition components"""
        # Split condition into components
        components = re.split(r'\s+(?:&&|\|\|)\s+', condition)
        
        for component in components:
            # Remove NOT operator if present
            if component.startswith('!'):
                component = component[1:]
                
            # Extract the base condition
            base = component.split('(')[0] if '(' in component else component
            base = base.split('>')[0] if '>' in component else base
            base = base.split('<')[0] if '<' in component else base
            base = base.split('==')[0] if '==' in component else base
            base = base.split('!=')[0] if '!=' in component else base
            
            # Check if base condition exists
            parts = base.split('.')
            if len(parts) < 2:
                return False
                
            category = parts[0]
            subcategory = parts[1]
            
            # Check if category exists
            if category not in ConditionValidator.BASIC_CONDITIONS:
                return False
                
            # Check if subcategory exists
            if subcategory not in ConditionValidator.BASIC_CONDITIONS[category]:
                return False
                
        return True

class ConditionBuilder:
    """Helps build conditions through UI interaction"""
    
    def __init__(self):
        self.condition_parts: List[str] = []
        self.current_class: Optional[str] = None

    def set_class(self, class_name: str) -> None:
        """Set the current class for class-specific conditions"""
        self.current_class = class_name

    def get_available_categories(self) -> List[str]:
        """Get available condition categories"""
        categories = list(ConditionValidator.BASIC_CONDITIONS.keys())
        if self.current_class and self.current_class in ConditionValidator.CLASS_CONDITIONS:
            categories.append(self.current_class)
        return sorted(categories)

    def get_conditions_for_category(self, category: str) -> Dict[str, str]:
        """Get available conditions for a category"""
        if category in ConditionValidator.BASIC_CONDITIONS:
            return ConditionValidator.BASIC_CONDITIONS[category]
        elif category == self.current_class and self.current_class in ConditionValidator.CLASS_CONDITIONS:
            return ConditionValidator.CLASS_CONDITIONS[self.current_class]
        return {}

    def add_condition_part(self, category: str, condition: str, 
                         operator: str = "", value: str = "") -> None:
        """Add a part to the condition"""
        condition_str = f"{category}.{condition}"
        if operator and value:
            condition_str += f" {operator} {value}"
        self.condition_parts.append(condition_str)

    def add_logical_operator(self, operator: str) -> None:
        """Add a logical operator (AND/OR) between conditions"""
        self.condition_parts.append(operator)

    def add_not_operator(self) -> None:
        """Add a NOT operator to the next condition"""
        if self.condition_parts and self.condition_parts[-1] not in ['&&', '||']:
            self.condition_parts.append('!')

    def get_condition(self) -> str:
        """Get the complete condition string"""
        return " ".join(self.condition_parts)

    def clear(self) -> None:
        """Clear the current condition"""
        self.condition_parts = []

    def remove_last(self) -> None:
        """Remove the last condition part"""
        if self.condition_parts:
            self.condition_parts.pop()

    def validate(self) -> Tuple[bool, str]:
        """Validate the current condition"""
        return ConditionValidator.validate_condition(self.get_condition())

def parse_condition(condition_str: str) -> List[Dict[str, Any]]:
    """
    Parse a condition string into components
    Returns a list of condition components with their properties
    """
    components = []
    
    # Split by logical operators
    parts = re.split(r'\s*(?:&&|\|\|)\s*', condition_str)
    operators = re.findall(r'(?:&&|\|\|)', condition_str)
    
    for i, part in enumerate(parts):
        component = {}
        
        # Handle NOT operator
        if part.startswith('!'):
            component['not'] = True
            part = part[1:]
        else:
            component['not'] = False
            
        # Handle comparison operators
        match = re.match(r'([a-zA-Z_.]+)\s*([<>=!]+)\s*(\d+)', part)
        if match:
            component['condition'] = match.group(1)
            component['operator'] = match.group(2)
            component['value'] = match.group(3)
        else:
            component['condition'] = part
            component['operator'] = None
            component['value'] = None
            
        # Add logical operator
        if i < len(operators):
            component['logical_operator'] = operators[i]
        else:
            component['logical_operator'] = None
            
        components.append(component)
        
    return components