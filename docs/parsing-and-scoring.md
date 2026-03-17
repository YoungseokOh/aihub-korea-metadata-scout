# Parsing and Scoring

## Parsing Principles

The parser is intentionally defensive because `aihubshell` output can include:

- banners
- notices
- Korean and English text
- UTF-8 box-drawing characters
- file tree branches
- incomplete or ambiguous lines

The parser prefers partial results over all-or-nothing parsing.

## Dataset Listing Parsing

Listing output is parsed from lines matching:

- `dataset_key, title`

Anything else is treated as a banner line or a parse warning.

## Dataset Detail Parsing

Per-dataset inspection output is parsed from the visible tree:

- directory nodes are inferred from indentation and branch characters
- leaf nodes are parsed from `name | size | file_key`
- notice blocks are captured separately
- unparsed lines are preserved as warnings

Special handling:

- missing page responses become `parse_status=error`
- file size totals are computed only from visible size strings

## Uncertainty Policy

The tool does not infer actual semantic meaning from invisible data contents.

Allowed evidence:

- dataset title
- metadata lines shown by the shell
- file and directory names
- file counts
- visible sizes
- visible train/validation or label/source splits

Disallowed evidence:

- hidden assumptions about the dataset internals
- undocumented API behavior
- imagined label semantics

## Scoring Heuristics

Three exploration scores are generated:

- opportunity score
- build difficulty score
- data readiness score

These scores are not meant to be precise. They are ranking hints only.

### Opportunity score

Factors:

- apparent commercial relevance of the domain
- modality usefulness
- likely repeat demand
- niche defensibility
- likely infrastructure burden

### Difficulty score

Factors:

- visible total size
- modality complexity
- number of fragments
- probable preprocessing burden
- integration complexity

### Data readiness score

Factors:

- metadata clarity
- visible structural consistency
- train/validation separation
- label/source separation
- parser confidence

## When Updating This Logic

- keep heuristics explainable
- preserve explicit uncertainty wording
- avoid overfitting to a small sample of fixtures
- update tests when adding new category or modality rules

