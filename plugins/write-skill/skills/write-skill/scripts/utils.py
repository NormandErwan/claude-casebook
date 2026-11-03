"""Shared utilities for write-skill evaluation scripts."""

from pathlib import Path



def parse_skill_md(skill_path: Path) -> tuple[str, str, str]:
    """Parse a SKILL.md file, returning (name, description, full_content)."""
    content = (skill_path / "SKILL.md").read_text()
    lines = content.split("\n")

    if lines[0].strip() != "---":
        raise ValueError("SKILL.md missing frontmatter (no opening ---)")

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        raise ValueError("SKILL.md missing frontmatter (no closing ---)")

    name = ""
    description = ""
    frontmatter_lines = lines[1:end_idx]
    i = 0
    while i < len(frontmatter_lines):
        line = frontmatter_lines[i]
        if line.startswith("name:"):
            name = line[len("name:"):].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            value = line[len("description:"):].strip()
            # A YAML block indicator (>, |, >-, |-) holds no text itself; a plain or
            # quoted scalar may also continue on indented lines.
            parts = [] if value in (">", "|", ">-", "|-") else [value]
            i += 1
            while i < len(frontmatter_lines) and (frontmatter_lines[i].startswith("  ") or frontmatter_lines[i].startswith("\t")):
                parts.append(frontmatter_lines[i].strip())
                i += 1
            description = " ".join(p for p in parts if p)
            if len(description) >= 2 and description[0] == description[-1] and description[0] in "\"'":
                description = description[1:-1]
            continue
        i += 1

    return name, description, content
