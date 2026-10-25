# kaptainkris92.github.io

My blog, built by GitHub Pages with Jekyll. There's no theme: the layouts and the stylesheet are all in this repo, so the look can be changed freely.

## Where things are

| Path | What it is |
|---|---|
| `_posts/` | One Markdown file per post, named `YYYY-MM-DD-slug.md`. Published at `/blog/<slug>/`. |
| `_layouts/` | `default.html` (every page), `post.html` (posts) |
| `index.html` | The home page |
| `privacy.html` | Night Shift Publisher privacy policy. **Keep this URL**: it's registered with Google and Meta. |
| `assets/css/site.css` | The whole look. Colours and fonts are tokens at the top, with a dark set below. |
| `assets/js/charts.js` | Hover tooltips for charts |
| `assets/posts/<post>/` | Each post's images |
| `_includes/charts/` | Charts for the Night Shift post, made by `_scripts/nightshift_charts.py` |
| `projects/vaper-taper/3d-model.html` | The interactive 3D model from the vape-logger repo |

`/vape-logger/` is served by the vape-logger repo's own Pages workflow (the Vaper Taper app), so don't create a folder with that name here.

## Writing a post

Add `_posts/2026-11-01-my-post.md`:

```markdown
---
title: My post
description: One or two sentences for the home page and link previews.
project: Project name
repo: kaptainkris92/some-repo        # optional
image: /assets/posts/my-post/hero.jpg  # optional
image_alt: What the picture shows
thumb: /assets/posts/my-post/thumb.jpg # optional, for the home page
---
Text here. Put "* Contents" then "{:toc}" on the next line for a table of contents.
```

Optional front matter: `image_dark` (a hero for dark mode), `image_credit` (a caption under the hero, HTML allowed), `image_fit: contain` (don't crop the hero), `charts: true` (loads the chart tooltips).

## Refreshing the Night Shift charts

```
python3 _scripts/nightshift_charts.py ../nightshift-pipeline/data/approvals.json _includes/charts
```

## Checking a change

Pull requests run the same Jekyll build Pages uses (`.github/workflows/check-build.yml`). To preview locally, install Ruby, then `gem install jekyll jekyll-feed webrick` and run `jekyll serve`.
