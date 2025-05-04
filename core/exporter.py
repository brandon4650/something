from typing import Dict, List, Optional, Tuple, Any
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import re
from .rotation import Rotation, SpellEntry
import spell_data

class RotationExporter:
    """Handles exporting rotations to different formats"""

    @staticmethod
    def to_soe(rotation: Rotation) -> str:
        """Export rotation to SOE Engine format"""
        lines = [
            f"-- {rotation.metadata.name}",
            f"-- Author: {rotation.metadata.author}",
            f"-- Version: {rotation.metadata.version}",
            f"-- Created: {datetime.fromtimestamp(rotation.metadata.created_at).strftime('%Y-%m-%d %H:%M:%S')}",
            f"-- Last Modified: {datetime.fromtimestamp(rotation.metadata.modified_at).strftime('%Y-%m-%d %H:%M:%S')}",
            "-- Description:",
            f"-- {rotation.metadata.description}",
            "",
            f"SOEEngine.rotation.register({rotation.spec_id}, {{",
            "    -- Combat rotation",
        ]

        # Add combat rotation spells
        for spell in rotation.spells:
            if spell.enabled:
                condition = spell.condition if spell.condition != "true" else "true"
                if spell.notes:
                    lines.append(f"    -- {spell.notes}")
                lines.append(f"    {{ \"{spell.name}\", \"{condition}\" }},")

        # Add closing bracket
        lines.append("})")

        return "\n".join(lines)

    @staticmethod
    def to_json(rotation: Rotation, pretty: bool = True) -> str:
        """Export rotation to JSON format"""
        data = {
            "format_version": "1.0",
            "metadata": {
                "name": rotation.metadata.name,
                "class_name": rotation.metadata.class_name,
                "spec_name": rotation.metadata.spec_name,
                "author": rotation.metadata.author,
                "version": rotation.metadata.version,
                "description": rotation.metadata.description,
                "created_at": rotation.metadata.created_at,
                "modified_at": rotation.metadata.modified_at,
                "tags": rotation.metadata.tags
            },
            "spec_id": rotation.spec_id,
            "spells": [
                {
                    "name": spell.name,
                    "condition": spell.condition,
                    "priority": spell.priority,
                    "enabled": spell.enabled,
                    "notes": spell.notes
                }
                for spell in rotation.spells
            ]
        }
        
        return json.dumps(data, indent=2 if pretty else None)

    @staticmethod
    def to_xml(rotation: Rotation, pretty: bool = True) -> str:
        """Export rotation to XML format"""
        root = ET.Element("rotation")
        
        # Add metadata
        metadata = ET.SubElement(root, "metadata")
        ET.SubElement(metadata, "name").text = rotation.metadata.name
        ET.SubElement(metadata, "class").text = rotation.metadata.class_name
        ET.SubElement(metadata, "spec").text = rotation.metadata.spec_name
        ET.SubElement(metadata, "author").text = rotation.metadata.author
        ET.SubElement(metadata, "version").text = rotation.metadata.version
        ET.SubElement(metadata, "description").text = rotation.metadata.description
        ET.SubElement(metadata, "created").text = datetime.fromtimestamp(
            rotation.metadata.created_at).isoformat()
        ET.SubElement(metadata, "modified").text = datetime.fromtimestamp(
            rotation.metadata.modified_at).isoformat()
        
        tags = ET.SubElement(metadata, "tags")
        for tag in rotation.metadata.tags:
            ET.SubElement(tags, "tag").text = tag
        
        # Add spells
        spells = ET.SubElement(root, "spells")
        for spell in rotation.spells:
            spell_elem = ET.SubElement(spells, "spell")
            ET.SubElement(spell_elem, "name").text = spell.name
            ET.SubElement(spell_elem, "condition").text = spell.condition
            ET.SubElement(spell_elem, "priority").text = str(spell.priority)
            ET.SubElement(spell_elem, "enabled").text = str(spell.enabled).lower()
            ET.SubElement(spell_elem, "notes").text = spell.notes
        
        # Convert to string
        if pretty:
            from xml.dom import minidom
            xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
            # Remove empty lines
            xml_str = '\n'.join([line for line in xml_str.split('\n') if line.strip()])
            return xml_str
        else:
            return ET.tostring(root, encoding='unicode')

    @staticmethod
    def to_lua(rotation: Rotation) -> str:
        """Export rotation to pure Lua format"""
        lines = [
            f"-- {rotation.metadata.name}",
            f"-- Author: {rotation.metadata.author}",
            f"-- Version: {rotation.metadata.version}",
            "",
            "local rotationTable = {",
            f"    name = \"{rotation.metadata.name}\",",
            f"    class = \"{rotation.metadata.class_name}\",",
            f"    spec = \"{rotation.metadata.spec_name}\",",
            "    spells = {"
        ]

        for spell in rotation.spells:
            if spell.enabled:
                lines.extend([
                    "        {",
                    f"            name = \"{spell.name}\",",
                    f"            condition = \"{spell.condition}\",",
                    f"            priority = {spell.priority},",
                    f"            notes = \"{spell.notes}\"",
                    "        },"
                ])

        lines.extend([
            "    }",
            "}",
            "",
            "return rotationTable"
        ])

        return "\n".join(lines)

