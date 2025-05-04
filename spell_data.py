"""
Spell data module for SOE Engine Rotation Creator.

This module provides class, specialization, and spell data for World of Warcraft 5.4.8.
"""

import os
import json

# Class to Spec ID mapping (from SOE Engine documentation)
SPEC_IDS = {
    "Mage": {
        "Arcane": 62,
        "Fire": 63,
        "Frost": 64
    },
    "Paladin": {
        "Holy": 65,
        "Protection": 66,
        "Retribution": 70
    },
    "Warrior": {
        "Arms": 71,
        "Fury": 72,
        "Protection": 73
    },
    "Druid": {
        "Balance": 102,
        "Feral": 103,
        "Guardian": 104,
        "Restoration": 105
    },
    "Death Knight": {
        "Blood": 250,
        "Frost": 251,
        "Unholy": 252
    },
    "Hunter": {
        "Beast Mastery": 253,
        "Marksmanship": 254,
        "Survival": 255
    },
    "Priest": {
        "Discipline": 256,
        "Holy": 257,
        "Shadow": 258
    },
    "Rogue": {
        "Assassination": 259,
        "Combat": 260,
        "Subtlety": 261
    },
    "Shaman": {
        "Elemental": 262,
        "Enhancement": 263,
        "Restoration": 264
    },
    "Warlock": {
        "Affliction": 265,
        "Demonology": 266,
        "Destruction": 267
    },
    "Monk": {
        "Brewmaster": 268,
        "Windwalker": 269,
        "Mistweaver": 270
    }
}

