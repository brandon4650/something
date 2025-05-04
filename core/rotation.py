from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json
import time
from conditions import ConditionValidator
import spell_data

@dataclass
class SpellEntry:
    """Represents a spell in the rotation"""
    name: str
    condition: str
    priority: int
    enabled: bool = True
    notes: str = ""
    id: Optional[int] = None

@dataclass
class RotationMetadata:
    """Metadata for a rotation"""
    name: str
    class_name: str
    spec_name: str
    author: str
    version: str
    description: str
    created_at: float
    modified_at: float
    tags: List[str]

class Rotation:
    """Main rotation class"""
    
    def __init__(self, class_name: str, spec_name: str):
        self.metadata = RotationMetadata(
            name=f"{class_name} {spec_name} Rotation",
            class_name=class_name,
            spec_name=spec_name,
            author="",
            version="1.0",
            description="",
            created_at=time.time(),
            modified_at=time.time(),
            tags=[]
        )
        self.spells: List[SpellEntry] = []
        self.spec_id = spell_data.get_spec_id(class_name, spec_name)
        self._validate_spec()

    def _validate_spec(self) -> None:
        """Validate the class/spec combination"""
        if not self.spec_id:
            raise ValueError(f"Invalid class/spec combination: {self.metadata.class_name}/{self.metadata.spec_name}")

    def add_spell(self, spell_name: str, condition: str = "true", priority: Optional[int] = None) -> SpellEntry:
        """Add a spell to the rotation"""
        # Validate spell exists for class/spec
        if spell_name not in spell_data.get_spells_for_spec(self.metadata.class_name, self.metadata.spec_name):
            raise ValueError(f"Spell {spell_name} not found for {self.metadata.class_name}/{self.metadata.spec_name}")

        # Validate condition
        is_valid, error = ConditionValidator.validate_condition(condition)
        if not is_valid:
            raise ValueError(f"Invalid condition: {error}")

        # Set priority
        if priority is None:
            priority = len(self.spells) + 1
        else:
            # Shift existing spells if needed
            for spell in self.spells:
                if spell.priority >= priority:
                    spell.priority += 1

        # Create spell entry
        entry = SpellEntry(
            name=spell_name,
            condition=condition,
            priority=priority
        )
        
        self.spells.append(entry)
        self._sort_spells()
        self.metadata.modified_at = time.time()
        return entry

    def remove_spell(self, priority: int) -> bool:
        """Remove a spell from the rotation"""
        for i, spell in enumerate(self.spells):
            if spell.priority == priority:
                self.spells.pop(i)
                # Update priorities
                for s in self.spells:
                    if s.priority > priority:
                        s.priority -= 1
                self.metadata.modified_at = time.time()
                return True
        return False

    def move_spell(self, from_priority: int, to_priority: int) -> bool:
        """Move a spell to a new priority"""
        if from_priority == to_priority:
            return True

        spell_to_move = None
        for spell in self.spells:
            if spell.priority == from_priority:
                spell_to_move = spell
                break

        if not spell_to_move:
            return False

        # Update priorities
        if from_priority < to_priority:
            for spell in self.spells:
                if from_priority < spell.priority <= to_priority:
                    spell.priority -= 1
        else:
            for spell in self.spells:
                if to_priority <= spell.priority < from_priority:
                    spell.priority += 1

        spell_to_move.priority = to_priority
        self._sort_spells()
        self.metadata.modified_at = time.time()
        return True

    def _sort_spells(self) -> None:
        """Sort spells by priority"""
        self.spells.sort(key=lambda x: x.priority)

    def update_spell(self, priority: int, **kwargs) -> bool:
        """Update spell properties"""
        for spell in self.spells:
            if spell.priority == priority:
                if 'condition' in kwargs:
                    is_valid, error = ConditionValidator.validate_condition(kwargs['condition'])
                    if not is_valid:
                        raise ValueError(f"Invalid condition: {error}")
                
                for key, value in kwargs.items():
                    setattr(spell, key, value)
                
                self.metadata.modified_at = time.time()
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert rotation to dictionary"""
        return {
            'metadata': asdict(self.metadata),
            'spells': [asdict(spell) for spell in self.spells],
            'spec_id': self.spec_id
        }

    def to_soe_format(self) -> str:
        """Convert rotation to SOE Engine format"""
        soe_code = [
            f"-- {self.metadata.name}",
            f"-- Author: {self.metadata.author}",
            f"-- Version: {self.metadata.version}",
            f"-- Description: {self.metadata.description}",
            "",
            f"SOEEngine.rotation.register({self.spec_id}, {{",
        ]

        # Add spells
        for spell in self.spells:
            if spell.enabled:
                condition = spell.condition if spell.condition != "true" else "true"
                soe_code.append(f"    {{ \"{spell.name}\", \"{condition}\" }},")

        soe_code.append("})")
        return "\n".join(soe_code)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Rotation':
        """Create rotation from dictionary"""
        rotation = cls(data['metadata']['class_name'], data['metadata']['spec_name'])
        rotation.metadata = RotationMetadata(**data['metadata'])
        rotation.spells = [SpellEntry(**spell) for spell in data['spells']]
        rotation.spec_id = data['spec_id']
        return rotation

    @classmethod
    def from_soe_format(cls, soe_code: str) -> 'Rotation':
        """Create rotation from SOE Engine format"""
        # Parse SOE Engine code
        try:
            # Extract spec ID
            spec_id_match = re.search(r'register\((\d+)', soe_code)
            if not spec_id_match:
                raise ValueError("Could not find spec ID in code")
            
            spec_id = int(spec_id_match.group(1))
            
            # Find class and spec from spec ID
            class_name = None
            spec_name = None
            for c, specs in spell_data.SPEC_IDS.items():
                for s, sid in specs.items():
                    if sid == spec_id:
                        class_name = c
                        spec_name = s
                        break
                if class_name:
                    break
            
            if not class_name or not spec_name:
                raise ValueError(f"Invalid spec ID: {spec_id}")
            
            # Create rotation
            rotation = cls(class_name, spec_name)
            
            # Extract spell entries
            spell_pattern = r'\{\s*"([^"]+)",\s*"([^"]+)"\s*\}'
            spell_matches = re.finditer(spell_pattern, soe_code)
            
            for i, match in enumerate(spell_matches, 1):
                spell_name, condition = match.groups()
                rotation.add_spell(spell_name, condition, i)
            
            return rotation
            
        except Exception as e:
            raise ValueError(f"Error parsing SOE Engine code: {str(e)}")

class RotationManager:
    """Manages multiple rotations"""
    
    def __init__(self):
        self.rotations: Dict[str, Rotation] = {}

    def create_rotation(self, class_name: str, spec_name: str, name: Optional[str] = None) -> Rotation:
        """Create a new rotation"""
        rotation = Rotation(class_name, spec_name)
        if name:
            rotation.metadata.name = name
        key = self._generate_key(rotation)
        self.rotations[key] = rotation
        return rotation

    def _generate_key(self, rotation: Rotation) -> str:
        """Generate unique key for rotation"""
        base_key = f"{rotation.metadata.name}_{rotation.metadata.class_name}_{rotation.metadata.spec_name}"
        key = base_key
        counter = 1
        while key in self.rotations:
            key = f"{base_key}_{counter}"
            counter += 1
        return key

    def save_rotation(self, rotation: Rotation, filename: str) -> bool:
        """Save rotation to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(rotation.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving rotation: {e}")
            return False

    def load_rotation(self, filename: str) -> Optional[Rotation]:
        """Load rotation from file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            rotation = Rotation.from_dict(data)
            key = self._generate_key(rotation)
            self.rotations[key] = rotation
            return rotation
        except Exception as e:
            print(f"Error loading rotation: {e}")
            return None

    def get_rotations(self, class_name: Optional[str] = None, spec_name: Optional[str] = None) -> List[Rotation]:
        """Get rotations, optionally filtered by class/spec"""
        rotations = list(self.rotations.values())
        if class_name:
            rotations = [r for r in rotations if r.metadata.class_name == class_name]
        if spec_name:
            rotations = [r for r in rotations if r.metadata.spec_name == spec_name]
        return rotations

    def delete_rotation(self, rotation: Rotation) -> bool:
        """Delete a rotation"""
        for key, r in self.rotations.items():
            if r is rotation:
                del self.rotations[key]
                return True
        return False