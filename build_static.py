"""Render the site to static HTML.

The app used to be served by App Engine (python27 runtime, now retired), which
rendered these jinja templates per-request. This reproduces the routing of that
app (disc2017.py, removed from the repo; see commit 2f3c16a) as a one-shot
build so the site can be hosted statically.

Usage:  python build_static.py [--where WHERE.JSON] [--out _site]
"""

import argparse
import datetime
import json
import os
import shutil
from collections import OrderedDict

import jinja2

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FOLDER = 'templates/'
DOMAIN = 'disc2017.geosci.xyz'

# copied verbatim into the output alongside the rendered pages
STATIC_DIRS = ['s']

# mirrors the skip_files patterns app.yaml used, so the static build serves the
# same set of assets App Engine did (notably *.ai, the Illustrator sources)
SKIP_SUFFIXES = ('.ai', '.pyc', '.pyo', '~')


def make_env():
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(HERE),
        extensions=['jinja2.ext.autoescape'] if jinja2.__version__ < '3' else [],
        autoescape=False,
    )


def render(env, template, values, out_path):
    values = dict(values)
    values['_templateFolder'] = TEMPLATE_FOLDER
    values['_year'] = str(datetime.datetime.now().year)

    html = env.get_template(os.path.normpath(TEMPLATE_FOLDER + template)).render(values)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        f.write(html)
    return len(html)


def build(where_path, out_dir):
    with open(where_path) as f:
        where = json.load(f, object_pairs_hook=OrderedDict)

    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)

    env = make_env()
    pages = []

    # '/' -> MainPage
    pages.append(('/', render(
        env, 'index.html', {'where': where}, os.path.join(out_dir, 'index.html')
    )))

    # '/events' -> Events
    pages.append(('/events', render(
        env, 'events.html', {}, os.path.join(out_dir, 'events', 'index.html')
    )))

    # '/schedule' -- linked from the templates but never had a route on App
    # Engine, so it used to fall through to the 404. The template exists, so
    # render it.
    pages.append(('/schedule', render(
        env, 'schedule.html', {'where': where},
        os.path.join(out_dir, 'schedule', 'index.html')
    )))

    # '/<loc>' -> Where, one page per entry in where.json
    for loc, args in where.items():
        values = dict(args)
        values.setdefault('name', loc)
        values['loc'] = loc
        values['where'] = where
        pages.append(('/' + loc, render(
            env, 'where/template.html', values,
            os.path.join(out_dir, loc, 'index.html')
        )))

    # everything else -> error.html; GitHub Pages serves 404.html
    pages.append(('/404', render(
        env, 'error.html', {}, os.path.join(out_dir, '404.html')
    )))

    skipped = []

    def ignore(dirname, names):
        drop = [n for n in names
                if n.endswith(SKIP_SUFFIXES) or n.startswith('.')]
        skipped.extend(os.path.join(dirname, n) for n in drop)
        return drop

    for d in STATIC_DIRS:
        shutil.copytree(os.path.join(HERE, d), os.path.join(out_dir, d),
                        ignore=ignore)

    for path in skipped:
        print('skipped asset: {}'.format(os.path.relpath(path, HERE)))

    with open(os.path.join(out_dir, 'CNAME'), 'w') as f:
        f.write(DOMAIN + '\n')
    # keep Pages from running the output through Jekyll
    open(os.path.join(out_dir, '.nojekyll'), 'w').close()

    return pages


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--where', default=os.path.join(HERE, 'templates/where/where.json'))
    p.add_argument('--out', default=os.path.join(HERE, '_site'))
    a = p.parse_args()

    pages = build(a.where, a.out)
    for url, size in pages:
        print('{:<28} {:>8,} bytes'.format(url, size))
    print('\n{} pages -> {}'.format(len(pages), a.out))


if __name__ == '__main__':
    main()