# WoW 5.4.8 spells - a comprehensive list of all available spells for each class and spec
# This is a simplified dataset for the application
SPELL_DATA = {
    "Mage": {
        "Arcane": [
            "Arcane Blast", "Arcane Missiles", "Arcane Barrage", "Arcane Power", 
            "Arcane Brilliance", "Evocation", "Blink", "Frost Nova", "Slow", 
            "Presence of Mind", "Time Warp", "Mirror Image", "Invisibility", 
            "Conjure Mana Gem", "Arcane Explosion", "Counterspell", "Spellsteal", 
            "Remove Curse", "Flamestrike", "Polymorph", "Ice Block"
        ],
        "Fire": [
            "Fireball", "Pyroblast", "Fire Blast", "Flamestrike", "Combustion", 
            "Dragon's Breath", "Scorch", "Living Bomb", "Blast Wave", "Molten Armor", 
            "Arcane Brilliance", "Evocation", "Blink", "Frost Nova", "Mirror Image", 
            "Time Warp", "Invisibility", "Conjure Mana Gem", "Counterspell", "Spellsteal", 
            "Remove Curse", "Polymorph", "Ice Block"
        ],
        "Frost": [
            "Frostbolt", "Ice Lance", "Frost Nova", "Blizzard", "Frozen Orb", 
            "Icy Veins", "Cone of Cold", "Frostfire Bolt", "Ice Barrier", "Cold Snap", 
            "Frost Armor", "Arcane Brilliance", "Evocation", "Blink", "Mirror Image", 
            "Time Warp", "Invisibility", "Conjure Mana Gem", "Counterspell", "Spellsteal", 
            "Remove Curse", "Polymorph", "Ice Block"
        ]
    },
    "Paladin": {
        "Holy": [
            "Holy Light", "Divine Light", "Holy Shock", "Word of Glory", "Holy Radiance", 
            "Light of Dawn", "Beacon of Light", "Divine Shield", "Divine Protection", 
            "Lay on Hands", "Blessing of Kings", "Blessing of Might", "Hand of Protection", 
            "Hand of Freedom", "Hand of Sacrifice", "Hand of Salvation", "Devotion Aura", 
            "Holy Prism", "Judgment", "Hammer of Justice", "Turn Evil", "Divine Plea"
        ],
        "Protection": [
            "Shield of the Righteous", "Avenger's Shield", "Consecration", "Hammer of the Righteous", 
            "Judgment", "Holy Wrath", "Word of Glory", "Guardian of Ancient Kings", "Divine Protection", 
            "Ardent Defender", "Divine Shield", "Blessing of Kings", "Blessing of Might", 
            "Hand of Protection", "Hand of Freedom", "Hand of Sacrifice", "Hand of Salvation", 
            "Devotion Aura", "Light's Hammer", "Hammer of Justice", "Turn Evil", "Divine Plea"
        ],
        "Retribution": [
            "Templar's Verdict", "Crusader Strike", "Hammer of Wrath", "Judgment", "Exorcism", 
            "Inquisition", "Execution Sentence", "Avenging Wrath", "Divine Shield", "Divine Protection", 
            "Blessing of Kings", "Blessing of Might", "Hand of Protection", "Hand of Freedom", 
            "Hand of Sacrifice", "Hand of Salvation", "Devotion Aura", "Hammer of Justice", 
            "Turn Evil", "Divine Plea"
        ]
    },
    "Warrior": {
        "Arms": [
            "Mortal Strike", "Overpower", "Slam", "Execute", "Colossus Smash", 
            "Rend", "Thunder Clap", "Sweeping Strikes", "Bladestorm", "Die by the Sword", 
            "Battle Shout", "Commanding Shout", "Charge", "Heroic Leap", "Hamstring", 
            "Rallying Cry", "Intervene", "Spell Reflection", "Shield Wall", "Pummel", 
            "Intimidating Shout", "Berserker Rage", "Victory Rush"
        ],
        "Fury": [
            "Bloodthirst", "Wild Strike", "Raging Blow", "Execute", "Colossus Smash", 
            "Thunder Clap", "Whirlwind", "Berserker Rage", "Recklessness", "Battle Shout", 
            "Commanding Shout", "Charge", "Heroic Leap", "Hamstring", "Rallying Cry", 
            "Intervene", "Spell Reflection", "Shield Wall", "Pummel", "Intimidating Shout", 
            "Victory Rush"
        ],
        "Protection": [
            "Shield Slam", "Revenge", "Thunder Clap", "Devastate", "Shield Block", 
            "Shield Barrier", "Demoralizing Shout", "Last Stand", "Shield Wall", "Battle Shout", 
            "Commanding Shout", "Charge", "Heroic Leap", "Intervene", "Spell Reflection", 
            "Pummel", "Intimidating Shout", "Berserker Rage", "Victory Rush"
        ]
    },
    "Druid": {
        "Balance": [
            "Wrath", "Starfire", "Starsurge", "Moonfire", "Sunfire", "Starfall", 
            "Hurricane", "Wild Mushroom", "Wild Mushroom: Detonate", "Celestial Alignment", 
            "Force of Nature", "Faerie Fire", "Barkskin", "Innervate", "Mark of the Wild", 
            "Rebirth", "Tranquility", "Cyclone", "Entangling Roots", "Hibernate", 
            "Solar Beam", "Typhoon", "Nature's Swiftness", "Symbiosis"
        ],
        "Feral": [
            "Shred", "Rake", "Rip", "Ferocious Bite", "Savage Roar", "Tiger's Fury", 
            "Berserk", "Cat Form", "Maim", "Faerie Fire", "Barkskin", "Innervate", 
            "Mark of the Wild", "Rebirth", "Tranquility", "Cyclone", "Entangling Roots", 
            "Hibernate", "Skull Bash", "Nature's Swiftness", "Symbiosis"
        ],
        "Guardian": [
            "Mangle", "Maul", "Lacerate", "Thrash", "Savage Defense", "Frenzied Regeneration", 
            "Survival Instincts", "Bear Form", "Incarnation: Son of Ursoc", "Faerie Fire", 
            "Barkskin", "Innervate", "Mark of the Wild", "Rebirth", "Tranquility", 
            "Cyclone", "Entangling Roots", "Hibernate", "Skull Bash", "Nature's Swiftness", 
            "Symbiosis"
        ],
        "Restoration": [
            "Rejuvenation", "Healing Touch", "Regrowth", "Lifebloom", "Wild Growth", 
            "Swiftmend", "Tranquility", "Wild Mushroom", "Wild Mushroom: Bloom", 
            "Nature's Swiftness", "Ironbark", "Innervate", "Barkskin", "Mark of the Wild", 
            "Rebirth", "Cyclone", "Entangling Roots", "Hibernate", "Symbiosis"
        ]
    },
    "Death Knight": {
        "Blood": [
            "Death Strike", "Heart Strike", "Blood Boil", "Outbreak", "Soul Reaper", 
            "Dancing Rune Weapon", "Rune Tap", "Vampiric Blood", "Icebound Fortitude", 
            "Anti-Magic Shell", "Death Grip", "Mind Freeze", "Strangulate", "Army of the Dead", 
            "Raise Dead", "Dark Command", "Death's Advance", "Empower Rune Weapon", "Horn of Winter"
        ],
        "Frost": [
            "Obliterate", "Frost Strike", "Howling Blast", "Outbreak", "Soul Reaper", 
            "Pillar of Frost", "Remorseless Winter", "Icebound Fortitude", "Anti-Magic Shell", 
            "Death Grip", "Mind Freeze", "Strangulate", "Army of the Dead", "Raise Dead", 
            "Dark Command", "Death's Advance", "Empower Rune Weapon", "Horn of Winter"
        ],
        "Unholy": [
            "Scourge Strike", "Death Coil", "Festering Strike", "Outbreak", "Soul Reaper", 
            "Dark Transformation", "Summon Gargoyle", "Icebound Fortitude", "Anti-Magic Shell", 
            "Death Grip", "Mind Freeze", "Strangulate", "Army of the Dead", "Raise Dead", 
            "Dark Command", "Death's Advance", "Empower Rune Weapon", "Horn of Winter"
        ]
    },
    "Hunter": {
        "Beast Mastery": [
            "Arcane Shot", "Steady Shot", "Kill Command", "Focus Fire", "Bestial Wrath", 
            "Dire Beast", "Multi-Shot", "Cobra Shot", "Rapid Fire", "Disengage", 
            "Deterrence", "Concussive Shot", "Freezing Trap", "Snake Trap", "Explosive Trap", 
            "Ice Trap", "Flare", "Feign Death", "Misdirection", "Tranquilizing Shot", 
            "Counter Shot", "Aspect of the Hawk", "Aspect of the Cheetah", "Aspect of the Pack"
        ],
        "Marksmanship": [
            "Chimera Shot", "Steady Shot", "Aimed Shot", "Arcane Shot", "Murder of Crows", 
            "Multi-Shot", "Rapid Fire", "Disengage", "Deterrence", "Concussive Shot", 
            "Freezing Trap", "Snake Trap", "Explosive Trap", "Ice Trap", "Flare", 
            "Feign Death", "Misdirection", "Tranquilizing Shot", "Counter Shot", 
            "Aspect of the Hawk", "Aspect of the Cheetah", "Aspect of the Pack"
        ],
        "Survival": [
            "Explosive Shot", "Black Arrow", "Serpent Sting", "Arcane Shot", "Multi-Shot", 
            "Cobra Shot", "Rapid Fire", "Disengage", "Deterrence", "Concussive Shot", 
            "Freezing Trap", "Snake Trap", "Explosive Trap", "Ice Trap", "Flare", 
            "Feign Death", "Misdirection", "Tranquilizing Shot", "Counter Shot", 
            "Aspect of the Hawk", "Aspect of the Cheetah", "Aspect of the Pack"
        ]
    },
    "Priest": {
        "Discipline": [
            "Power Word: Shield", "Penance", "Prayer of Mending", "Flash Heal", "Greater Heal", 
            "Prayer of Healing", "Power Word: Barrier", "Pain Suppression", "Spirit Shell", 
            "Divine Aegis", "Inner Focus", "Archangel", "Dispel Magic", "Mass Dispel", 
            "Purify", "Leap of Faith", "Fear Ward", "Fade", "Psychic Scream", "Power Word: Fortitude", 
            "Divine Hymn", "Holy Fire", "Smite"
        ],
        "Holy": [
            "Heal", "Flash Heal", "Greater Heal", "Binding Heal", "Prayer of Mending", 
            "Prayer of Healing", "Circle of Healing", "Holy Word: Sanctuary", "Divine Hymn", 
            "Guardian Spirit", "Renew", "Chakra", "Dispel Magic", "Mass Dispel", "Purify", 
            "Leap of Faith", "Fear Ward", "Fade", "Psychic Scream", "Power Word: Fortitude", 
            "Holy Fire", "Smite"
        ],
        "Shadow": [
            "Mind Blast", "Mind Flay", "Shadow Word: Pain", "Vampiric Touch", "Devouring Plague", 
            "Mind Spike", "Shadow Word: Death", "Shadowfiend", "Dispersion", "Psychic Horror", 
            "Dispel Magic", "Mass Dispel", "Leap of Faith", "Fear Ward", "Fade", 
            "Psychic Scream", "Power Word: Fortitude", "Shadow Word: Insanity"
        ]
    },
    "Rogue": {
        "Assassination": [
            "Mutilate", "Envenom", "Dispatch", "Rupture", "Garrote", "Vendetta", 
            "Fan of Knives", "Crimson Tempest", "Slice and Dice", "Recuperate", "Sprint", 
            "Vanish", "Cloak of Shadows", "Evasion", "Combat Readiness", "Shadow Step", 
            "Feint", "Kick", "Blind", "Tricks of the Trade", "Kidney Shot", "Cheap Shot", 
            "Sap", "Distract", "Stealth"
        ],
        "Combat": [
            "Sinister Strike", "Eviscerate", "Revealing Strike", "Slice and Dice", 
            "Adrenaline Rush", "Killing Spree", "Blade Flurry", "Fan of Knives", 
            "Crimson Tempest", "Recuperate", "Sprint", "Vanish", "Cloak of Shadows", 
            "Evasion", "Combat Readiness", "Feint", "Kick", "Blind", "Tricks of the Trade", 
            "Kidney Shot", "Cheap Shot", "Sap", "Distract", "Stealth"
        ],
        "Subtlety": [
            "Backstab", "Hemorrhage", "Eviscerate", "Rupture", "Shadow Dance", "Premeditation", 
            "Ambush", "Fan of Knives", "Crimson Tempest", "Slice and Dice", "Recuperate", 
            "Sprint", "Vanish", "Cloak of Shadows", "Evasion", "Combat Readiness", 
            "Shadow Step", "Feint", "Kick", "Blind", "Tricks of the Trade", "Kidney Shot", 
            "Cheap Shot", "Sap", "Distract", "Stealth"
        ]
    },
    "Shaman": {
        "Elemental": [
            "Lightning Bolt", "Chain Lightning", "Earth Shock", "Flame Shock", "Lava Burst", 
            "Earthquake", "Elemental Blast", "Thunderstorm", "Ascendance", "Spiritwalker's Grace", 
            "Fire Elemental Totem", "Earth Elemental Totem", "Healing Stream Totem", 
            "Healing Tide Totem", "Grounding Totem", "Capacitor Totem", "Wind Shear", 
            "Ghost Wolf", "Water Walking", "Water Breathing"
        ],
        "Enhancement": [
            "Stormstrike", "Lava Lash", "Earth Shock", "Flame Shock", "Lightning Bolt", 
            "Searing Totem", "Feral Spirit", "Ascendance", "Fire Elemental Totem", 
            "Earth Elemental Totem", "Healing Stream Totem", "Healing Tide Totem", 
            "Grounding Totem", "Capacitor Totem", "Wind Shear", "Ghost Wolf", "Water Walking", 
            "Water Breathing"
        ],
        "Restoration": [
            "Healing Wave", "Healing Surge", "Greater Healing Wave", "Chain Heal", 
            "Riptide", "Healing Rain", "Healing Stream Totem", "Healing Tide Totem", 
            "Spirit Link Totem", "Ascendance", "Spiritwalker's Grace", "Earth Shield", 
            "Water Shield", "Grounding Totem", "Capacitor Totem", "Wind Shear", "Ghost Wolf", 
            "Water Walking", "Water Breathing"
        ]
    },
    "Warlock": {
        "Affliction": [
            "Agony", "Corruption", "Unstable Affliction", "Malefic Grasp", "Haunt", 
            "Drain Soul", "Seed of Corruption", "Soulburn", "Dark Soul: Misery", "Life Tap", 
            "Fear", "Howl of Terror", "Mortal Coil", "Demonic Circle: Teleport", 
            "Unending Resolve", "Dark Bargain", "Soulshatter", "Fel Armor", "Health Funnel", 
            "Create Healthstone", "Summon Doomguard", "Summon Infernal", "Summon Felhunter", 
            "Summon Voidwalker", "Summon Imp", "Summon Succubus"
        ],
        "Demonology": [
            "Shadow Bolt", "Soul Fire", "Hand of Gul'dan", "Metamorphosis", "Touch of Chaos", 
            "Doom", "Hellfire", "Chaos Wave", "Dark Soul: Knowledge", "Life Tap", "Fear", 
            "Howl of Terror", "Mortal Coil", "Demonic Circle: Teleport", "Unending Resolve", 
            "Dark Bargain", "Soulshatter", "Fel Armor", "Health Funnel", "Create Healthstone", 
            "Summon Doomguard", "Summon Infernal", "Summon Felhunter", "Summon Voidwalker", 
            "Summon Imp", "Summon Felguard"
        ],
        "Destruction": [
            "Incinerate", "Immolate", "Conflagrate", "Chaos Bolt", "Shadowburn", "Rain of Fire", 
            "Havoc", "Dark Soul: Instability", "Life Tap", "Fear", "Howl of Terror", 
            "Mortal Coil", "Demonic Circle: Teleport", "Unending Resolve", "Dark Bargain", 
            "Soulshatter", "Fel Armor", "Health Funnel", "Create Healthstone", 
            "Summon Doomguard", "Summon Infernal", "Summon Felhunter", "Summon Voidwalker", 
            "Summon Imp", "Summon Succubus"
        ]
    },
    "Monk": {
        "Brewmaster": [
            "Keg Smash", "Blackout Kick", "Tiger Palm", "Breath of Fire", "Guard", 
            "Purifying Brew", "Fortifying Brew", "Zen Sphere", "Chi Wave", "Leg Sweep", 
            "Rushing Jade Wind", "Summon Black Ox Statue", "Spear Hand Strike", "Elusive Brew", 
            "Expel Harm", "Detox", "Roll", "Flying Serpent Kick", "Spinning Crane Kick", 
            "Touch of Death", "Paralysis", "Legacy of the Emperor", "Legacy of the White Tiger"
        ],
        "Windwalker": [
            "Tiger Palm", "Blackout Kick", "Rising Sun Kick", "Fists of Fury", "Spinning Crane Kick", 
            "Touch of Death", "Storm, Earth, and Fire", "Energizing Brew", "Tiger's Lust", 
            "Chi Wave", "Zen Sphere", "Leg Sweep", "Rushing Jade Wind", "Spear Hand Strike", 
            "Expel Harm", "Detox", "Roll", "Flying Serpent Kick", "Touch of Karma", 
            "Paralysis", "Legacy of the Emperor", "Legacy of the White Tiger"
        ],
        "Mistweaver": [
            "Soothing Mist", "Enveloping Mist", "Surging Mist", "Renewing Mist", "Chi Wave", 
            "Zen Sphere", "Chi Burst", "Life Cocoon", "Revival", "Thunder Focus Tea", 
            "Spinning Crane Kick", "Detox", "Roll", "Flying Serpent Kick", "Touch of Death", 
            "Paralysis", "Legacy of the Emperor", "Legacy of the White Tiger"
        ]
    }
}

def get_available_classes():
    """Get a list of available classes."""
    return sorted(SPEC_IDS.keys())

def get_specs_for_class(class_name):
    """Get a list of specializations for a given class."""
    if class_name in SPEC_IDS:
        return sorted(SPEC_IDS[class_name].keys())
    return []

def get_spec_id(class_name, spec_name):
    """Get the specialization ID for a given class and spec."""
    if class_name in SPEC_IDS and spec_name in SPEC_IDS[class_name]:
        return SPEC_IDS[class_name][spec_name]
    return None

def get_spells_for_spec(class_name, spec_name):
    """Get a list of spells for a given class and spec."""
    if class_name in SPELL_DATA and spec_name in SPELL_DATA[class_name]:
        return sorted(SPELL_DATA[class_name][spec_name])
    return []

def save_user_spell_data(spell_data, filename="user_spell_data.json"):
    """Save custom user spell data."""
    try:
        with open(filename, 'w') as f:
            json.dump(spell_data, f, indent=2)
        return True
    except Exception:
        return False

def load_user_spell_data(filename="user_spell_data.json"):
    """Load custom user spell data."""
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}
