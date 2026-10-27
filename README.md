# Oslo Mental Health Map

A community-driven overview of mental health resources in Oslo.

## How it works

Entries are stored as YAML files in `_data/entries/`, grouped by the categories in `_data/categories.yml`. The site is built with Jekyll and hosted on GitHub Pages.

## Local preview

Requires Homebrew Ruby (`brew install ruby`). The site uses Jekyll 4, the same version the deploy workflow builds with.

```bash
export PATH=/opt/homebrew/opt/ruby/bin:$PATH
bundle config set --local path vendor/bundle   # first time only
bundle install                                  # first time only
bundle exec jekyll serve --livereload
```

Then open http://localhost:4000/Oslo_Mental_Health_Map/

Before committing data changes, run `ruby scripts/validate_entries.rb`.

## Deploy and weekly checks

- `.github/workflows/deploy.yml` builds and publishes to GitHub Pages on every push to `main`.
- `.github/workflows/weekly_checks.yml` runs every Monday: it checks each website (broken links get a "Brutt lenke" tag) and opens an issue when a `kilde` page changes. It never edits entries.
- `scripts/update_dps.py` and `scripts/update_dps_geo.py` refresh the DPS catchment data from SSB when a new year's version appears.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) or use the suggest form on the site.
