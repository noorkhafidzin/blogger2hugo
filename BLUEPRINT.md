# Blogger2Hugo Blueprint

**Version:** v1.0.1  
**Last Updated:** 2026-06-29
**Language:** Python 3  
**License:** MIT

## Overview

Blogger2Hugo is a command-line tool that converts Blogger backup files (Atom XML) into Hugo-compatible Markdown posts with images, SEO-friendly redirects, and proper frontmatter.

## Architecture

### Core Components

#### 1. **Utility Layer** (`safe_mkdir`, `extract_text`, `download_file`)
- **safe_mkdir**: Creates directories with collision detection
- **extract_text**: Safely extracts XML text with namespace support and default fallbacks
- **download_file**: Concurrent-safe file downloading with error handling

#### 2. **HTML Conversion Engine**

##### Tables (`has_complex_table`, `row_to_text_cells`, `table_to_markdown`, `convert_tables`)
- Detects colspan/rowspan complexity
- Converts simple tables to Markdown pipes
- Preserves complex tables as HTML inline

##### Links (`convert_links`)
- Converts HTML `<a>` tags to Markdown links
- Preserves href and text content

##### Media & Cleanup (`clean_html`, `html_to_markdown`, `sanitize_filename`)
- Strips Blogger-specific attributes and styling
- Downloads images to local directory with SHA256-based filenames
- Converts HTML to Markdown via markdownify library
- Sanitizes filenames: spaces/underscores → dashes, special chars → removed, duplicates → collapsed

#### 3. **Frontmatter Generation** (`frontmatter`)
- YAML format with escaped quotes
- Fields: title, date, updated, tags, permalink, draft status
- Compatible with Hugo's default config

#### 4. **Main Conversion Pipeline** (`convert_atom`)
- Parses Atom XML with namespace support
- Iterates over entries, filters non-POST types
- Extracts metadata: title, published, updated, status, tags
- Fallback permalink generation from title or post ID
- Creates post directory structure: `posts/{slug}/index.md` + `posts/{slug}/images/`
- Processes HTML → Markdown conversion
- Writes frontmatter + markdown content
- Tracks and reports posted vs. draft counts

### Data Flow

```
Blogger .atom file
    ↓
[XML parsing with namespaces]
    ↓
[For each entry]
    ├─ Extract metadata (title, date, status, tags)
    ├─ Generate slug from permalink/title/ID
    ├─ Download images → posts/{slug}/images/
    ├─ Convert HTML tables → Markdown/HTML
    ├─ Convert links → Markdown
    ├─ Convert images → Markdown
    ├─ Clean unsupported HTML
    ├─ Generate frontmatter (YAML)
    └─ Write index.md
    ↓
[Final summary report]
```

### Key Design Decisions

1. **Namespace-aware XML parsing**: Handles both `atom:` and `blogger:` namespaces correctly
2. **Two-pass cleanup**: Converts specific elements (tables, links, images) before general HTML-to-Markdown
3. **Deterministic image filenames**: SHA256 hashing ensures stable, reproducible builds
4. **Slug generation fallback chain**: permalink → title → post ID for robustness
5. **Upfront directory creation**: Avoids misplacement bugs by creating both post and image dirs before processing
6. **Narrow exception handling**: Specific catches in download and markdown conversion for better debugging

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| trafilatura | 1.8.0 | HTML extraction and cleaning |
| markdownify | 0.11.6 | HTML to Markdown conversion |
| beautifulsoup4 | 4.12.3 | HTML parsing and manipulation |
| requests | 2.32.3 | HTTP file downloads |

## Feature Modules

### URL Conversion
- **Blogger format**: `/2020/06/my-post.html`
- **Hugo format**: `/posts/my-post/`
- **Redirect aliases**: Maintains old URLs in frontmatter for SEO

### Image Handling
- Downloads all images from Blogger posts
- Stores locally in `{post}/images/` directory
- Generates stable filenames using SHA256 hash of download URL
- Updates image src to local paths in Markdown

### Draft Support
- Distinguishes published (false) vs. draft (true) in frontmatter
- Allows Hugo to filter drafts in build config

### Tag Preservation
- Extracts Blogger categories as tags
- Stores in YAML array format for Hugo compatibility
## Limitations & Future Work

### Current Limitations
- Complex HTML tables (colspan/rowspan) not fully supported
- Blogger theme-specific HTML elements not converted
- No embedded widget or JavaScript support
- ~~Windows lxml dependency issues~~ (resolved v1.0.1 — lxml 5.x ships pre-built wheels)

### Potential Enhancements
- Parallel post processing for large exports
- Custom HTML template support
- Blogger comment migration
- Automatic SEO metadata optimization
- Incremental updates (skip already-converted posts)

## Installation & Usage

```bash
pip install -r requirements.txt
python blogger2hugo.py [file.atom] [output_dir]
```

**Arguments:**
- `file.atom`: Blogger export from Google Takeout (required)
- `output_dir`: Target directory for Hugo content (default: `content/`)

**Output:**
- `content/posts/{slug}/index.md` — Post with frontmatter + Markdown
- `content/posts/{slug}/images/*.{jpg|png|gif}` — Downloaded post images

## Testing & Verification

Current validation method: Manual testing with sample Blogger exports. Future work should include:
- Unit tests for HTML conversion edge cases
- E2E tests with real Blogger exports
- Regression tests for image download stability
- Windows/Docker environment validation

## Platform Verification

**Windows 11 Pro, Python 3.11** (2026-06-29):
- ✅ All dependencies install from pre-built wheels (lxml 5.4.0)
- ✅ Full end-to-end conversion: 3 published + 1 draft posts processed
- ✅ HTML element conversion: tables, links, images, bold/italic all working
- ✅ Filename sanitization: special chars, underscores, quotes handled correctly
- ✅ Draft flag, tags, and frontmatter YAML format verified
- ✅ Fallback permalink generation (when link element missing) working

**Conclusion**: Project is fully functional on Windows. Docker not required.
