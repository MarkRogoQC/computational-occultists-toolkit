# Computational Occultists Toolkit

A collection of Python programs that measure frequency patterns in time, events, and symbolic systems. Each tool decomposes its input into a 72-band frequency vector and compares against known references.

This is a diagnostic instrument. Not a prediction engine.

## Install

```
pip install git+https://github.com/MarkRogoQC/computational-occultists-toolkit
```

Or locally:

```
cd cotk
pip install -r requirements.txt
pip install -e .
cot --help
```

## Tools

| Tool | File | What |
|------|------|------|
| Naometria Calculator | `naometria_calculator.py` | Apply Studion's number operations to any year |
| Shem HaMephorash | `shem_hamephorash.py` | 72 Names lookup by band, angel name, or datetime |
| Ars Magna Llull | `ars_magna_llull.py` | Combinatorial triples of 9 principles for any subject |
| Pi Memory Reader | `pi_memory_reader.py` | Deterministic π position from any input |
| Planetary Mirror | `planetary_mirror.py` | Planetary positions as 72-band vectors |
| Enoch Calendar | `enoch_calendar.py` | Convert dates to 364-day Enoch calendar |
| Trithemius Cipher | `trithemius_cipher.py` | 3-mode polyalphabetic cipher engine |
| Fludd Monochord | `fludd_monochord.py` | Harmonic ratio ladder for 72 bands |
| Waveform Trace | `trace.py` | Compare event signatures against 45 historical events |
| CLI | `cli.py` | `cot pulse`, `cot date`, `cot trace`, etc. |

## Run

```
cot pulse              # Reading of right now
cot date 2040          # Analyze any year
cot trace "Ukraine" 2022 2 24
cot test               # Run all tests
cot tools              # List all commands
```

## Dependencies

- Python 3.10+
- pyephem (planetary positions)

## Architecture

```
Input → decompose → 72-band vector → compare → output
```

All tools decompose to the same 72-band frequency space for cross-comparison.

## Sources

The algorithms reference historical systems: Book of Enoch (364-day calendar), Kabbalistic Shem HaMephorash (72 Names), Ramón Llull's Ars Magna (combinatorial wheels), Johannes Trithemius's Steganographia (ciphers), Simon Studion's Naometria (prophetic calculation), Robert Fludd's Monochord (harmonic ratios).

## Limitations

- Symbol database: 400 entries — not comprehensive
- Historical database: 45 events — sparse
- Planetary positions are astronomical, mapping to 72 bands is one possible mapping
- π digits beyond 10000 use repeated blocks — not rigorous at large positions
- The 72-band register is a choice of resolution, not a natural constant
