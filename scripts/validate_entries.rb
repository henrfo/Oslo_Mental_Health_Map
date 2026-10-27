# Checks every entry in _data/entries/ against the schema in CONTRIBUTING.md.
# Run before committing:  ruby scripts/validate_entries.rb
# Exits non-zero and lists the problems if anything is wrong.
#
# Written in Ruby because Ruby (via Jekyll) is already needed to build the site,
# and its YAML parser reads the files exactly as Jekyll does.

require 'yaml'
require 'date'

ROOT = File.expand_path('..', __dir__)
load_yaml = ->(path) { YAML.load_file(File.join(ROOT, path), permitted_classes: [Date]) }

categories = load_yaml.('_data/categories.yml')
tilstand   = load_yaml.('_data/tilstand.yml').map { |t| t['id'] }
malgruppe  = load_yaml.('_data/malgruppe.yml').map { |m| m['id'] }
bydeler    = load_yaml.('_data/bydeler.yml')
dager      = load_yaml.('_data/dager.yml').map { |d| d['id'] }
dps_codes  = load_yaml.('_data/dps.yml')['areas'].map { |a| a['code'] }

problems = []
count = 0

Dir[File.join(ROOT, '_data/entries/*.yml')].sort.each do |file|
  cat = categories.find { |c| c['id'] == File.basename(file, '.yml') }
  unless cat
    problems << "#{File.basename(file)}: no category with this id in _data/categories.yml"
    next
  end
  service = cat['group'] == 'tjenester'

  (YAML.load_file(file, permitted_classes: [Date]) || []).each do |e|
    count += 1
    where = "#{File.basename(file)} / #{e['name'] || '(no name)'}"
    bad = ->(msg) { problems << "#{where}: #{msg}" }

    %w[name website date_added last_verified].each { |k| bad.("missing #{k}") unless e[k] }
    bad.('website should start with https://') if e['website'] && !e['website'].to_s.start_with?('https://')

    # Description: both languages, exactly one sentence each
    d = e['description']
    if !d.is_a?(Hash) || d.keys.sort != %w[en nb]
      bad.('description needs nb and en (the key "no" reads as false in YAML; use nb)')
    else
      d.each do |lang, text|
        text = text.to_s.strip
        bad.("description.#{lang} should end with a full stop") unless text.end_with?('.')
        # Abbreviations like "St. Hanshaugen" aren't sentence breaks
        plain = text.gsub(/\b(St|Dr|Nr|ca|kl|bl\.a|f\.eks|m\.m|osv)\./i, '')
        bad.("description.#{lang} should be one sentence") if plain =~ /[.!?]\s+[[:upper:]]/
      end
    end

    if service
      bad.('needs dekker, dps or bydel (which bydeler it serves)') unless e['dekker'] || e['dps'] || e['bydel']
      %w[tilstand malgruppe].each { |k| bad.("missing #{k}") unless e[k] }
      %w[henvisning akutt].each { |k| bad.("#{k} must be true or false") unless [true, false].include?(e[k]) }
    end

    Array(e['tilstand']).each  { |v| bad.("unknown tilstand '#{v}'") unless tilstand.include?(v) }
    Array(e['malgruppe']).each { |v| bad.("unknown malgruppe '#{v}' (pårørende is written parorende)") unless malgruppe.include?(v) }
    bad.("unknown bydel '#{e['bydel']}'") if e['bydel'] && !bydeler.include?(e['bydel'])
    Array(e['dekker']).each    { |v| bad.("unknown bydel '#{v}' in dekker") unless bydeler.include?(v) }
    bad.("unknown dps '#{e['dps']}'") if e['dps'] && !dps_codes.include?(e['dps'])

    if e['address'] && !(e['lat'] && e['lon']) && !e['draft']
      bad.('has an address but no lat/lon (geocode it)')
    end

    # Recurring activities
    if (nar = e['nar'])
      bad.("nar.dag must be one of #{dager.join(', ')}") unless dager.include?(nar['dag'])
      %w[fra til].each do |k|
        next unless nar.key?(k)
        bad.("nar.#{k} must be a quoted time like \"12:00\" (unquoted, YAML reads it as a number)") unless nar[k].is_a?(String) && nar[k] =~ /\A\d{2}:\d{2}\z/
      end
      bad.('nar.hyppighet must be ukentlig or annenhver') unless %w[ukentlig annenhver].include?(nar['hyppighet'])
      bad.('annenhver needs sesong.fra to count weeks from') if nar['hyppighet'] == 'annenhver' && !(e['sesong'] && e['sesong']['fra'])
    end
    if (s = e['sesong'])
      %w[fra til].each { |k| bad.("sesong.#{k} must be a date like 2026-11-01") if s.key?(k) && !s[k].is_a?(Date) }
      bad.('sesong.til is before sesong.fra') if s['fra'].is_a?(Date) && s['til'].is_a?(Date) && s['til'] < s['fra']
    end
    if e['pris'] && !(e['pris'].is_a?(Hash) && e['pris'].keys.sort == %w[en nb])
      bad.('pris needs nb and en')
    end
  end
end

if problems.empty?
  puts "All #{count} entries are valid."
else
  puts problems
  puts "\n#{problems.size} problem(s) in #{count} entries."
  exit 1
end
