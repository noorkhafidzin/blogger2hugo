# Blogger Atom to Hugo Markdown Converter

This Python script converts a Blogger backup file (`.atom`) from Google Takeout into Markdown (`.md`) files for Hugo.
The output is compatible with default Hugo structure and can be used directly inside `content/`.

## Features

1. Automatically converts URL paths from
   `/yyyy/mm/slug.html` → `/posts/slug/`
2. Creates Hugo redirect aliases from the old Blogger URL to the new Hugo path.
   This helps keep SEO and old links working after migration.
3. Converts both published and draft posts.
4. Downloads all article images and saves them inside `/images/` inside each post folder.
5. Converts simple HTML elements to Markdown:

   * Image tags
   * Basic tables (without colspan/rowspan)

## Additional Notes

* Filenames and image names are cleaned and converted. Underscores (`_`) are replaced with dashes (`-`) to avoid backslash escaping in Markdown.
* Complex or theme-specific HTML from Blogger will be kept as raw HTML inside the Markdown file. Some parts may be lost and should be checked manually.

## Installation

```
git clone https://github.com/your/repo.git
cd your-repo
pip install -r requirements.txt
```

## Usage

```
python blogger2hugo.py [file.atom] [output_dir]
```

* `file.atom` : Blogger export file from Google Takeout
* `output_dir` : optional target directory (default is `content/`)

### Example

```
python blogger2hugo.py myblog.atom
```

Output structure:

```
content/
 └─ posts/
    └─ example-slug/
       ├─ index.md
       └─ images/
```

## Known Issues

* Custom HTML designed for Blogger themes may not convert correctly.
  Some styling attributes will be removed, and some elements may be written as incomplete HTML.
  Please review those posts manually.

## License

This project is licensed under the MIT License.
You are free to modify or improve the script as needed.

---
