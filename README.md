# CoderList

This project is a lightweight static website hosted on GitHub Pages using a GitHub Actions workflow.

## Resource data source

The resource list is stored in `resources.json`, and that file is the source of truth for the site.

Example:

```json
{
  "categories": [
    {
      "title": "Core references",
      "links": [
        {
          "title": "MDN Web Docs",
          "url": "https://developer.mozilla.org/",
          "description": "HTML / CSS / JavaScript"
        }
      ]
    }
  ]
}
```

The build step runs `python3 build.py`, which reads `resources.json` and regenerates `index.html` automatically.

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
