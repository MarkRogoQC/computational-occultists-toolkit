#!/usr/bin/env python3
"""
Fludd's Monochord — Harmonic Ratio Ladder
===========================================
Utriusque Cosmi Historia (1617–1619)

Robert Fludd's Monochord of the Universe divides a single string
into 72 harmonic bands, mapping the macrocosm through musical
ratios, planetary associations, and Hermetic principles.

The 72-band register spans 6 octaves (12 chromatic notes per octave)
using just-intonation ratios. Each octave maps to a cosmic register:

    Octave 0 — bands   1–12 : Primum Mobile (Planetary Foundation)
    Octave 1 — bands  13–24 : Elemental Realm
    Octave 2 — bands  25–36 : Hermetic Angelic Kingdom
    Octave 3 — bands  37–48 : Sidereal Cosmic Spheres
    Octave 4 — bands  49–60 : Human Microcosm
    Octave 5 — bands  61–72 : Divine Meta-Omega

Key octave points:
    Band  1 = 1:1   (Unison — Earth/Saturn foundation)
    Band 12 = 2:1   (Octave — completion of Planetary register)
    Band 24 = 4:1   (Double Octave — Hermetic register)
    Band 36 = 8:1   (Triple Octave — Angelic register)
    Band 48 = 16:1  (Quadruple Octave — Cosmic register)
    Band 60 = 32:1  (Quintuple Octave — Human register)
    Band 72 = 64:1  (Sextuple Octave — Meta/Omega)

Reference frequency: C₂ = 65.406 Hz (fundamental for band 1).
"""

import math
from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Union

# ──────────────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────────────

# Fundamental reference frequency (C₂ in A440 equal temperament)
FUNDAMENTAL_HZ: float = 65.406

# ── Chromatic just-intonation ratios (12-tone scale within one octave) ──
# Each entry is (numerator, denominator) representing the interval from
# the tonic.  Step 11 IS the octave (2:1), so each octave has exactly
# 12 chromatic positions including the destination octave note.
CHROMATIC_RATIOS: List[Tuple[int, int]] = [
    (1, 1),       # 0 — 1:1    Unison
    (16, 15),     # 1 — 16:15  Minor Second / Semitone
    (9, 8),       # 2 — 9:8    Major Second / Whole Tone
    (6, 5),       # 3 — 6:5    Minor Third
    (5, 4),       # 4 — 5:4    Major Third
    (4, 3),       # 5 — 4:3    Perfect Fourth
    (45, 32),     # 6 — 45:32  Augmented Fourth / Tritone
    (3, 2),       # 7 — 3:2    Perfect Fifth
    (8, 5),       # 8 — 8:5    Minor Sixth
    (5, 3),       # 9 — 5:3    Major Sixth
    (16, 9),      # 10 — 16:9  Minor Seventh
    (2, 1),       # 11 — 2:1   Octave
]

# Human-readable interval names for each chromatic step
INTERVAL_NAMES: List[str] = [
    "Unison",
    "Minor Second",
    "Major Second",
    "Minor Third",
    "Major Third",
    "Perfect Fourth",
    "Tritone (Augmented Fourth)",
    "Perfect Fifth",
    "Minor Sixth",
    "Major Sixth",
    "Minor Seventh",
    "Octave",
]

# Consonance scores for each chromatic step (0 = dissonant, 1 = perfectly consonant)
# Based on harmonic simplicity of the ratio.
CONSONANCE_SCORES: List[float] = [
    1.00,   # Unison — pure identity
    0.10,   # Minor Second — most dissonant interval
    0.30,   # Major Second — mild dissonance
    0.65,   # Minor Third — consonant (imperfect)
    0.75,   # Major Third — consonant (imperfect)
    0.80,   # Perfect Fourth — strong consonance
    0.15,   # Tritone — the "devil's interval", tense
    0.85,   # Perfect Fifth — most consonant after unison/octave
    0.50,   # Minor Sixth — imperfect consonance
    0.55,   # Major Sixth — imperfect consonance
    0.30,   # Minor Seventh — mild dissonance
    1.00,   # Octave — perfect identity (doubled frequency)
]

# ── Octave register names (Fludd's cosmic hierarchy) ──
OCTAVE_REGISTERS: List[str] = [
    "Primum Mobile — Planetary Foundation",
    "Elemental Realm",
    "Hermetic Angelic Kingdom",
    "Sidereal Cosmic Spheres",
    "Human Microcosm",
    "Divine Meta-Omega",
]

