from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from .rotation import Rotation, SpellEntry
import spell_data

@dataclass
class ValidationResult:
    """Results of a rotation validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    stats: Dict[str, Any]

@dataclass
class RotationAnalysis:
    """Detailed analysis of a rotation"""
    coverage: Dict[str, float]  # Coverage of different situations
    gaps: List[str]            # Potential gaps in rotation
    suggestions: List[str]     # Improvement suggestions
    complexity: float          # Complexity score (0-1)
    efficiency: float          # Efficiency score (0-1)

class RotationValidator:
    """Validates and analyzes rotations"""

    CRITICAL_SPELLS = {
        "Mage": {
            "Arcane": ["Arcane Blast", "Arcane Missiles", "Evocation"],
            "Fire": ["Fireball", "Pyroblast", "Fire Blast"],
            "Frost": ["Frostbolt", "Ice Lance", "Frozen Orb"]
        },
        "Paladin": {
            "Holy": ["Holy Light", "Divine Light", "Holy Shock"],
            "Protection": ["Shield of the Righteous", "Avenger's Shield", "Judgment"],
            "Retribution": ["Templar's Verdict", "Crusader Strike", "Judgment"]
        },
        "Warrior": {
            "Arms": ["Mortal Strike", "Colossus Smash", "Execute"],
            "Fury": ["Bloodthirst", "Wild Strike", "Raging Blow"],
            "Protection": ["Shield Slam", "Revenge", "Thunder Clap"]
        },
        "Druid": {
            "Balance": ["Wrath", "Starfire", "Starsurge"],
            "Feral": ["Rake", "Shred", "Rip"],
            "Guardian": ["Mangle", "Thrash", "Savage Defense"],
            "Restoration": ["Rejuvenation", "Healing Touch", "Swiftmend"]
        },
        "Death Knight": {
            "Blood": ["Death Strike", "Heart Strike", "Blood Boil"],
            "Frost": ["Obliterate", "Frost Strike", "Howling Blast"],
            "Unholy": ["Scourge Strike", "Festering Strike", "Death Coil"]
        },
        "Hunter": {
            "Beast Mastery": ["Kill Command", "Arcane Shot", "Cobra Shot"],
            "Marksmanship": ["Chimera Shot", "Aimed Shot", "Steady Shot"],
            "Survival": ["Explosive Shot", "Black Arrow", "Arcane Shot"]
        },
        "Priest": {
            "Discipline": ["Penance", "Power Word: Shield", "Prayer of Mending"],
            "Holy": ["Prayer of Mending", "Circle of Healing", "Holy Word: Sanctuary"],
            "Shadow": ["Mind Blast", "Mind Flay", "Shadow Word: Pain"]
        },
        "Rogue": {
            "Assassination": ["Mutilate", "Envenom", "Rupture"],
            "Combat": ["Sinister Strike", "Eviscerate", "Revealing Strike"],
            "Subtlety": ["Backstab", "Hemorrhage", "Eviscerate"]
        },
        "Shaman": {
            "Elemental": ["Lightning Bolt", "Lava Burst", "Earth Shock"],
            "Enhancement": ["Stormstrike", "Lava Lash", "Lightning Bolt"],
            "Restoration": ["Healing Wave", "Riptide", "Chain Heal"]
        },
        "Warlock": {
            "Affliction": ["Agony", "Corruption", "Malefic Grasp"],
            "Demonology": ["Shadow Bolt", "Hand of Gul'dan", "Soul Fire"],
            "Destruction": ["Incinerate", "Chaos Bolt", "Immolate"]
        },
        "Monk": {
            "Brewmaster": ["Keg Smash", "Blackout Kick", "Guard"],
            "Windwalker": ["Tiger Palm", "Rising Sun Kick", "Fists of Fury"],
            "Mistweaver": ["Soothing Mist", "Enveloping Mist", "Renewing Mist"]
        }
    }

    DEFENSIVE_SPELLS = {
        "Mage": ["Ice Block", "Frost Nova", "Blink"],
        "Paladin": ["Divine Shield", "Hand of Protection", "Divine Protection"],
        "Warrior": ["Shield Wall", "Last Stand", "Spell Reflection"],
        "Druid": ["Barkskin", "Survival Instincts", "Frenzied Regeneration"],
        "Death Knight": ["Anti-Magic Shell", "Icebound Fortitude", "Vampiric Blood"],
        "Hunter": ["Deterrence", "Disengage", "Feign Death"],
        "Priest": ["Dispersion", "Pain Suppression", "Guardian Spirit"],
        "Rogue": ["Cloak of Shadows", "Evasion", "Combat Readiness"],
        "Shaman": ["Astral Shift", "Shamanistic Rage", "Healing Stream Totem"],
        "Warlock": ["Unending Resolve", "Dark Bargain", "Sacrificial Pact"],
        "Monk": ["Fortifying Brew", "Guard", "Touch of Karma"]
    }

    COOLDOWN_SPELLS = {
        "Mage": ["Time Warp", "Mirror Image", "Arcane Power", "Combustion", "Icy Veins"],
        "Paladin": ["Avenging Wrath", "Guardian of Ancient Kings", "Holy Avenger"],
        "Warrior": ["Recklessness", "Bladestorm", "Avatar"],
        "Druid": ["Incarnation", "Nature's Vigil", "Force of Nature"],
        "Death Knight": ["Pillar of Frost", "Dancing Rune Weapon", "Summon Gargoyle"],
        "Hunter": ["Rapid Fire", "Bestial Wrath", "Stampede"],
        "Priest": ["Power Infusion", "Shadowfiend", "Divine Hymn"],
        "Rogue": ["Adrenaline Rush", "Shadow Dance", "Vendetta"],
        "Shaman": ["Ascendance", "Stormlash Totem", "Fire Elemental Totem"],
        "Warlock": ["Dark Soul", "Summon Doomguard", "Grimoire of Service"],
        "Monk": ["Energizing Brew", "Tigereye Brew", "Thunder Focus Tea"]
    }

    @classmethod
    def validate_rotation(cls, rotation: Rotation) -> ValidationResult:
        """
        Perform comprehensive validation of a rotation
        """
        errors = []
        warnings = []
        stats = {
            "spell_count": len(rotation.spells),
            "critical_spells": 0,
            "defensive_spells": 0,
            "cooldown_spells": 0,
            "conditional_spells": 0
        }

        # Check for critical spells
        critical_spells = cls.CRITICAL_SPELLS.get(rotation.metadata.class_name, {}).get(rotation.metadata.spec_name, [])
        found_critical = set()
        for spell in rotation.spells:
            if spell.name in critical_spells:
                found_critical.add(spell.name)
                stats["critical_spells"] += 1

        missing_critical = set(critical_spells) - found_critical
        if missing_critical:
            errors.append(f"Missing critical spells: {', '.join(missing_critical)}")

        # Check for defensive abilities
        class_defensives = cls.DEFENSIVE_SPELLS.get(rotation.metadata.class_name, [])
        for spell in rotation.spells:
            if spell.name in class_defensives:
                stats["defensive_spells"] += 1

        if stats["defensive_spells"] == 0:
            warnings.append("No defensive abilities in rotation")

        # Check for cooldowns
        class_cooldowns = cls.COOLDOWN_SPELLS.get(rotation.metadata.class_name, [])
        for spell in rotation.spells:
            if spell.name in class_cooldowns:
                stats["cooldown_spells"] += 1

        if stats["cooldown_spells"] == 0:
            warnings.append("No cooldown abilities in rotation")

        # Check conditions
        for spell in rotation.spells:
            if spell.condition != "true":
                stats["conditional_spells"] += 1

        # Check for duplicate spells
        spell_names = [spell.name for spell in rotation.spells]
        duplicates = {name for name in spell_names if spell_names.count(name) > 1}
        if duplicates:
            warnings.append(f"Duplicate spells found: {', '.join(duplicates)}")

        # Check for empty conditions
        empty_conditions = [spell.name for spell in rotation.spells if not spell.condition]
        if empty_conditions:
            errors.append(f"Empty conditions found for: {', '.join(empty_conditions)}")

        # Validate all conditions
        from conditions import ConditionValidator
        for spell in rotation.spells:
            is_valid, error = ConditionValidator.validate_condition(spell.condition)
            if not is_valid:
                errors.append(f"Invalid condition for {spell.name}: {error}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            stats=stats
        )

    @classmethod
    def analyze_rotation(cls, rotation: Rotation) -> RotationAnalysis:
        """
        Perform detailed analysis of a rotation
        """
        # Calculate coverage
        coverage = {
            "single_target": cls._calculate_single_target_coverage(rotation),
            "aoe": cls._calculate_aoe_coverage(rotation),
            "defensive": cls._calculate_defensive_coverage(rotation),
            "cooldown": cls._calculate_cooldown_coverage(rotation)
        }

        # Find gaps
        gaps = cls._find_rotation_gaps(rotation)

        # Generate suggestions
        suggestions = cls._generate_suggestions(rotation, coverage, gaps)

        # Calculate complexity
        complexity = cls._calculate_complexity(rotation)

        # Calculate efficiency
        efficiency = cls._calculate_efficiency(rotation)

        return RotationAnalysis(
            coverage=coverage,
            gaps=gaps,
            suggestions=suggestions,
            complexity=complexity,
            efficiency=efficiency
        )

    @classmethod
    def _calculate_single_target_coverage(cls, rotation: Rotation) -> float:
        """Calculate single target rotation coverage"""
        critical_spells = set(cls.CRITICAL_SPELLS.get(rotation.metadata.class_name, {})
                            .get(rotation.metadata.spec_name, []))
        found_spells = set(spell.name for spell in rotation.spells 
                         if spell.name in critical_spells)
        return len(found_spells) / len(critical_spells) if critical_spells else 0.0

    @classmethod
    def _calculate_aoe_coverage(cls, rotation: Rotation) -> float:
        """Calculate AOE rotation coverage"""
        has_aoe_condition = False
        has_aoe_spells = False
        
        for spell in rotation.spells:
            if "area.enemies" in spell.condition:
                has_aoe_condition = True
            # Add class-specific AOE spells check here
            
        return 1.0 if has_aoe_condition and has_aoe_spells else 0.0

    @classmethod
    def _calculate_defensive_coverage(cls, rotation: Rotation) -> float:
        """Calculate defensive ability coverage"""
        class_defensives = set(cls.DEFENSIVE_SPELLS.get(rotation.metadata.class_name, []))
        found_defensives = set(spell.name for spell in rotation.spells 
                             if spell.name in class_defensives)
        return len(found_defensives) / len(class_defensives) if class_defensives else 0.0

    @classmethod
    def _calculate_cooldown_coverage(cls, rotation: Rotation) -> float:
        """Calculate cooldown usage coverage"""
        class_cooldowns = set(cls.COOLDOWN_SPELLS.get(rotation.metadata.class_name, []))
        found_cooldowns = set(spell.name for spell in rotation.spells 
                            if spell.name in class_cooldowns)
        return len(found_cooldowns) / len(class_cooldowns) if class_cooldowns else 0.0

    @classmethod
    def _find_rotation_gaps(cls, rotation: Rotation) -> List[str]:
        """Find potential gaps in the rotation"""
        gaps = []
        
        # Check for missing core rotation elements
        critical_spells = cls.CRITICAL_SPELLS.get(rotation.metadata.class_name, {}).get(rotation.metadata.spec_name, [])
        found_critical = set(spell.name for spell in rotation.spells)
        missing_critical = set(critical_spells) - found_critical
        
        if missing_critical:
            gaps.append(f"Missing core abilities: {', '.join(missing_critical)}")

        # Check for resource generation/spending balance
        # This would be class-specific
        
        # Check for cooldown distribution
        cooldown_positions = [i for i, spell in enumerate(rotation.spells) 
                            if spell.name in cls.COOLDOWN_SPELLS.get(rotation.metadata.class_name, [])]
        if len(cooldown_positions) >= 2:
            for i in range(len(cooldown_positions) - 1):
                if cooldown_positions[i+1] - cooldown_positions[i] < 2:
                    gaps.append("Cooldowns are clustered too closely")
                    break

        return gaps

    @classmethod
    def _generate_suggestions(cls, rotation: Rotation, 
                            coverage: Dict[str, float], 
                            gaps: List[str]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []

        # Coverage-based suggestions
        if coverage["single_target"] < 0.8:
            suggestions.append("Consider adding more core rotation abilities")
        if coverage["aoe"] < 0.5:
            suggestions.append("Consider adding AOE abilities or conditions")
        if coverage["defensive"] < 0.3:
            suggestions.append("Consider adding defensive cooldowns")
        if coverage["cooldown"] < 0.5:
            suggestions.append("Consider adding major cooldowns")

        # Condition-based suggestions
        has_resource_conditions = False
        has_proc_conditions = False
        has_health_conditions = False
        
        for spell in rotation.spells:
            if any(resource in spell.condition for resource in 
                  ["mana", "rage", "energy", "focus", "runicpower", "holypower"]):
                has_resource_conditions = True
            if "buff" in spell.condition:
                has_proc_conditions = True
            if "health" in spell.condition:
                has_health_conditions = True

        if not has_resource_conditions:
            suggestions.append("Consider adding resource-based conditions")
        if not has_proc_conditions:
            suggestions.append("Consider adding proc/buff tracking conditions")
        if not has_health_conditions:
            suggestions.append("Consider adding health-based defensive conditions")

        return suggestions

    @classmethod
    def _calculate_complexity(cls, rotation: Rotation) -> float:
        """Calculate rotation complexity score"""
        if not rotation.spells:
            return 0.0

        factors = {
            "spell_count": len(rotation.spells) / 20,  # Normalized to 20 spells
            "condition_complexity": sum(len(spell.condition.split()) for spell in rotation.spells) / (len(rotation.spells) * 10),
            "conditional_ratio": len([s for s in rotation.spells if s.condition != "true"]) / len(rotation.spells),
            "cooldown_ratio": len([s for s in rotation.spells if s.name in cls.COOLDOWN_SPELLS.get(rotation.metadata.class_name, [])]) / len(rotation.spells)
        }

        return min(1.0, sum(factors.values()) / len(factors))

    @classmethod
    def _calculate_efficiency(cls, rotation: Rotation) -> float:
        """Calculate rotation efficiency score"""
        if not rotation.spells:
            return 0.0

        factors = {
            "critical_coverage": cls._calculate_single_target_coverage(rotation),
            "defensive_coverage": cls._calculate_defensive_coverage(rotation),
            "cooldown_coverage": cls._calculate_cooldown_coverage(rotation),
            "condition_presence": 1.0 if any(spell.condition != "true" for spell in rotation.spells) else 0.0
        }

        return sum(factors.values()) / len(factors)