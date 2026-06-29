# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.0.1] - 2026-06-29

### Changed
- Updated documentation: removed obsolete Windows installation warning. lxml 5.x now ships pre-built wheels for Windows—no compilation required. Project verified working on Windows 11, Python 3.11.

### Fixed
- Cleaned up duplicate section headers in readme.md

## [v1.0.0] - 2026-06-29

### Added
- Core Blogger Atom to Hugo Markdown conversion engine
- Automatic URL path conversion from Blogger (`/yyyy/mm/slug.html`) to Hugo (`/posts/slug/`)
- SEO-friendly redirect aliases from old Blogger URLs to new Hugo paths
- Support for both published and draft posts with draft status in frontmatter
- Automatic image download and local storage within post folder structure
- HTML-to-Markdown conversion for common elements (images, basic tables)
- Filename and image name sanitization (underscores to dashes, special char removal)
- Stable, deterministic image filenames using SHA256 hashing
- Link conversion to Markdown format
- Table detection and smart conversion (complex tables preserved as HTML)
- YAML frontmatter generation with title, date, updated, tags, permalink, and draft status
- Tag extraction from Blogger categories
- Robust error handling for missing permalinks with fallback to title or post ID
- Concurrent file download capability
- Support for custom output directory (default: `content/`)
- Comprehensive CLI interface with usage instructions

### Fixed
- Tags now correctly passed as YAML string instead of Python list to frontmatter
- Image filenames now use hashlib.sha256 for stability and determinism
- HTML suffix removal restricted to regex pattern (suffix-only) to prevent false positives
- Empty string handling in extract_text with explicit None check
- File collision detection in safe_mkdir using os.path.isdir
- Narrowed exception clauses in download_file and html_to_markdown for better error diagnostics

### Known Limitations
- Complex tables with colspan/rowspan may not render properly and are preserved as HTML
- Custom Blogger theme HTML may not convert correctly; manual review recommended
- Blogger-specific widgets and JavaScript elements are not converted
- ~~Windows installation may require Docker due to lxml compilation issues~~ (resolved in v1.0.1)

## Versioning

Starting with v1.0.0, this project follows Semantic Versioning:
- MAJOR: Breaking changes to CLI or output format
- MINOR: New features (e.g., new conversion capabilities)
- PATCH: Bug fixes and improvements