# ── Step-level associations: planet or element for each chromatic position ──
STEP_ASSOCIATIONS: List[Tuple[str, str]] = [
    ("Saturn  ♄ / Earth    ", "planet"),
    ("Moon    ☽ / Silver   ", "planet"),
    ("Mercury ☿ / Quicksilver", "planet"),
    ("Venus   ♀ / Copper   ", "planet"),
    ("Sun     ☉ / Gold     ", "planet"),
    ("Mars    ♂ / Iron     ", "planet"),
    ("Fire    🔥 / Aries    ", "element"),
    ("Jupiter ♃ / Tin      ", "planet"),
    ("Water   💧 / Cancer   ", "element"),
    ("Air     💨 / Libra    ", "element"),
    ("Aether  ✧ / Quintessence", "element"),
    ("Omega   Ω / Completion", "element"),
]

# ── Planetary intervals: each planet's signature ratio within the first octave ──
# Fludd mapped the 7 classical planets to the 7 diatonic notes.
# Saturn (Earth) anchors the fundamental; Jupiter crowns the octave threshold.
PLANETARY_DATA: Dict[str, Dict] = {
    "Saturn":   {"step": 0,  "ratio": (1, 1),   "note": "C",  "hermetic_ratio": "1:1"},
    "Moon":     {"step": 1,  "ratio": (16, 15), "note": "C♯", "hermetic_ratio": "16:15"},
    "Mercury":  {"step": 2,  "ratio": (9, 8),   "note": "D",  "hermetic_ratio": "9:8"},
    "Venus":    {"step": 3,  "ratio": (6, 5),   "note": "D♯", "hermetic_ratio": "6:5"},
    "Sun":      {"step": 4,  "ratio": (5, 4),   "note": "E",  "hermetic_ratio": "5:4"},
    "Mars":     {"step": 5,  "ratio": (4, 3),   "note": "F",  "hermetic_ratio": "4:3"},
    "Jupiter":  {"step": 7,  "ratio": (3, 2),   "note": "G",  "hermetic_ratio": "3:2"},
}

# Note names for each chromatic step (relative to C)
CHROMATIC_NOTE_NAMES: List[str] = [
    "C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B",
]

# ── Chord templates: (name, [step_pattern], is_complete) ──
# Each template is a list of chromatic step indices from the root.
CHORD_TEMPLATES: List[Tuple[str, List[int]]] = [
    ("Major",                 [0, 4, 7]),
    ("Minor",                 [0, 3, 7]),
    ("Diminished",            [0, 3, 6]),
    ("Augmented",             [0, 4, 8]),
    ("Sus2",                  [0, 2, 7]),
    ("Sus4",                  [0, 5, 7]),
    ("Power Chord (5th)",     [0, 7]),
    ("Major 7th",             [0, 4, 7, 11]),
    ("Minor 7th",             [0, 3, 7, 10]),
    ("Dominant 7th",          [0, 4, 7, 10]),
    ("Diminished 7th",        [0, 3, 6, 9]),
    ("Half-Diminished 7th",   [0, 3, 6, 10]),
    ("Major 6th",             [0, 4, 7, 9]),
    ("Minor 6th",             [0, 3, 7, 9]),
    ("Augmented 7th",         [0, 4, 8, 10]),
    ("Minor-Major 7th",       [0, 3, 7, 11]),
    ("Dominant 9th",          [0, 2, 4, 7, 10]),
    ("Major 9th",             [0, 2, 4, 7, 11]),
    ("Minor 9th",             [0, 2, 3, 7, 10]),
    ("Add9",                  [0, 2, 4, 7]),
    ("Quartal (4th stack)",   [0, 5, 10]),
    ("Quintal (5th stack)",   [0, 7, 2]),
    ("Whole Tone",            [0, 2, 4, 6, 8, 10]),
    ("Chromatic Cluster",     list(range(12))),
]


# ──────────────────────────────────────────────────────────────────────
# DATA CLASSES
# ──────────────────────────────────────────────────────────────────────

@dataclass
class BandDivision:
    """A single division (band) on Fludd's Monochord."""
    band: int
    octave: int
    step: int
    ratio: float
    ratio_str: str
    cents: float
    frequency_hz: float
    interval_name: str
    association: str
    association_type: str       # "planet" or "element"
    register: str
    consonance_score: float


@dataclass
class IntervalResult:
    """Result of computing the interval between two bands."""
    band_a: int
    band_b: int
    ratio: float
    ratio_str: str
    cents: float
    interval_name: str
    step_distance: int
    consonance_score: float


@dataclass
class HarmonicNode:
    """A single harmonic in the natural harmonic series."""
    harmonic_number: int
    band: int
    frequency_ratio: float
    frequency_ratio_str: str
    interval_name: str
    cents_from_fundamental: float


