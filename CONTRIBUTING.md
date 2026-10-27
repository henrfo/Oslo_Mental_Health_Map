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
| `akutt.yml` | Akutt: emergency and crisis services (legevakt, psychiatric emergency, child welfare on call) |

The levels form a ladder: Frivillig → Førstelinje → Spesialist → Akutt.

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
- name: Example Service                   # required. Short display name, one line (about 22 characters)
  full_name: Example Service for Everyone # optional. The full official name; shown on hover and searchable
  description:                            # required. Exactly one sentence: what it is and who it's for
    nb: Samtaletilbud for unge mellom 16 og 25 år.
    en: Counselling for young people aged 16 to 25.
  website: https://example.no             # required. The offer's own page (intake, referral info)
  date_added: 2026-10-27                  # required. Drives "Recently added"
  last_verified: 2026-10-27               # required. Date a person last confirmed the details; drives the status dot
  tilstand: [angst, depresjon]            # services: required. Fagstoff/ressurser: optional. List, see values below
  malgruppe: [ungdom]                     # services: required. Fagstoff/ressurser: optional. List, see values below
  bydel: Gamle Oslo                       # services: required. One of the 15 bydeler, or "Hele Oslo"
  henvisning: false                       # services: required. true = referral needed
  address: Storgata 1, 0155 Oslo          # optional. Omit for phone- or online-only services
  lat: 59.9133                            # required if address is set. Decimal degrees (WGS84)
  lon: 10.7522
  phone: 116 123                          # optional. Required for hjelpelinjer
  samling: aktivitetshus                  # optional. Groups similar places into one expandable list row (see _data/samlinger.yml)
  draft: true                             # optional. Kept in the data but not shown on the site, e.g. while details are being verified
  nar:                                    # optional, for recurring activities
    dag: sondag                           #   mandag | tirsdag | onsdag | torsdag | fredag | lordag | sondag
    fra: "12:00"                          #   quoted, or YAML reads 12:00 as a number
    til: "14:00"
    hyppighet: ukentlig                   #   ukentlig | annenhver (every other week, counted from sesong.fra)
  sesong:                                 # optional. Required for annenhver; the activity drops out of "Denne uken" after til
    fra: 2026-11-01
    til: 2027-04-11
  pris: { nb: Gratis, en: Free }          # optional
  kilde: https://mentalhelse.no/oslo/…    # optional. Page the nar/sesong info comes from; checked weekly for changes
```

**One sentence.** `description` is exactly one sentence saying what it is and who it's for. Times, season and price go in `nar`, `sesong` and `pris`, not in the description.

**Recurring activities.** `nar` + `sesong` power the "Denne uken" chip: the browser works out which activities run this week. The weekly source check fetches each `kilde` page and opens an issue when it changes; it never edits the data, so a person approves every change.

**Check before committing.** `ruby scripts/validate_entries.rb` checks every entry against these rules.

**YAML traps.** YAML reads `yes`, `no`, `on`, `off`, `true` and `false` (in any case) as true/false, both as keys and as values:
- The key for Norwegian text is `nb`, not `no`.
- Quote words like `"No"`, `"Yes"` and `"On"` when you mean the text.
- Inside `{ … }` on one line, quote any text that contains a comma or a colon, or it gets split.

**tilstand** (what the offer helps with): ids from `_data/tilstand.yml`: `angst`, `depresjon`, `bipolar`, `personlighetsforstyrrelser`, `psykose`, `spiseforstyrrelser`, `traumer` (incl. PTSD), `ocd`, `adhd`, `rus` (substance use and addiction), `selvskading` (self-harm and suicidality), `krise` (crisis and grief), or `generelt` for offers not tied to a specific condition. An entry with `generelt` matches every tilstand filter.

**malgruppe**: ids from `_data/malgruppe.yml`: `barn`, `ungdom`, `voksne`, `eldre`, `parorende` (pårørende), or `alle`. An entry with `alle` matches every målgruppe filter.

**bydel**: as listed in `_data/bydeler.yml`: Alna, Bjerke, Frogner, Gamle Oslo, Grorud, Grünerløkka, Nordre Aker, Nordstrand, Sagene, St. Hanshaugen, Stovner, Søndre Nordstrand, Ullern, Vestre Aker, Østensjø, or `Hele Oslo` for city-wide services. An entry with `Hele Oslo` matches every bydel filter.

**last_verified** is a human check that the service still exists and the details above are right. A working link doesn't prove that: a site can stay up after a service closes or changes. It drives the status dot; hover the dot to see the date.

**Status dot.** Shows the age of `last_verified`: green within the last 30 days, amber 1–6 months, grey over 6 months.

**Link status** is not part of an entry; a broken link fades the row and adds a "Brutt lenke" tag. The weekly link checker writes it to `_data/health.yml`, keyed by the entry's slugified name.

No marketing language.
