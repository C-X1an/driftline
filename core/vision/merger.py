def merge_vision_sections(original: str, sections: dict) -> str:
    core_md = sections.get("core_capabilities_markdown", "").strip()
    guarantees_md = sections.get("guarantees_markdown", "").strip()

    lines = original.splitlines(keepends=True)

    def find_section_bounds(header: str):
        start = None
        end = None

        for i, line in enumerate(lines):
            if line.strip() == f"## {header}":
                start = i
                break

        if start is None:
            return None, None

        for j in range(start + 1, len(lines)):
            stripped = lines[j].strip()
            if stripped.startswith("## ") or stripped == "---":
                end = j
                break

        if end is None:
            end = len(lines)

        return start, end

    def replace_section(header: str, new_body: str):
        start, end = find_section_bounds(header)
        if start is None:
            return

        new_section = [f"## {header}\n", "\n"]

        if new_body:
            new_section.append(new_body.strip() + "\n")

        new_section.append("\n")

        lines[start:end] = new_section

    replace_section("Core Capabilities", core_md)
    replace_section("Guarantees", guarantees_md)

    return "".join(lines)