@dataclass
class PlanetaryResult:
    """A planet's harmonic signature."""
    planet: str
    hermetic_ratio: str
    cents: float
    musical_note: str
    step: int
    aligned_bands: List[int]


@dataclass
class ChordResult:
    """The chord formed by a set of bands."""
    chord_name: str
    root_band: int
    root_note: str
    intervals: List[str]
    step_pattern: List[int]
    consonance: float


# ──────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────

def ratio_to_cents(numerator: int, denominator: int) -> float:
    """Convert a frequency ratio n:d to cents (1200 cents = 1 octave)."""
    return 1200.0 * math.log2(numerator / denominator)


def ratio_value(numerator: int, denominator: int) -> float:
    """Return the float value of a ratio n:d."""
    return numerator / denominator


def normalize_ratio_to_octave(ratio: float) -> float:
    """Fold an arbitrary ratio into the range [1.0, 2.0)."""
    if ratio <= 0:
        raise ValueError(f"Ratio must be positive, got {ratio}")
    while ratio >= 2.0:
        ratio /= 2.0
    while ratio < 1.0:
        ratio *= 2.0
    return ratio


def ratio_to_fraction(ratio: float, max_denominator: int = 64) -> Fraction:
    """Approximate a float ratio as a simple fraction."""
    return Fraction(ratio).limit_denominator(max_denominator)


def ratio_to_str(numerator: int, denominator: int) -> str:
    """Format a ratio as a reduced string like '3:2'."""
    g = math.gcd(numerator, denominator)
    return f"{numerator // g}:{denominator // g}"


def band_to_octave_step(band: int) -> Tuple[int, int]:
    """Convert a band number (1-72) to (octave_index, step_index)."""
    if not 1 <= band <= 72:
        raise ValueError(f"Band must be between 1 and 72, got {band}")
    octave = (band - 1) // 12
    step = (band - 1) % 12
    return octave, step


def band_to_ratio(band: int) -> float:
    """Get the absolute frequency ratio for a given band."""
    octave, step = band_to_octave_step(band)
    num, den = CHROMATIC_RATIOS[step]
    return (2 ** octave) * (num / den)


def band_to_frequency(band: int) -> float:
    """Get the frequency in Hz for a given band."""
    return FUNDAMENTAL_HZ * band_to_ratio(band)


def ratio_to_closest_step(ratio: float) -> int:
    """Find the chromatic step (0-11) closest to a given ratio."""
    normalized = normalize_ratio_to_octave(ratio)
    best_step = 0
    best_diff = float("inf")
    for step_idx, (num, den) in enumerate(CHROMATIC_RATIOS):
        step_ratio = num / den
        diff = abs(normalized - step_ratio)
        if diff < best_diff:
            best_diff = diff
            best_step = step_idx
    return best_step


def steps_to_chromatic_ratio(steps: int) -> float:
    """Get the ratio for a given number of chromatic steps (e.g., 7 = perfect fifth)."""
    octaves = steps // 12
    remainder = steps % 12
    num, den = CHROMATIC_RATIOS[remainder]
    return (2 ** octaves) * (num / den)


def consonance_for_ratio(ratio: float) -> float:
    """Compute a 0-1 consonance score for an arbitrary frequency ratio.

    Algorithm: find the closest just-intonation chromatic step, then
    apply a penalty proportional to the tuning deviation in cents.
    Pure matches get the canonical consonance score; deviations are
    penalised smoothly.
    """
    normalized = normalize_ratio_to_octave(ratio)
    best_step = ratio_to_closest_step(normalized)
    base_score = CONSONANCE_SCORES[best_step]
    ideal_ratio = CHROMATIC_RATIOS[best_step][0] / CHROMATIC_RATIOS[best_step][1]
    deviation_cents = abs(1200.0 * math.log2(normalized / ideal_ratio))
    # Penalty: every 5 cents of deviation reduces score by 10%
    penalty = min(1.0, deviation_cents / 50.0)
    return base_score * (1.0 - penalty)


def _note_name_for_octave_step(octave: int, step: int) -> str:
    """Return a scientific pitch notation note name."""
    note = CHROMATIC_NOTE_NAMES[step]
    # C₂ is octave 2 in SPD, our octave 0 maps to C₂
    return f"{note}{octave + 2}"


# ──────────────────────────────────────────────────────────────────────
# CORE FUNCTIONS
# ──────────────────────────────────────────────────────────────────────

