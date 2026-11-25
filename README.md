# DISC 2017

Website for the 2017 SEG Distinguished Instructor Short Course,
[disc2017.geosci.xyz](https://disc2017.geosci.xyz).

The pages are jinja templates in `templates/`, with the course locations in
`templates/where/where.json`. `build_static.py` renders them to static HTML in
`_site/`, and the GitHub Actions workflow in `.github/workflows/pages.yml`
publishes that to GitHub Pages on every push to `main`.

To build locally:

    pip install -r requirements.txt
    python build_static.py
