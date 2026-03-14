# Body Nutrition — Corporate Site + AI Blog

Astro static site with automated AI blog publishing. Deploys to Netlify.

## Project Structure

```
body-nutrition/
├── src/
│   ├── pages/
│   │   ├── index.astro          ← Homepage
│   │   ├── capabilities.astro   ← Services/capabilities
│   │   ├── contact.astro        ← Contact form
│   │   └── blog/
│   │       ├── index.astro      ← Blog grid (auto-lists all .md files)
│   │       └── [slug].astro     ← Individual post template
│   │
│   ├── layouts/
│   │   ├── BaseLayout.astro     ← HTML head, Header, Footer wrapper
│   │   └── BlogPostLayout.astro ← Blog post template (hero + content + sidebar)
│   │
│   ├── components/
│   │   ├── Header.astro         ← Nav bar
│   │   ├── Footer.astro         ← Site footer
│   │   └── BlogCard.astro       ← Blog grid card
│   │
│   ├── content/
│   │   └── blog/                ← MARKDOWN FILES GO HERE (AI-generated)
│   │       ├── pea-protein-isolate-guide.md
│   │       ├── alkalized-vs-natural-cocoa.md
│   │       └── monk-fruit-vs-stevia.md
│   │
│   └── styles/
│       └── global.css           ← Site-wide styles
│
├── scripts/
│   └── publish_post.py          ← AI blog post generator
│
├── public/                      ← Static assets (images, favicon)
├── astro.config.mjs
├── netlify.toml
└── package.json
```

## Quick Start

```bash
# Install dependencies
npm install

# Run dev server
npm run dev
# → opens at http://localhost:4321

# Build for production
npm run build

# Preview production build
npm run preview
```

## Deploy to Netlify

1. Push this repo to GitHub
2. Go to [app.netlify.com](https://app.netlify.com)
3. Click "Add new site" → "Import an existing project"
4. Connect your GitHub repo
5. Netlify auto-detects Astro — build command and publish dir are in `netlify.toml`
6. Click "Deploy"

Every `git push` triggers an automatic rebuild.

## AI Blog Publishing

### Manual — write about a specific ingredient:

```bash
export ANTHROPIC_API_KEY=sk-ant-...

# Generate and publish
python scripts/publish_post.py "Organic Rice Protein" --category "Plant Protein"

# Preview without saving
python scripts/publish_post.py "Ashwagandha KSM-66" --category "Functional" --dry-run

# Generate but don't git push
python scripts/publish_post.py "MCT Oil Powder" --category "Functional" --no-push
```

### Automatic — let it pick the next topic:

```bash
python scripts/publish_post.py --auto
```

This picks from the `AUTO_TOPICS` list in the script, skipping any already published.

### Cron — publish daily:

```bash
# Add to crontab (crontab -e)
# Publish a new post every weekday at 6 AM
0 6 * * 1-5 cd /path/to/body-nutrition && ANTHROPIC_API_KEY=sk-ant-... python scripts/publish_post.py --auto
```

Or use a Render.com cron job, GitHub Actions, or any scheduler.

### How it works:

1. Script calls Claude API to generate article + metadata
2. Writes a `.md` file to `src/content/blog/`
3. Commits and pushes to Git
4. Netlify detects the push and rebuilds the site (~10 seconds)
5. New post is live with full styling, sidebar, SEO meta tags

## Adding a New Page

1. Create a `.astro` file in `src/pages/`
2. Import and wrap with `BaseLayout`
3. Add a nav link in `Header.astro`

## Editing Corporate Pages

Corporate pages (home, capabilities, contact) are static Astro files.
Edit the content directly in the `.astro` files and push to git.

## Customization

- **Colors/fonts**: Edit CSS variables in `src/styles/global.css`
- **Nav links**: Edit `src/components/Header.astro`
- **Footer**: Edit `src/components/Footer.astro`
- **Blog post layout**: Edit `src/layouts/BlogPostLayout.astro`
- **Homepage sections**: Edit `src/pages/index.astro`

## Adding Images

1. Put images in `public/images/`
2. Reference in markdown: `![Alt text](/images/filename.jpg)`
3. Or in Astro components: `<img src="/images/filename.jpg" alt="..." />`

For the corporate pages, replace the emoji placeholders with actual facility/product photos.