def monochord_divisions(
    n_divisions: int = 72,
) -> List[BandDivision]:
    """Return the full harmonic series divided across n_divisions bands.

    Each band maps to a specific harmonic ratio on Fludd's Monochord,
    with planetary/elemental associations and cosmic register names.

    Args:
        n_divisions: Number of divisions (default 72).

    Returns:
        List of BandDivision dataclass instances.
    """
    divisions: List[BandDivision] = []
    for band in range(1, n_divisions + 1):
        octave, step = band_to_octave_step(band)
        num, den = CHROMATIC_RATIOS[step]
        ratio = (2 ** octave) * (num / den)
        cents = ratio_to_cents(num, den) + (octave * 1200)
        freq = FUNDAMENTAL_HZ * ratio
        assoc, assoc_type = STEP_ASSOCIATIONS[step]
        register = OCTAVE_REGISTERS[octave] if octave < len(OCTAVE_REGISTERS) else f"Octave {octave}"

        divisions.append(BandDivision(
            band=band,
            octave=octave,
            step=step,
            ratio=ratio,
            ratio_str=ratio_to_str(num * (2 ** octave), den),
            cents=cents,
            frequency_hz=freq,
            interval_name=INTERVAL_NAMES[step],
            association=assoc.strip(),
            association_type=assoc_type,
            register=register,
            consonance_score=CONSONANCE_SCORES[step],
        ))
    return divisions


def interval_for_bands(band_a: int, band_b: int) -> IntervalResult:
    """Compute the musical interval between any two bands.

    Returns the frequency ratio, cents, named interval, and consonance
    score for the interval formed by comparing band_a to band_b.

    Args:
        band_a: First band number (1-72).
        band_b: Second band number (1-72).

    Returns:
        IntervalResult with ratio, cents, interval name, and consonance.
    """
    ratio_a = band_to_ratio(band_a)
    ratio_b = band_to_ratio(band_b)

    # Interval ratio: larger / smaller (always ≥ 1)
    interval_ratio = max(ratio_a, ratio_b) / min(ratio_a, ratio_b)
    cents = 1200.0 * math.log2(interval_ratio)

    # Step distance in chromatic semitones
    step_dist = round(cents / 100.0)

    # Normalize interval to within one octave for naming
    normalized = normalize_ratio_to_octave(interval_ratio)
    step = ratio_to_closest_step(normalized)
    interval_name = INTERVAL_NAMES[step]

    # Add octave count prefix for wider intervals
    octaves = step_dist // 12
    remainder = step_dist % 12
    if octaves > 0:
        if remainder == 0:
            # Pure octave(s) — no need to append "+ Unison"
            if octaves == 1:
                interval_name = "Octave"
            else:
                interval_name = f"{octaves} Octaves"
        else:
            if octaves == 1:
                prefix = "Octave + "
            else:
                prefix = f"{octaves} Octaves + "
            interval_name = prefix + interval_name

    # Reduce ratio to simplest terms for display
    frac = ratio_to_fraction(interval_ratio)
    ratio_str = f"{frac.numerator}:{frac.denominator}"

    consonance = consonance_for_ratio(interval_ratio)

    return IntervalResult(
        band_a=band_a,
        band_b=band_b,
        ratio=interval_ratio,
        ratio_str=ratio_str,
        cents=cents,
        interval_name=interval_name,
        step_distance=step_dist,
        consonance_score=consonance,
    )


def harmonic_series(
    base_band: int,
    n_harmonics: int = 12,
) -> List[HarmonicNode]:
    """Generate the natural harmonic series from any base band.

    The natural harmonic series of a vibrating string has overtones at
    integer multiples of the fundamental frequency: 1f, 2f, 3f, 4f, ...
    Each harmonic is mapped to the closest band on the Monochord.

    Args:
        base_band: The fundamental band (1-72).
        n_harmonics: Number of harmonics to generate.

    Returns:
        List of HarmonicNode instances.
    """
    base_ratio = band_to_ratio(base_band)
    harmonics: List[HarmonicNode] = []

    for k in range(1, n_harmonics + 1):
        harmonic_ratio = k * base_ratio

        # Find the band closest to this harmonic ratio
        best_band = 1
        best_diff = float("inf")
        for band in range(1, 73):
            br = band_to_ratio(band)
            diff = abs(br - harmonic_ratio)
            if diff < best_diff:
                best_diff = diff
                best_band = band

        # Compute interval from fundamental
        cents_from_base = 1200.0 * math.log2(k)  # k:1 interval
        # Normalize steps
        steps = round(cents_from_base / 100.0) % 12
        interval_name = INTERVAL_NAMES[steps]
        octaves = round(cents_from_base / 100.0) // 12
        if octaves > 0:
            if steps == 0:
                # Pure octave multiple
                if octaves == 1:
                    interval_name = "Octave"
                else:
                    interval_name = f"{octaves} Octaves"
            else:
                if octaves == 1:
                    interval_name = f"Octave + {interval_name}"
                else:
                    interval_name = f"{octaves} Octaves + {interval_name}"

        # Ratio display
        frac = ratio_to_fraction(harmonic_ratio / base_ratio)
        ratio_str = f"{frac.numerator}:{frac.denominator}"

        harmonics.append(HarmonicNode(
            harmonic_number=k,
            band=best_band,
            frequency_ratio=harmonic_ratio / base_ratio,
            frequency_ratio_str=ratio_str,
            interval_name=interval_name,
            cents_from_fundamental=cents_from_base,
        ))

    return harmonics


