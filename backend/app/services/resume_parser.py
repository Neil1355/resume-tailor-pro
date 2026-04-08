"""Resume parser to extract positions and bullet points from DOCX."""
import re
from pathlib import Path

from docx import Document


class ResumeParser:
    """Parse a resume DOCX to extract job positions and their associated bullets."""

    def __init__(self):
        self.bullet_pattern = re.compile(r"^\s*(?:bullet_\d+|[-•*])\s*", re.IGNORECASE)
        # Resume-specific bullet markers: check if line starts with dash/bullet AND has meaningful content
        self.bullet_marker_pattern = re.compile(r"^[\s\t]*[-•*]\s+\S", re.IGNORECASE)

    def parse_docx(self, file_path: Path) -> dict[str, list[dict]]:
        """
        Extract positions and bullets from a DOCX file.

        Returns:
            {
              "positions": [
                {
                  "title": "Software Engineer",
                  "bullets": [
                    {"tag": "bullet_1", "text": "..."},
                    {"tag": "bullet_2", "text": "..."}
                  ]
                },
                ...
              ]
            }
        """
        doc = Document(str(file_path))
        positions = []
        current_position = None
        bullet_counter = 1

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            # Detect position headers (bold paragraph or looks like a job title)
            if self._is_position_header(para, text):
                if current_position and current_position.get("bullets"):
                    positions.append(current_position)
                current_position = {"title": text, "bullets": []}
                bullet_counter = 1  # Reset counter for new position

            # Detect bullet points (marked with bullet_N tags or common bullet markers)
            elif self._is_bullet_point(text):
                if current_position is None:
                    current_position = {"title": "Experience", "bullets": []}

                bullet_tag, bullet_text = self._extract_bullet(text, bullet_counter)
                if bullet_tag == "bullet":
                    bullet_tag = f"bullet_{bullet_counter}"
                    bullet_counter += 1

                current_position["bullets"].append({"tag": bullet_tag, "text": bullet_text})

        # Append the last position if it has bullets
        if current_position and current_position.get("bullets"):
            positions.append(current_position)

        return {"positions": positions}

    def _is_position_header(self, para, text: str) -> bool:
        """Detect if a paragraph is a position/job title header."""
        # Only treat as header if the paragraph is ENTIRELY bold and relatively short
        is_all_bold = all(run.bold for run in para.runs if run.text.strip())
        if is_all_bold and 5 <= len(text) <= 120:
            return True

        return False

    def _is_bullet_point(self, text: str) -> bool:
        """Check if text is formatted as a bullet point."""
        # Check for explicit bullet_N tags
        if re.match(r"^\s*bullet_\d+", text, re.IGNORECASE):
            return True

        # Check for actual bullet markers (dash/bullet + content, not just a single dash)
        # This prevents matching lines like "---" or single dashes used for dividers
        if self.bullet_marker_pattern.match(text):
            return True

        return False

    def _extract_bullet(self, text: str, counter: int) -> tuple[str, str]:
        """Extract bullet tag and clean text from a bullet line."""
        # Match bullet_N format
        match = re.match(r"^\s*(bullet_\d+)[\s:]+(.*)", text, re.IGNORECASE)
        if match:
            tag, content = match.groups()
            return tag.lower(), content.strip()

        # For standard bullets, strip the marker and return auto-assigned tag
        cleaned = self.bullet_pattern.sub("", text)
        return "bullet", cleaned.strip()

    def extract_bullets_by_tag(
        self, file_path: Path
    ) -> dict[str, str]:
        """Extract just bullets as a flat dict of {tag: text} for Gemini processing."""
        parsed = self.parse_docx(file_path)
        bullets_dict = {}
        bullet_counter = 1

        for position in parsed["positions"]:
            for bullet in position["bullets"]:
                tag = bullet["tag"]
                if tag == "bullet":
                    tag = f"bullet_{bullet_counter}"
                    bullet_counter += 1
                bullets_dict[tag] = bullet["text"]

        return bullets_dict
