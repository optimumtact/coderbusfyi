#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
JSON_FILE = ROOT / "resources.json"
TEMPLATE_FILE = ROOT / "template.html"
OUTPUT_FILE = ROOT / "index.html"
RESOURCE_PLACEHOLDER = "{{RESOURCE_SECTIONS}}"
JSON_LD_PLACEHOLDER = "{{JSON_LD}}"


def slugify_anchor(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "section"


def render_section(section_index: int, title: str, items: list[dict[str, Any]]) -> str:
    list_items = []
    section_id = slugify_anchor(title)
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
        f'        <section class="panel" id="{html.escape(section_id, quote=True)}">\n'
        '          <div class="section-heading">\n'
        f'            <a class="heading-tag section-anchor" href="#{html.escape(section_id, quote=True)}" aria-label="Permanent link to {html.escape(title, quote=True)}">[{section_index:02d}]</a>\n'
        f'            <h2 id="{html.escape(section_id, quote=True)}"><a class="section-title-anchor" href="#{html.escape(section_id, quote=True)}" aria-label="Permanent link to {html.escape(title, quote=True)}">{html.escape(title)}</a></h2>\n'
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


def build_structured_data(data: dict[str, Any]) -> str:
    item_list = []
    for index, category in enumerate(data["categories"], start=1):
        links = []
        for link_index, link in enumerate(category["links"], start=1):
            links.append(
                {
                    "@type": "ListItem",
                    "position": link_index,
                    "name": link["title"],
                    "url": link["url"],
                    "description": link["description"],
                }
            )

        item_list.append(
            {
                "@type": "ListItem",
                "position": index,
                "name": category["title"],
                "itemListElement": links,
            }
        )

    structured_data = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Coder // Bus",
        "description": "Curated DM, BYOND, and SS13 references, learning resources, tooling, and infrastructure links.",
        "url": "https://coderbus.fyi/",
        "inLanguage": "en",
        "isPartOf": {
            "@type": "WebSite",
            "name": "Coder // Bus",
            "url": "https://coderbus.fyi/",
        },
        "publisher": {
            "@type": "Organization",
            "name": "Coder // Bus",
            "url": "https://coderbus.fyi/",
        },
        "mainEntity": {
            "@type": "ItemList",
            "name": "Resource categories",
            "itemListElement": item_list,
        },
    }

    return (
        '<script type="application/ld+json">\n'
        f"{json.dumps(structured_data, ensure_ascii=False)}\n"
        "</script>"
    )


def build_html() -> str:
    if not TEMPLATE_FILE.exists():
        raise FileNotFoundError(f"Missing template: {TEMPLATE_FILE}")

    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    data = load_data_from_json()
    html_output = template.replace(RESOURCE_PLACEHOLDER, build_sections(data))
    return html_output.replace(JSON_LD_PLACEHOLDER, build_structured_data(data))


def main() -> None:
    if not JSON_FILE.exists():
        raise FileNotFoundError(f"Missing resource list: {JSON_FILE}")

    OUTPUT_FILE.write_text(build_html(), encoding="utf-8")
    print(
        f"Generated {OUTPUT_FILE.relative_to(ROOT)} from {TEMPLATE_FILE.relative_to(ROOT)} and {JSON_FILE.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