def planetary_interval(planet: str) -> PlanetaryResult:
    """Return the Hermetic harmonic signature of a classical planet.

    Fludd mapped the seven classical planets to specific musical
    intervals within the first octave (the Planetary register).
    Each planet has a canonical ratio, a note, and a set of aligned
    bands across all six octave registers.

    Args:
        planet: Planet name (Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon).

    Returns:
        PlanetaryResult with ratio, cents, note, and band alignment.
    """
    planet = planet.title()
    if planet not in PLANETARY_DATA:
        available = ", ".join(sorted(PLANETARY_DATA.keys()))
        raise ValueError(f"Unknown planet '{planet}'. Available: {available}")

    data = PLANETARY_DATA[planet]
    step = data["step"]
    num, den = data["ratio"]
    cents = ratio_to_cents(num, den)
    note = data["note"]

    # Aligned bands: the planet's step position in every octave (0-5)
    aligned_bands = [octave * 12 + step + 1 for octave in range(6)]

    return PlanetaryResult(
        planet=planet,
        hermetic_ratio=data["hermetic_ratio"],
        cents=cents,
        musical_note=note,
        step=step,
        aligned_bands=aligned_bands,
    )


def bands_to_chord(band_list: List[int]) -> ChordResult:
    """Identify the chord formed by a set of monochord bands.

    Normalises all band ratios to a single octave, deduplicates by
    pitch class, and matches the resulting step pattern against known
    chord templates (major, minor, diminished, augmented, seventh
    chords, suspensions, quartal stacks, etc.).

    Args:
        band_list: List of band numbers (1-72).

    Returns:
        ChordResult with chord name, root, intervals, and consonance.
    """
    if not band_list:
        raise ValueError("band_list must not be empty")

    # Get the step (pitch class) for each band, deduplicate
    steps: List[int] = []
    for band in band_list:
        _, step = band_to_octave_step(band)
        if step not in steps:
            steps.append(step)
    steps.sort()

    if not steps:
        raise ValueError("No valid bands provided")

    n = len(steps)

    # Try every possible root (rotate the step pattern)
    best_match: Optional[Tuple[str, List[int], float]] = None
    best_score = -1.0

    for root_candidate in steps:
        # Rotate so root_candidate becomes 0
        rotated = sorted((s - root_candidate) % 12 for s in steps)

        for chord_name, template in CHORD_TEMPLATES:
            # Skip templates with wrong number of notes (allow subsets as simpler chords)
            if len(template) > n:
                continue
            # For exact matching, only consider templates with same note count
            if len(template) != n:
                continue

            if rotated == sorted(template):
                # Score: prefer simpler chords (fewer notes) for tie-breaking
                score = 1.0 / len(template)
                if score > best_score:
                    best_score = score
                    best_match = (chord_name, rotated, template)

    if best_match is None:
        # Fallback: report the step pattern as a raw description
        chord_name = f"Custom ({n}-note cluster)"
        pattern = steps
    else:
        chord_name, pattern, _ = best_match
        # Find which band is the root
        root_step = min(s for s in steps if s == (pattern[0] if pattern else 0))

    # Root band: the band in band_list with the matching step at the lowest octave
    root_band = None
    root_octave = 99
    for band in band_list:
        _, step = band_to_octave_step(band)
        octave, _ = band_to_octave_step(band)
        if step == pattern[0] and octave < root_octave:
            root_octave = octave
            root_band = band
    if root_band is None:
        root_band = band_list[0]

    # Build interval descriptors
    intervals: List[str] = []
    for i, p in enumerate(pattern):
        if i > 0:
            num, den = CHROMATIC_RATIOS[p]
            intervals.append(f"{INTERVAL_NAMES[p]} ({num}:{den})")
        else:
            intervals.append(f"Root ({INTERVAL_NAMES[p]})")

    # Overall chord consonance: average of all pairwise consonances
    pairwise_scores: List[float] = []
    for i in range(len(band_list)):
        for j in range(i + 1, len(band_list)):
            ratio_a = band_to_ratio(band_list[i])
            ratio_b = band_to_ratio(band_list[j])
            interval = max(ratio_a, ratio_b) / min(ratio_a, ratio_b)
            pairwise_scores.append(consonance_for_ratio(interval))
    avg_consonance = sum(pairwise_scores) / len(pairwise_scores) if pairwise_scores else 1.0

    root_note = CHROMATIC_NOTE_NAMES[pattern[0]]

    return ChordResult(
        chord_name=chord_name,
        root_band=root_band,
        root_note=root_note,
        intervals=intervals,
        step_pattern=pattern,
        consonance=avg_consonance,
    )


