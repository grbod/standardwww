#!/usr/bin/env python3
"""
publish_post.py — AI Blog Post Generator for Body Nutrition

Generates a blog post using Claude API, writes it as a markdown file,
and commits/pushes to Git so Netlify auto-rebuilds the site.

Usage:
    python scripts/publish_post.py "Organic Rice Protein" --category "Plant Protein"
    python scripts/publish_post.py "Ashwagandha KSM-66" --category "Functional"

Automate with cron:
    # Publish a new post every weekday at 6 AM
    0 6 * * 1-5 cd /path/to/body-nutrition && python scripts/publish_post.py --auto

Requirements:
    pip install anthropic python-slugify

Environment variables:
    ANTHROPIC_API_KEY=sk-ant-...
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("Install anthropic: pip install anthropic")
    sys.exit(1)

try:
    from slugify import slugify
except ImportError:
    # Simple fallback if python-slugify not installed
    def slugify(text):
        return text.lower().replace(' ', '-').replace(':', '').replace("'", "")


# ---- Config ----
CONTENT_DIR = Path(__file__).parent.parent / "src" / "content" / "blog"
MODEL = "claude-sonnet-4-5-20250514"

# Topics the AI can write about (used in --auto mode)
AUTO_TOPICS = [
    ("Collagen Peptides Types I & III", "Protein", "🧬"),
    ("Organic Brown Rice Protein", "Plant Protein", "🌾"),
    ("Ashwagandha KSM-66 for Supplements", "Functional", "🧪"),
    ("MCT Oil Powder in Protein Formulations", "Functional", "🥥"),
    ("Sunflower Lecithin as an Instantizing Agent", "Processing", "🌻"),
    ("Probiotics in Powder Supplements: Stability Challenges", "Functional", "🦠"),
    ("Natural vs Artificial Flavoring in Protein Powders", "Flavoring", "🍦"),
    ("Creatine Monohydrate: Sourcing and Quality", "Sports Nutrition", "💪"),
    ("Vitamin D3 in Supplement Capsules", "Vitamins", "☀️"),
    ("Turmeric Curcumin Extract: Bioavailability Solutions", "Functional", "🟡"),
    ("Hemp Protein: Nutrition and Formulation Guide", "Plant Protein", "🌿"),
    ("Digestive Enzymes in Protein Powders", "Functional", "⚡"),
    ("Grass-Fed Whey Isolate vs Concentrate", "Dairy Protein", "🥛"),
    ("Beetroot Powder in Pre-Workout Formulations", "Sports Nutrition", "🔴"),
    ("Citric Acid and pH Management in Powder Blends", "Processing", "🧪"),
]

SYSTEM_PROMPT = """You are a senior formulation scientist and ingredient specialist at Body Nutrition,
a contract manufacturer of dietary supplements in St. Petersburg, FL.

Write a blog post for our Ingredients Blog aimed at brand owners, formulators, and product
developers evaluating ingredients for their supplement products.

The tone is professional, authoritative, and practical — like a knowledgeable colleague
sharing real-world manufacturing experience. Avoid marketing fluff.

Include:
- What the ingredient is and why it matters
- Sourcing considerations (origin, quality markers, pricing context)
- Formulation tips from a manufacturing perspective
- Regulatory/labeling notes (FDA, Prop 65, GRAS status where relevant)
- A clear bottom-line recommendation

Write 600-900 words. Use markdown formatting with ## headers, bullet points where helpful,
and one blockquote with a key insight. Do NOT include a title — that's provided separately."""


def generate_post(topic: str, category: str) -> dict:
    """Call Claude API to generate a blog post."""
    client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

    # Generate the article body
    body_response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Write a blog post about: {topic}"}],
    )
    body = body_response.content[0].text

    # Generate metadata (title, excerpt, emoji)
    meta_response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": f"""Given this blog post about "{topic}", generate:
1. A compelling SEO-friendly title (60-70 chars)
2. A concise excerpt/meta description (120-155 chars)
3. A single emoji that represents the topic

Respond in JSON format only:
{{"title": "...", "excerpt": "...", "emoji": "..."}}

Blog post:
{body[:500]}...""",
            }
        ],
    )

    meta_text = meta_response.content[0].text.strip()
    # Strip markdown code fences if present
    meta_text = meta_text.replace("```json", "").replace("```", "").strip()
    meta = json.loads(meta_text)

    return {
        "title": meta["title"],
        "excerpt": meta["excerpt"],
        "emoji": meta.get("emoji", "📄"),
        "category": category,
        "body": body,
    }


def write_markdown(post: dict) -> Path:
    """Write the post as a markdown file."""
    slug = slugify(post["title"])
    date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{slug}.md"
    filepath = CONTENT_DIR / filename

    frontmatter = f"""---
title: "{post['title']}"
slug: "{slug}"
category: "{post['category']}"
emoji: "{post['emoji']}"
excerpt: "{post['excerpt']}"
date: "{date}"
---"""

    content = f"{frontmatter}\n\n{post['body']}\n"
    filepath.write_text(content, encoding="utf-8")

    return filepath


def git_push(filepath: Path):
    """Stage, commit, and push the new post."""
    try:
        subprocess.run(["git", "add", str(filepath)], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"New post: {filepath.stem}"],
            check=True,
        )
        subprocess.run(["git", "push"], check=True)
        print(f"✅ Pushed to git — Netlify will rebuild automatically")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Git push failed: {e}")
        print("   File was created locally. Push manually when ready.")


def pick_auto_topic() -> tuple:
    """Pick a topic that hasn't been published yet."""
    existing = {f.stem for f in CONTENT_DIR.glob("*.md")}

    for topic, category, emoji in AUTO_TOPICS:
        slug = slugify(topic)
        if slug not in existing:
            return topic, category, emoji

    # All topics used — you should add more to AUTO_TOPICS
    print("⚠️  All auto topics have been published. Add more to AUTO_TOPICS.")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Generate and publish a blog post")
    parser.add_argument("topic", nargs="?", help="Ingredient or topic to write about")
    parser.add_argument("--category", default="Ingredients", help="Post category")
    parser.add_argument("--emoji", default=None, help="Emoji for the post card")
    parser.add_argument("--auto", action="store_true", help="Auto-pick next topic")
    parser.add_argument("--no-push", action="store_true", help="Skip git push")
    parser.add_argument("--dry-run", action="store_true", help="Print post but don't save")

    args = parser.parse_args()

    if args.auto:
        topic, category, emoji = pick_auto_topic()
        print(f"📝 Auto-selected topic: {topic} [{category}]")
    elif args.topic:
        topic = args.topic
        category = args.category
        emoji = args.emoji
    else:
        parser.print_help()
        sys.exit(1)

    # Generate
    print(f"🤖 Generating post about: {topic}")
    post = generate_post(topic, category)
    if emoji:
        post["emoji"] = emoji

    print(f"📰 Title: {post['title']}")
    print(f"📝 Excerpt: {post['excerpt']}")

    if args.dry_run:
        print("\n--- DRY RUN — Post content: ---\n")
        print(post["body"])
        return

    # Write
    filepath = write_markdown(post)
    print(f"💾 Saved: {filepath}")

    # Push
    if not args.no_push:
        git_push(filepath)
    else:
        print("⏭️  Skipped git push (--no-push)")


if __name__ == "__main__":
    main()
