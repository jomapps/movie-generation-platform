"""
Character Validation Service

Validates story arc content against character roster to ensure no new characters
are introduced and provides continuity flag generation.
"""

import re
from typing import List, Set, Dict, Any, Optional, Tuple
import structlog

from ..config import get_config
from ..models.story_models import (
    Character,
    StoryArc,
    ContinuityFlag,
    ContinuityFlagCode,
    ContinuitySeverity
)


logger = structlog.get_logger(__name__)


class CharacterValidationService:
    """Service for validating character references in story arcs"""
    
    def __init__(self):
        self.config = get_config()
        self._character_cache: Dict[str, List[Character]] = {}
    
    async def validate_story_arc(
        self,
        story_arc: StoryArc,
        character_roster: List[Character],
        project_id: Optional[str] = None
    ) -> Tuple[List[ContinuityFlag], Set[str], Set[str]]:
        """
        Validate story arc against character roster
        
        Args:
            story_arc: Story arc to validate
            character_roster: Available characters for the story
            project_id: Optional project ID for context
            
        Returns:
            Tuple of (continuity_flags, found_characters, unknown_characters)
        """
        continuity_flags = []
        
        # Extract character names from roster
        roster_names = {char.name.lower().strip() for char in character_roster}
        roster_lookup = {char.name.lower().strip(): char.name for char in character_roster}
        
        logger.info(
            "Starting character validation",
            roster_size=len(character_roster),
            project_id=project_id
        )
        
        # Extract character references from story arc text
        story_text = f"{story_arc.setup} {story_arc.escalation} {story_arc.resolution}"
        referenced_characters = self._extract_character_references(story_text)
        
        logger.debug(
            "Extracted character references",
            referenced_count=len(referenced_characters),
            references=list(referenced_characters)
        )
        
        # Validate each referenced character
        found_characters = set()
        unknown_characters = set()
        
        for ref_name in referenced_characters:
            ref_lower = ref_name.lower().strip()
            
            if ref_lower in roster_names:
                # Character found in roster
                actual_name = roster_lookup[ref_lower]
                found_characters.add(actual_name)
                
                logger.debug(
                    "Character validated",
                    referenced=ref_name,
                    roster_name=actual_name
                )
            else:
                # Character not found in roster
                unknown_characters.add(ref_name)
                
                # Create continuity flag
                flag = ContinuityFlag(
                    code=ContinuityFlagCode.CHARACTER_NOT_FOUND,
                    message=f"Story references character '{ref_name}' not found in roster",
                    severity=ContinuitySeverity.ERROR if self.config.strict_character_validation else ContinuitySeverity.WARNING,
                    context={
                        "referenced_character": ref_name,
                        "available_characters": [char.name for char in character_roster],
                        "project_id": project_id
                    }
                )
                continuity_flags.append(flag)
                
                logger.warning(
                    "Character not found in roster",
                    referenced_character=ref_name,
                    roster_size=len(character_roster)
                )
        
        # Additional validations
        additional_flags = self._perform_additional_validations(
            story_arc, character_roster, found_characters
        )
        continuity_flags.extend(additional_flags)
        
        logger.info(
            "Character validation complete",
            found_characters=len(found_characters),
            unknown_characters=len(unknown_characters),
            continuity_flags=len(continuity_flags)
        )
        
        return continuity_flags, found_characters, unknown_characters
    
    def _extract_character_references(self, text: str) -> Set[str]:
        """Extract potential character references from story text"""
        
        # Common patterns for character references
        patterns = [
            # Direct name references (capitalized words that could be names)
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
            # Possessive forms (Name's)
            r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'s\b",
            # Quoted references ("Name said...")
            r'"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"',
            # Character action patterns (Name walks, Name runs, etc.)
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:walks|runs|says|thinks|feels|looks|turns|moves|stops|starts|goes|comes|sees|hears|speaks|whispers|shouts|cries|laughs|smiles|frowns)'
        ]
        
        references = set()
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                # Get the captured group if it exists, otherwise the full match
                name = match.group(1) if match.groups() else match.group(0)
                name = name.strip()
                
                # Filter out common non-character words
                if self._is_likely_character_name(name):
                    references.add(name)
        
        return references
    
    def _is_likely_character_name(self, text: str) -> bool:
        """Determine if text is likely a character name"""
        
        # Filter out common non-character words
        excluded_words = {
            'The', 'A', 'An', 'And', 'Or', 'But', 'In', 'On', 'At', 'To', 'For',
            'With', 'By', 'From', 'About', 'Into', 'Through', 'During', 'Before',
            'After', 'Above', 'Below', 'Up', 'Down', 'Out', 'Off', 'Over', 'Under',
            'Again', 'Further', 'Then', 'Once', 'Here', 'There', 'When', 'Where',
            'Why', 'How', 'All', 'Any', 'Both', 'Each', 'Few', 'More', 'Most',
            'Other', 'Some', 'Such', 'No', 'Nor', 'Not', 'Only', 'Own', 'Same',
            'So', 'Than', 'Too', 'Very', 'Can', 'Will', 'Just', 'Should', 'Now',
            'Day', 'Night', 'Morning', 'Evening', 'Today', 'Tomorrow', 'Yesterday',
            'World', 'Life', 'Time', 'Work', 'Home', 'School', 'City', 'Country'
        }
        
        # Single word check
        words = text.split()
        if len(words) == 1 and words[0] in excluded_words:
            return False
        
        # Length checks
        if len(text) < 2 or len(text) > 50:
            return False
        
        # Must start with capital letter
        if not text[0].isupper():
            return False
        
        # Should not contain numbers or special characters (except spaces and hyphens)
        if not re.match(r'^[A-Za-z\s\-\'\.]+$', text):
            return False
        
        # Should not be all uppercase (likely an acronym or emphasis)
        if text.isupper() and len(text) > 3:
            return False
        
        return True
    
    def _perform_additional_validations(
        self,
        story_arc: StoryArc,
        character_roster: List[Character],
        found_characters: Set[str]
    ) -> List[ContinuityFlag]:
        """Perform additional character-related validations"""
        
        flags = []
        
        # Check if story uses no characters at all
        if not found_characters:
            flags.append(ContinuityFlag(
                code=ContinuityFlagCode.CHARACTER_NOT_FOUND,
                message="Story arc does not reference any characters from the roster",
                severity=ContinuitySeverity.WARNING,
                context={
                    "available_characters": [char.name for char in character_roster],
                    "story_has_character_references": len(self._extract_character_references(
                        f"{story_arc.setup} {story_arc.escalation} {story_arc.resolution}"
                    )) > 0
                }
            ))
        
        # Check for protagonist/antagonist balance
        protagonist_chars = [char for char in character_roster if char.role and 'protagonist' in char.role.lower()]
        antagonist_chars = [char for char in character_roster if char.role and 'antagonist' in char.role.lower()]
        
        protagonist_used = any(char.name in found_characters for char in protagonist_chars)
        antagonist_used = any(char.name in found_characters for char in antagonist_chars)
        
        if protagonist_chars and not protagonist_used:
            flags.append(ContinuityFlag(
                code=ContinuityFlagCode.CONFLICT_DRIFT,
                message="Story does not use any protagonist characters despite conflict focus",
                severity=ContinuitySeverity.INFO,
                context={
                    "available_protagonists": [char.name for char in protagonist_chars],
                    "characters_used": list(found_characters)
                }
            ))
        
        if len(found_characters) > 3:
            flags.append(ContinuityFlag(
                code=ContinuityFlagCode.RUNTIME_FEASIBILITY_RISK,
                message=f"Story references {len(found_characters)} characters, may be complex for short format",
                severity=ContinuitySeverity.WARNING,
                context={
                    "character_count": len(found_characters),
                    "characters_used": list(found_characters)
                }
            ))
        
        return flags
    
    def get_character_suggestions(
        self,
        story_context: str,
        character_roster: List[Character],
        max_suggestions: int = 3
    ) -> List[Character]:
        """Get character suggestions based on story context and available roster"""
        
        if not character_roster:
            return []
        
        # Simple scoring based on role and description matching
        scored_characters = []
        
        context_lower = story_context.lower()
        keywords = set(re.findall(r'\b\w+\b', context_lower))
        
        for character in character_roster:
            score = 0
            
            # Score based on role match
            if character.role:
                role_words = set(re.findall(r'\b\w+\b', character.role.lower()))
                score += len(keywords.intersection(role_words)) * 3
            
            # Score based on description match
            if character.description:
                desc_words = set(re.findall(r'\b\w+\b', character.description.lower()))
                score += len(keywords.intersection(desc_words)) * 2
            
            # Prefer protagonist/main characters
            if character.role and 'protagonist' in character.role.lower():
                score += 5
            elif character.role and 'main' in character.role.lower():
                score += 3
            
            scored_characters.append((score, character))
        
        # Sort by score and return top suggestions
        scored_characters.sort(reverse=True, key=lambda x: x[0])
        return [char for score, char in scored_characters[:max_suggestions] if score > 0]
    
    def validate_character_consistency(
        self,
        story_arc: StoryArc,
        character_roster: List[Character]
    ) -> List[ContinuityFlag]:
        """Validate character usage consistency across story arc sections"""
        
        flags = []
        
        # Extract characters from each section
        setup_chars = self._extract_character_references(story_arc.setup)
        escalation_chars = self._extract_character_references(story_arc.escalation)
        resolution_chars = self._extract_character_references(story_arc.resolution)
        
        # Check for characters that appear only in one section
        all_chars = setup_chars | escalation_chars | resolution_chars
        
        for char in all_chars:
            sections = []
            if char in setup_chars:
                sections.append("setup")
            if char in escalation_chars:
                sections.append("escalation")  
            if char in resolution_chars:
                sections.append("resolution")
            
            if len(sections) == 1:
                flags.append(ContinuityFlag(
                    code=ContinuityFlagCode.PACING_ISSUE,
                    message=f"Character '{char}' only appears in {sections[0]} section",
                    severity=ContinuitySeverity.INFO,
                    context={
                        "character": char,
                        "sections": sections,
                        "suggestion": "Consider character continuity across story arc"
                    }
                ))
        
        return flags