def harmonic_map() -> List[BandDivision]:
    """Return the complete 72-band harmonic register.

    Convenience wrapper around monochord_divisions(72).

    Returns:
        List of BandDivision for all 72 bands.
    """
    return monochord_divisions(72)


def band_consonance(band_a: int, band_b: int) -> float:
    """Compute the consonance score (0.0–1.0) between two bands.

    Higher scores indicate more consonant (pleasing) intervals.
    The score is based on the simplicity of the frequency ratio
    between the two bands.

    Args:
        band_a: First band number (1-72).
        band_b: Second band number (1-72).

    Returns:
        Consonance score from 0.0 (maximally dissonant) to 1.0 (perfectly consonant).
    """
    ratio_a = band_to_ratio(band_a)
    ratio_b = band_to_ratio(band_b)
    interval_ratio = max(ratio_a, ratio_b) / min(ratio_a, ratio_b)
    return consonance_for_ratio(interval_ratio)


# ──────────────────────────────────────────────────────────────────────
# DEMO / MAIN
# ──────────────────────────────────────────────────────────────────────

def _demo_header(text: str) -> None:
    """Print a formatted demo section header."""
    width = 72
    print()
    print("═" * width)
    print(f"  {text}")
    print("═" * width)


def _demo_sub(text: str) -> None:
    """Print a formatted demo sub-header."""
    print(f"\n── {text} ──")


def demo_full_harmonic_map() -> None:
    """Print the complete 72-band harmonic register as a formatted table."""
    _demo_header("1. THE 72-BAND HARMONIC MAP")
    print(f"{'Band':>4} │ {'Oct':>3} │ {'Step':>4} │ {'Ratio (n:d)':>14} │ {'Cents':>8} │ {'Freq (Hz)':>10} │ {'Interval':<28} │ {'Association':<30} │ {'Register'}")
    print("─" * 4 + "─┼─" + "─" * 3 + "─┼─" + "─" * 4 + "─┼─" + "─" * 14 + "─┼─" + "─" * 8 + "─┼─" + "─" * 10 + "─┼─" + "─" * 28 + "─┼─" + "─" * 30 + "─┼─" + "─" * 40)

    divisions = harmonic_map()
    last_register = ""
    for d in divisions:
        # Print register separator
        if d.register != last_register:
            if last_register:
                print(" " * 4 + "│" + " " * 3 + "│" + " " * 4 + "│" + " " * 14 + "│" + " " * 8 + "│" + " " * 10 + "│" + " " * 28 + "│" + " " * 30 + "│")
            last_register = d.register

        print(
            f"{d.band:>4} │ {d.octave:>3} │ {d.step:>4} │ {d.ratio_str:>14} │ {d.cents:>8.2f} │ {d.frequency_hz:>10.2f} │ {d.interval_name:<28} │ {d.association:<30} │ {d.register}"
        )


def demo_interval_tests() -> None:
    """Test interval_for_bands with key harmonic relationships."""
    _demo_header("2. INTERVAL TESTS — interval_for_bands()")

    test_pairs = [
        (1, 12, "Octave (Band 1 → Band 12)"),
        (1, 8, "Perfect Fifth (Band 1 → Band 8)"),
        (1, 6, "Perfect Fourth (Band 1 → Band 6)"),
        (1, 5, "Major Third (Band 1 → Band 5)"),
        (1, 4, "Minor Third (Band 1 → Band 4)"),
        (1, 24, "Double Octave (Band 1 → Band 24)"),
        (8, 6, "Fifth vs Fourth (Band 8 → Band 6)"),
        (13, 25, "Octave in higher register"),
        (36, 72, "Octave across far registers"),
    ]

    for band_a, band_b, desc in test_pairs:
        result = interval_for_bands(band_a, band_b)
        print(f"\n  {desc}:")
        print(f"    Ratio: {result.ratio_str} ({result.ratio:.4f})")
        print(f"    Cents: {result.cents:.2f}")
        print(f"    Interval: {result.interval_name}")
        print(f"    Step distance: {result.step_distance} semitones")
        print(f"    Consonance: {result.consonance_score:.3f}")


