# Oslo Mental Health Map

A community-driven overview of mental health resources in Oslo.

## How it works

Entries are stored as YAML files in `_data/tools/`, grouped by the categories in `_data/categories.yml`. The site is built with Jekyll and hosted on GitHub Pages.

## Local preview

Requires Homebrew Ruby (`brew install ruby`). `Gemfile.local` uses Jekyll 4, since the `github-pages` gem does not run on current Ruby.

```bash
export PATH=/opt/homebrew/opt/ruby/bin:$PATH BUNDLE_GEMFILE=Gemfile.local
bundle config set --local path vendor/bundle   # first time only
bundle install                                  # first time only
bundle exec jekyll serve --livereload
```

Then open http://localhost:4000/Oslo_Mental_Health_Map/

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) or use the suggest form on the site.
