# Contributing

Three ways to contribute:

**1. Use the form** — use the suggest form on the site. Suggest a new offer or flag an edit. Takes 30 seconds. No account needed. Your submission becomes a public GitHub Issue automatically.

**2. Open a GitHub Issue** — go to [Issues](https://github.com/henrfo/Oslo_Mental_Health_Map/issues) and create one directly. Use the `suggestion` or `edit` label.

**3. Open a pull request** — add an entry to the right file in `_data/entries/` (see schema below).

## Entry schema

There is one file per category in `_data/entries/`. The file an entry sits in is its category.

**Services** (middle chips). The file is the offer's nivå (level of care):

| File | Nivå |
|---|---|
| `frivillig.yml` | Frivillig: volunteer and peer organisations |
| `forstelinje.yml` | Førstelinje: municipal low-threshold services, GP-level care |
| `spesialist.yml` | Spesialist: specialist health services (DPS, BUP, private specialists) |

Urgency is separate from nivå: set `akutt: true` on any offer that takes acute cases, at any level. The Akutt chip shows those.

**Fagstoff** (right chip, what you know):

| File | Contents |
|---|---|
| `retningslinjer.yml` | Retningslinjer: national guidelines and pathways (Helsedirektoratet etc.) |
| `veiledere.yml` | Veiledere: national guides and handbooks |
| `kurs.yml` | Kurs: courses and training |

**Ressurser** (right chip, who you point to):

| File | Contents |
|---|---|
| `hjelpelinjer.yml` | Hjelpelinjer: crisis and support phone lines |
| `brukerorganisasjoner.yml` | Brukerorganisasjoner: user and patient organisations |

```yaml
- name: Example Service                   # required. Official name, untranslated
  description:                            # required. One sentence: what it offers, not why it matters
    nb: Samtaletilbud for unge mellom 16 og 25 år.
    en: Counselling for young people aged 16 to 25.
  website: https://example.no             # required. The offer's own page (intake, referral info)
  date_added: 2026-10-27                  # required. Drives "Recently added"
  last_verified: 2026-10-27               # required. Date a person last confirmed the details are still correct
  tilstand: [angst, depresjon]            # services: required. Fagstoff/ressurser: optional. List, see values below
  malgruppe: [ungdom]                     # services: required. Fagstoff/ressurser: optional. List, see values below
  bydel: Gamle Oslo                       # services: required. One of the 15 bydeler, or "Hele Oslo"
  henvisning: false                       # services: required. true = referral needed
  akutt: false                            # services: required. true = takes acute cases
  address: Storgata 1, 0155 Oslo          # optional. Omit for phone- or online-only services
  lat: 59.9133                            # required if address is set. Decimal degrees (WGS84)
  lon: 10.7522
  phone: 116 123                          # optional. Required for hjelpelinjer
  draft: true                             # optional. Kept in the data but not shown on the site, e.g. while details are being verified
```

**YAML traps.** YAML reads `yes`, `no`, `on`, `off`, `true` and `false` (in any case) as true/false, both as keys and as values:
- The key for Norwegian text is `nb`, not `no`.
- Quote words like `"No"`, `"Yes"` and `"On"` when you mean the text.
- Inside `{ … }` on one line, quote any text that contains a comma or a colon, or it gets split.

**tilstand** (what the offer helps with): ids from `_data/tilstand.yml`: `angst`, `depresjon`, `bipolar`, `personlighetsforstyrrelser`, `psykose`, `spiseforstyrrelser`, `traumer` (incl. PTSD), `ocd`, `adhd`, `rus` (substance use and addiction), `selvskading` (self-harm and suicidality), `krise` (crisis and grief), or `generelt` for offers not tied to a specific condition. An entry with `generelt` matches every tilstand filter.

**malgruppe**: ids from `_data/malgruppe.yml`: `barn`, `ungdom`, `voksne`, `eldre`, `parorende` (pårørende), or `alle`. An entry with `alle` matches every målgruppe filter.

**bydel**: as listed in `_data/bydeler.yml`: Alna, Bjerke, Frogner, Gamle Oslo, Grorud, Grünerløkka, Nordre Aker, Nordstrand, Sagene, St. Hanshaugen, Stovner, Søndre Nordstrand, Ullern, Vestre Aker, Østensjø, or `Hele Oslo` for city-wide services. An entry with `Hele Oslo` matches every bydel filter.

**last_verified** is a human check that the service still exists and the details above are right. A working link doesn't prove that: a site can stay up after a service closes or changes. It shows as small text under the description.

**Link status** is not part of an entry. The weekly link checker writes it to `_data/health.yml`, keyed by the entry's slugified name.

No marketing language.
