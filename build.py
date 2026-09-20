#!/usr/bin/env python3
from __future__ import annotations

import configparser
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INI_FILE = ROOT / "resources.ini"
TEMPLATE_FILE = ROOT / "template.html"
OUTPUT_FILE = ROOT / "index.html"
PLACEHOLDER = "{{RESOURCE_SECTIONS}}"


def parse_value(value: str) -> tuple[str, str]:
    if " | " in value:
        url, meta = value.split(" | ", 1)
        return url.strip(), meta.strip()
    return value.strip(), ""


def render_section(section_index: int, title: str, items: list[tuple[str, str, str]]) -> str:
    list_items = "\n".join(
        (
            "            <li class=\"resource-item\">\n"
            f"              <a href=\"{html.escape(url, quote=True)}\" target=\"_blank\" rel=\"noreferrer\">{html.escape(label)}</a>\n"
            f"              {f'<span class=\"meta\">{html.escape(meta)}</span>' if meta else ''}\n"
            "            </li>"
        )
        for label, url, meta in items
    )

    return (
        "        <section class=\"panel\">\n"
        "          <div class=\"section-heading\">\n"
        f"            <span class=\"heading-tag\">[{section_index:02d}]</span>\n"
        f"            <h2>{html.escape(title)}</h2>\n"
        "          </div>\n\n"
        "          <ul class=\"resource-list\">\n"
        f"{list_items}\n"
        "          </ul>\n"
        "        </section>\n"
    )


def build_sections() -> str:
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(INI_FILE, encoding="utf-8")

    sections = []
    for index, section in enumerate(parser.sections(), start=1):
        items = []
        for label, value in parser.items(section):
            url, meta = parse_value(value)
            items.append((label, url, meta))
        sections.append(render_section(index, section, items))

    return "".join(sections)


def build_html() -> str:
    if not TEMPLATE_FILE.exists():
        raise FileNotFoundError(f"Missing template: {TEMPLATE_FILE}")

    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    return template.replace(PLACEHOLDER, build_sections())


def main() -> None:
    if not INI_FILE.exists():
        raise FileNotFoundError(f"Missing resource list: {INI_FILE}")

    OUTPUT_FILE.write_text(build_html(), encoding="utf-8")
    print(f"Generated {OUTPUT_FILE.relative_to(ROOT)} from {TEMPLATE_FILE.relative_to(ROOT)} and {INI_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