def demo_harmonic_series() -> None:
    """Print the natural harmonic series from band 1."""
    _demo_header("3. HARMONIC SERIES FROM BAND 1 — harmonic_series(1, 16)")

    harmonics = harmonic_series(1, n_harmonics=16)
    print(f"{'Harmonic':>9} │ {'Band':>5} │ {'Ratio':>8} │ {'Interval from Fundamental':<35} │ {'Cents':>8}")
    print("─" * 9 + "─┼─" + "─" * 5 + "─┼─" + "─" * 8 + "─┼─" + "─" * 35 + "─┼─" + "─" * 8)

    for h in harmonics:
        print(
            f"{h.harmonic_number:>9} │ {h.band:>5} │ {h.frequency_ratio_str:>8} │ {h.interval_name:<35} │ {h.cents_from_fundamental:>8.2f}"
        )


def demo_planetary_intervals() -> None:
    """Display planetary harmonic signatures."""
    _demo_header("4. PLANETARY INTERVALS — planetary_interval()")

    planet_order = ["Saturn", "Moon", "Mercury", "Venus", "Sun", "Mars", "Jupiter"]
    print(f"{'Planet':>8} │ {'Ratio':>8} │ {'Cents':>8} │ {'Note':>4} │ {'Step':>4} │ Aligned Bands (across 6 octaves)")
    print("─" * 8 + "─┼─" + "─" * 8 + "─┼─" + "─" * 8 + "─┼─" + "─" * 4 + "─┼─" + "─" * 4 + "─┼─" + "─" * 40)

    for planet in planet_order:
        result = planetary_interval(planet)
        bands_str = ", ".join(str(b) for b in result.aligned_bands)
        print(
            f"{result.planet:>8} │ {result.hermetic_ratio:>8} │ {result.cents:>8.2f} │ {result.musical_note:>4} │ {result.step:>4} │ {bands_str}"
        )

    # Show that all 7 planets form a coherent scale
    _demo_sub("Planetary Diatonic Scale (within first octave)")
    print("  C → C♯ → D → D♯ → E → F → G")
    print("  Saturn Moon Merc Venus Sun Mars Jupiter")
    print("  (1:1 → 16:15 → 9:8 → 6:5 → 5:4 → 4:3 → 3:2)")
    print()
    print("  The 7 classical planets map to 7 of the 12 chromatic notes.")
    print("  The remaining 5 notes (F♯, G♯, A, A♯, B) carry elemental")
    print("  associations: Fire, Water, Air, Aether, Omega.")


def demo_chord_generation() -> None:
    """Test bands_to_chord with various band combinations."""
    _demo_header("5. CHORD GENERATION — bands_to_chord()")

    test_chords = [
        ([1, 5, 8],          "C Major triad — bands 1,5,8 → steps [0,4,7]"),
        ([1, 4, 8],          "C Minor triad — bands 1,4,8 → steps [0,3,7]"),
        ([1, 4, 7],          "C Diminished — bands 1,4,7 → steps [0,3,6]"),
        ([1, 5, 9],          "C Augmented — bands 1,5,9 → steps [0,4,8]"),
        ([1, 8],             "C Power chord — bands 1,8 → steps [0,7]"),
        ([1, 5, 8, 11],      "C Dominant 7th — bands 1,5,8,11 → steps [0,4,7,10]"),
        ([1, 4, 8, 11],      "C Minor 7th — bands 1,4,8,11 → steps [0,3,7,10]"),
        ([1, 4, 8, 10],      "C Minor 6th — bands 1,4,8,10 → steps [0,3,7,9]"),
        ([1, 5, 8, 10],      "C Major 6th — bands 1,5,8,10 → steps [0,4,7,9]"),
        ([1, 4, 7, 10],      "C Dim 7th — bands 1,4,7,10 → steps [0,3,6,9]"),
        ([1, 4, 7, 11],      "C Half-Dim 7th — bands 1,4,7,11 → steps [0,3,6,10]"),
        ([1, 3, 8],          "C Sus2 — bands 1,3,8 → steps [0,2,7]"),
        ([1, 6, 8],          "C Sus4 — bands 1,6,8 → steps [0,5,7]"),
        ([1, 3, 5, 8],       "C Add9 — bands 1,3,5,8 → steps [0,2,4,7]"),
        ([13, 17, 20],       "C Major (octave up) — bands 13,17,20 → steps [0,4,7]"),
    ]

    for bands, desc in test_chords:
        try:
            result = bands_to_chord(bands)
            print(f"\n  {desc}:")
            print(f"    Bands: {bands}")
            print(f"    Chord: {result.root_note} {result.chord_name}")
            print(f"    Root band: {result.root_band}")
            print(f"    Step pattern: {result.step_pattern}")
            print(f"    Intervals: {' → '.join(result.intervals)}")
            print(f"    Consonance: {result.consonance:.3f}")
        except ValueError as e:
            print(f"\n  {desc}: ERROR — {e}")