class RotationImporter:
    """Handles importing rotations from different formats"""

    @staticmethod
    def from_soe(content: str) -> Rotation:
        """Import rotation from SOE Engine format"""
        try:
            # Extract spec ID
            spec_match = re.search(r'register\((\d+)', content)
            if not spec_match:
                raise ValueError("Could not find spec ID in SOE code")
            
            spec_id = int(spec_match.group(1))
            
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
            rotation = Rotation(class_name, spec_name)
            
            # Extract metadata from comments
            author_match = re.search(r'--\s*Author:\s*(.+)', content)
            if author_match:
                rotation.metadata.author = author_match.group(1).strip()
            
            version_match = re.search(r'--\s*Version:\s*(.+)', content)
            if version_match:
                rotation.metadata.version = version_match.group(1).strip()
            
            description_match = re.search(r'--\s*Description:\s*(.+)', content)
            if description_match:
                rotation.metadata.description = description_match.group(1).strip()
            
            # Extract spells
            spell_pattern = r'\{\s*"([^"]+)",\s*"([^"]+)"\s*\}'
            spell_matches = re.finditer(spell_pattern, content)
            
            for i, match in enumerate(spell_matches, 1):
                spell_name, condition = match.groups()
                rotation.add_spell(spell_name, condition, i)
            
            return rotation
            
        except Exception as e:
            raise ValueError(f"Error parsing SOE Engine code: {str(e)}")

    @staticmethod
    def from_json(content: str) -> Rotation:
        """Import rotation from JSON format"""
        try:
            data = json.loads(content)
            
            # Validate format version
            if "format_version" not in data or data["format_version"] != "1.0":
                raise ValueError("Unsupported JSON format version")
            
            # Create rotation
            rotation = Rotation(data["metadata"]["class_name"], 
                             data["metadata"]["spec_name"])
            
            # Update metadata
            rotation.metadata.name = data["metadata"]["name"]
            rotation.metadata.author = data["metadata"]["author"]
            rotation.metadata.version = data["metadata"]["version"]
            rotation.metadata.description = data["metadata"]["description"]
            rotation.metadata.created_at = data["metadata"]["created_at"]
            rotation.metadata.modified_at = data["metadata"]["modified_at"]
            rotation.metadata.tags = data["metadata"]["tags"]
            
            # Add spells
            for spell_data in data["spells"]:
                spell = rotation.add_spell(
                    spell_data["name"],
                    spell_data["condition"],
                    spell_data["priority"]
                )
                spell.enabled = spell_data["enabled"]
                spell.notes = spell_data["notes"]
            
            return rotation
            
        except Exception as e:
            raise ValueError(f"Error parsing JSON: {str(e)}")

    @staticmethod
    def from_xml(content: str) -> Rotation:
        """Import rotation from XML format"""
        try:
            root = ET.fromstring(content)
            
            # Extract metadata
            metadata = root.find("metadata")
            class_name = metadata.find("class").text
            spec_name = metadata.find("spec").text
            
            # Create rotation
            rotation = Rotation(class_name, spec_name)
            
            # Update metadata
            rotation.metadata.name = metadata.find("name").text
            rotation.metadata.author = metadata.find("author").text
            rotation.metadata.version = metadata.find("version").text
            rotation.metadata.description = metadata.find("description").text
            
            created = datetime.fromisoformat(metadata.find("created").text)
            rotation.metadata.created_at = created.timestamp()
            
            modified = datetime.fromisoformat(metadata.find("modified").text)
            rotation.metadata.modified_at = modified.timestamp()
            
            tags = metadata.find("tags")
            if tags is not None:
                rotation.metadata.tags = [tag.text for tag in tags.findall("tag")]
            
            # Add spells
            for spell_elem in root.find("spells").findall("spell"):
                spell = rotation.add_spell(
                    spell_elem.find("name").text,
                    spell_elem.find("condition").text,
                    int(spell_elem.find("priority").text)
                )
                spell.enabled = spell_elem.find("enabled").text == "true"
                notes = spell_elem.find("notes")
                if notes is not None:
                    spell.notes = notes.text
            
            return rotation
            
        except Exception as e:
            raise ValueError(f"Error parsing XML: {str(e)}")

    @staticmethod
    def from_lua(content: str) -> Rotation:
        """Import rotation from Lua format"""
        try:
            # Extract class and spec
            class_match = re.search(r'class\s*=\s*"([^"]+)"', content)
            spec_match = re.search(r'spec\s*=\s*"([^"]+)"', content)
            
            if not class_match or not spec_match:
                raise ValueError("Could not find class or spec in Lua code")
            
            class_name = class_match.group(1)
            spec_name = spec_match.group(1)
            
            # Create rotation
            rotation = Rotation(class_name, spec_name)
            
            # Extract name
            name_match = re.search(r'name\s*=\s*"([^"]+)"', content)
            if name_match:
                rotation.metadata.name = name_match.group(1)
            
            # Extract spells
            spell_pattern = r'{\s*name\s*=\s*"([^"]+)",\s*condition\s*=\s*"([^"]+)",\s*priority\s*=\s*(\d+),\s*notes\s*=\s*"([^"]*)"'
            spell_matches = re.finditer(spell_pattern, content)
            
            for match in spell_matches:
                name, condition, priority, notes = match.groups()
                spell = rotation.add_spell(name, condition, int(priority))
                spell.notes = notes
            
            return rotation
            
        except Exception as e:
            raise ValueError(f"Error parsing Lua code: {str(e)}")

class RotationConverter:
    """Handles converting between different rotation formats"""
    
    @classmethod
    def convert(cls, content: str, from_format: str, to_format: str) -> str:
        """
        Convert rotation between formats
        
        Args:
            content: The rotation content to convert
            from_format: Source format ('soe', 'json', 'xml', 'lua')
            to_format: Target format ('soe', 'json', 'xml', 'lua')
            
        Returns:
            Converted rotation content
        """
        # Import rotation
        importers = {
            'soe': RotationImporter.from_soe,
            'json': RotationImporter.from_json,
            'xml': RotationImporter.from_xml,
            'lua': RotationImporter.from_lua
        }
        
        if from_format not in importers:
            raise ValueError(f"Unsupported source format: {from_format}")
            
        rotation = importers[from_format](content)
        
        # Export rotation
        exporters = {
            'soe': RotationExporter.to_soe,
            'json': RotationExporter.to_json,
            'xml': RotationExporter.to_xml,
            'lua': RotationExporter.to_lua
        }
        
        if to_format not in exporters:
            raise ValueError(f"Unsupported target format: {to_format}")
            
        return exporters[to_format](rotation)