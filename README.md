# CoderList

This project is a lightweight static website hosted on GitHub Pages using a GitHub Actions workflow.

## Resource data source

The resource list is stored in `resources.ini`. The build converts it into a JSON snapshot at `resources.json`, then renders the site from that JSON structure.

Example:

```ini
[Core references]
MDN Web Docs = https://developer.mozilla.org/ | HTML / CSS / JavaScript
GitHub Docs = https://docs.github.com/ | Git / Actions / Pages
```

The build step runs `python3 build.py`, which reads `resources.ini`, regenerates `resources.json`, and updates `index.html` automatically.

## Local preview

Generate the page and then serve it locally:

```bash
python3 build.py
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## GitHub Pages setup

1. Push this repository to GitHub.
2. In the repository settings, enable GitHub Pages.
3. Set the source to **GitHub Actions**.
4. The page will deploy automatically on pushes to the `main` branch.
