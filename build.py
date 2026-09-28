#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
JSON_FILE = ROOT / "resources.json"
TEMPLATE_FILE = ROOT / "template.html"
OUTPUT_FILE = ROOT / "index.html"
PLACEHOLDER = "{{RESOURCE_SECTIONS}}"


def render_section(section_index: int, title: str, items: list[dict[str, Any]]) -> str:
    list_items = []
    for item in items:
        description = item["description"]
        description_markup = (
            f'              <span class="meta">{html.escape(description)}</span>\n'
            if description
            else ""
        )
        list_items.append(
            '            <li class="resource-item">\n'
            f"              <a href=\"{html.escape(item['url'], quote=True)}\" target=\"_blank\" rel=\"noreferrer\">{html.escape(item['title'])}</a>\n"
            f"{description_markup}"
            "            </li>"
        )
    list_items = "\n".join(list_items)

    return (
        '        <section class="panel">\n'
        '          <div class="section-heading">\n'
        f'            <span class="heading-tag">[{section_index:02d}]</span>\n'
        f"            <h2>{html.escape(title)}</h2>\n"
        "          </div>\n\n"
        '          <ul class="resource-list">\n'
        f"{list_items}\n"
        "          </ul>\n"
        "        </section>\n"
    )


def load_data_from_json() -> dict[str, Any]:
    data = json.loads(JSON_FILE.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("categories"), list):
        raise ValueError("resources.json must contain a 'categories' list")
    return data


def build_sections(data: dict[str, Any]) -> str:
    categories = data["categories"]

    sections = []
    for index, category in enumerate(categories, start=1):
        if not isinstance(category, dict):
            raise ValueError("Each category must be a JSON object")

        title = category.get("title")
        links = category.get("links")
        if not isinstance(title, str) or not isinstance(links, list):
            raise ValueError("Each category must contain 'title' and 'links'")

        normalized_links = []
        for link in links:
            if not isinstance(link, dict):
                raise ValueError("Each link must be a JSON object")

            url = link.get("url")
            link_title = link.get("title")
            description = link.get("description", "")
            if (
                not isinstance(url, str)
                or not isinstance(link_title, str)
                or not isinstance(description, str)
            ):
                raise ValueError(
                    "Each link must contain 'url', 'title', and 'description'"
                )

            normalized_links.append(
                {"url": url, "title": link_title, "description": description}
            )

        sections.append(render_section(index, title, normalized_links))

    return "".join(sections)


def build_html() -> str:
    if not TEMPLATE_FILE.exists():
        raise FileNotFoundError(f"Missing template: {TEMPLATE_FILE}")

    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    data = load_data_from_json()
    return template.replace(PLACEHOLDER, build_sections(data))


def main() -> None:
    if not JSON_FILE.exists():
        raise FileNotFoundError(f"Missing resource list: {JSON_FILE}")

    OUTPUT_FILE.write_text(build_html(), encoding="utf-8")
    print(
        f"Generated {OUTPUT_FILE.relative_to(ROOT)} from {TEMPLATE_FILE.relative_to(ROOT)} and {JSON_FILE.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