def demo_consonance_matrix() -> None:
    """Show a small consonance matrix for key bands."""
    _demo_header("6. BAND CONSONANCE MATRIX — band_consonance()")

    key_bands = [1, 4, 5, 6, 7, 8, 12]

    # Header
    print(f"{'':>4}", end="")
    for b in key_bands:
        print(f"│ {b:>5} ", end="")
    print("│")
    print("─" * 4, end="")
    for _ in key_bands:
        print("┼" + "─" * 6, end="")
    print("┤")

    for ba in key_bands:
        print(f"{ba:>4} ", end="")
        for bb in key_bands:
            score = band_consonance(ba, bb)
            print(f"│ {score:.3f} ", end="")
        print("│")

    print()
    print("  Interpreting scores:")
    print("    1.000 = Unison / Octave (perfect identity)")
    print("    0.850 = Perfect Fifth (3:2)")
    print("    0.800 = Perfect Fourth (4:3)")
    print("    0.750 = Major Third (5:4)")
    print("    0.650 = Minor Third (6:5)")
    print("    0.300 = Major Second (9:8)")
    print("    0.150 = Tritone (45:32)")
    print("    0.100 = Minor Second (16:15) — most dissonant")


def demo_ratio_summary() -> None:
    """Summarise the key ratios in Fludd's system."""
    _demo_header("7. FLUDD'S KEY HARMONIC RATIOS — Summary")

    print("  Pythagorean / Hermetic Tuning Ratios used in the Monochord:")
    print()
    ratios_display = [
        ("1:1",   "Unison",        "0.00",    "Earth / Saturn — Foundation"),
        ("16:15", "Minor Second",   "111.73",  "Moon — Nearest sphere"),
        ("9:8",   "Major Second",   "203.91",  "Mercury — Messenger"),
        ("6:5",   "Minor Third",    "315.64",  "Venus — Love, harmony"),
        ("5:4",   "Major Third",    "386.31",  "Sun — Centre, light"),
        ("4:3",   "Perfect Fourth", "498.04",  "Mars — Energy, war"),
        ("45:32", "Tritone",        "590.22",  "Fire — Dynamic tension"),
        ("3:2",   "Perfect Fifth",  "701.96",  "Jupiter — Expansion, king"),
        ("8:5",   "Minor Sixth",    "813.69",  "Water — Flow, emotion"),
        ("5:3",   "Major Sixth",    "884.36",  "Air — Intellect, breath"),
        ("16:9",  "Minor Seventh",  "996.09",  "Aether — Quintessence"),
        ("2:1",   "Octave",         "1200.00", "Omega — Completion"),
    ]
    print(f"  {'Ratio':>8} │ {'Interval':<28} │ {'Cents':>8} │ Association")
    print("  " + "─" * 8 + "─┼─" + "─" * 28 + "─┼─" + "─" * 8 + "─┼─" + "─" * 35)
    for ratio, name, cents, association in ratios_display:
        print(f"  {ratio:>8} │ {name:<28} │ {cents:>8} │ {association}")

    print()
    print("  6 Octaves × 12 chromatic notes = 72 bands")
    print("  Octave ratio progression: 1:1 → 2:1 → 4:1 → 8:1 → 16:1 → 32:1 → 64:1")
    print("  Frequency range: C₂ (65.41 Hz) → C₈ (4186.01 Hz)")


def main() -> None:
    """Run the complete Fludd Monochord demonstration."""
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║   FLUDD'S MONOCHORD — Harmonic Ratio Ladder                         ║")
    print("║   Utriusque Cosmi Historia (1617–1619)                              ║")
    print("║   Robert Fludd's 72-band Monochord of the Universe                  ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    demo_ratio_summary()
    demo_interval_tests()
    demo_harmonic_series()
    demo_planetary_intervals()
    demo_chord_generation()
    demo_consonance_matrix()
    demo_full_harmonic_map()

    print()
    print("═" * 72)
    print("  Demonstration complete.")
    print("  Module is importable: from fludd_monochord import *")
    print("═" * 72)
    print()


if __name__ == "__main__":
    main()
