#!/usr/bin/env python3
"""
NAOMETRIA CALCULATOR — THE PROPHETIC ENGINE
═══════════════════════════════════════════════════════════
Implements Simon Studion's calculation methods (1604):
  Abbreviatio, Confirmatio, Divisio, Contradictionis Calamus,
  Hour↔Year, Gematria Lookup, Prophetic Date Engine

Wired into the Code72 framework at the measurement layer.

"The geometrica proportion is truth operating through number."
  — Simone Studione, inter Scorpiones
"""

import math
import json
import os
from datetime import datetime, timedelta

# ── Paths ─────────────────────────────────────────────────────────────────
CALC_DATA_PATH = os.path.join(
    os.path.dirname(__file__) if __file__ else '.',
    '..', '..', 'bookcraft', 'c_zetter', 'Naometrica Decoded',
    'naometric_calculator_data.md'
)

SIG_PATH = os.path.join(
    os.path.dirname(__file__) if __file__ else '.',
    '..', '..', 'bookcraft', 'c_zetter', 'Naometrica Decoded',
    'naometria_frequency_signature.json'
)

# ═══════════════════════════════════════════════════════════════════════════
# 1. FOUNDATIONAL CONSTANTS (from Studion's Naometria)
# ═══════════════════════════════════════════════════════════════════════════

# Core prophetic numbers
YEAR_CIRCLE    = 360       # The perfect year / full circle
GREAT_CYCLE    = 1260      # Rev 12:6 — Church in wilderness (42 months × 30)
GREAT_CYCLE_D3 = 420       # 1260 / 3 — one dove/witness period
VENUS_CYCLE    = 720       # 2 × 360 — Morning + Evening star
VENUS_TRIPLE   = 1080      # 3 × 360 — Venus in candelabra
BEAST          = 666       # The Beast's number
SEALED         = 144       # 12 × 12 — the elect
PHOENIX        = 84        # Phoenix cycle (86 theological → 84)
JACOBS_LADDER  = 130       # Selam gematria — master key

# Star numbers
TYCHO_STAR     = 1572      # γ Cassiopeiae, Nov 1572
STAR_VISIBILITY = 30       # 1572 → 1602
STAR_COMPLETE  = 1602      # 1572 + 30

# Chronological pivots
CHRIST_BIRTH   = 3963      # World year
CHRIST_CRUCIFY = 3996      # World year = AD 34
PIVOT_1543     = 1543      # Virga Ferrea — pivot year
NAOMETRIA_YEAR = 1604      # Written
BABYLON_FALLS  = 1620      # 💥 One faith begins
TERMINAL_YEAR  = 1878      # Terminal star point

# Contradiction pairs (Studion's truth-from-opposites method)
CONTRADICTION_PAIRS = {
    106: 1601,    # Hasmona/Vienna
    112: 1612,    # Henry IV
    801: 2,       # Alpha = 801, reversed
    1572: 1602,   # Star → Star Complete (30 years)
    1590: 1620,   # Abbreviatio → Babylon falls (30 years)
    1620: 1620,   # Self-confirming
    43: 86,       # 1543 cycle
    303: 43,      # Bicorn root
    372: 1218,    # Scorpion character
}

# Hour↔Year conversion table
HOUR_YEAR_TABLE = {
    12:    0.5,
    24:    1,
    120:   5,
    240:   10,
    720:   30,
    960:   40,
    1440:  60,
    2880:  120,
    4320:  180,
    6480:  270,
    9360:  390,
}

# ═══════════════════════════════════════════════════════════════════════════
# 2. GEMATRIA DATABASE (extracted from Naometria alphabetical index)
# ═══════════════════════════════════════════════════════════════════════════

GEMATRIA_PAPAL = {
    "Rome":         (78, "Seven hills / Root of Roman Babylon"),
    "Rome_found":   (791, "Rome foundation gematria"),
    "Rome_alt":     (793, "Rome foundation gematria (alt)"),
    "Papal_power":  (1566, "Papal power projection"),
    "Rodolph_year": (1576, "Rodolph's year"),
    "Calendar_ref": (1582, "Calendar reform"),
    "Rome_1590":    (2340, "Rome 2340 = Christ 1590"),
    "Rome_world":   (4800, "Rome world-year"),
}

GEMATRIA_STONES = {
    "Lapis":         501,
    "Sapphire":     1166,
    "Chaledon":     1515,
    "Smaragdus":     619,
    "Sardonyx":      885,
    "Sardius":       585,
    "Christophilus": 1689,
    "Beryllus":      460,
    "Topazius":      568,
    "Crisolitus":   2021,
    "Heliacisthius": 760,
    "Amethistus":   1225,
}

GEMATRIA_CROSS = {
    "Rodolph_crux":       (208, 242, 505),
    "Jacob_crossed":      (720, 740, 631, 260),
    "Esdol_HenryIV":      (196, 242, 277),
    "Davidic_cherub":     (346, 672),
}

SCORPION_NUMBERS = {
    "Babylon_root":           (372, "Character Scorpionum root — Babylon's destruction"),
    "Babylon_destruction":    (1218, "Scorpion character — final blow"),
    "Star_cycle_seal":        (10800, "30 × 360 — Star cycle + seal"),
    "Thau_cross":             (400, "Ezekiel 9:4 — Cross mark of God"),
    "Total_sealing":          (12400, "10800 + 400 — Total sealing work"),
    "Sealing_duration_hours": (960, "40 days — Duration of sealing"),
    "Venus_candelabrum":      (1080, "Venus triplicity — Candelabrum"),
    "Mars_war":               (600, "Mars triplicity — War"),
    "Luna_crescent":          (1560, "Luna triplicity — Crescent"),
    "Double_confirmation":    (3240, "2 × 1620 — Double confirmation"),
    "Scorpion_domain":        (240, "Book of tribulation — Scorpion domain"),
}

# World-year calculation constants
WORLD_YEARS = {
    "adam_creation":   0,
    "enoch":           987,
    "abraham_called":  2024,
    "abraham_430_end": 2453,
    "moses_born":      2573,
    "david_born":      2861,
    "david_reigns":    2883,
    "solomon_temple":  2940,
    "daniel_70_weeks": 3472,
    "christ_birth":    3963,
    "christ_crucifix": 3996,
    "christ_1590":     4680,
    "rome_world":      4800,
}

# ═══════════════════════════════════════════════════════════════════════════
# 3. CORE CALCULATION METHODS
# ═══════════════════════════════════════════════════════════════════════════

class NaometriaCalculator:
    """
    The Naometria prophetic calculation engine.
    
    Takes a date/number, runs it through Studion's method series:
    1. Abbreviatio — shorten to prophetic root
    2. Divisio — partition into component parts
    3. Confirmatio — cross-verify from multiple systems
    4. Contradictionis Calamus — find truth through opposites
    5. Gematria — number → meaning lookup
    """

    def __init__(self):
        self.history = []
        self._load_frequency_signature()

    def _load_frequency_signature(self):
        """Load the Naometria's 72-band frequency signature if available."""
        try:
            if os.path.exists(SIG_PATH):
                with open(SIG_PATH) as f:
                    sig = json.load(f)
                self.naometria_vector = sig.get("72_band_vector", [])
                self.peak_band = sig.get("peak_band", None)
            else:
                self.naometria_vector = []
                self.peak_band = None
        except Exception:
            self.naometria_vector = []
            self.peak_band = None

    # ── Abbreviatio (Shortening) ──────────────────────────────────────

    def abbreviate(self, date_val, root=30):
        """
        Abbreviatio — shorten a date by subtracting a root.
        
        Studion's rule: Date - Root = Abbreviation
        Standard root: 30 (star visibility), 1000, or variable.
        
        Returns all valid abbreviations found.
        """
        results = []
        for r in [30, 1000, 360, 420, 1260, self._find_natural_root(date_val)]:
            r = int(r) if r else None
            if not r or r <= 0:
                continue
            abbrev = date_val - r
            if abbrev > 0:
                results.append({
                    "operation": "Abbreviatio",
                    "input": date_val,
                    "root": r,
                    "result": abbrev,
                    "formula": f"{date_val} - {r} = {abbrev}",
                })
        self.history.extend(results)
        return results

    def _find_natural_root(self, n):
        """Find the most natural root for a given number."""
        for r in [STAR_VISIBILITY, YEAR_CIRCLE, GREAT_CYCLE_D3, GREAT_CYCLE, PHOENIX]:
            if n > r and n % r < 5:
                return r
        return None

    # ── Divisio (Partition) ────────────────────────────────────────────

    def divide(self, n, parts=3):
        """
        Divisio — partition a number into its component parts.
        
        Studion's typical divisions:
          1260 = 420 + 420 + 420 (3 parts)
          3240 = 1080 + 600 + 1560 (Venus/Mars/Luna triplicity)
          360 = 6 × 60 = 12 × 30
        
        Returns canonical decompositions.
        """
        results = []

        # Known canonical divisions
        known = {
            1260: [
                f"{GREAT_CYCLE_D3} + {GREAT_CYCLE_D3} + {GREAT_CYCLE_D3}",
                f"3.5 × {YEAR_CIRCLE}",
                f"42 months × 30 days",
            ],
            3240: [
                f"{VENUS_TRIPLE} + 600 + 1560",
                f"2 × {BABYLON_FALLS}",
            ],
            360: [f"6 × 60", f"12 × 30", f"30 × 12"],
            720: [f"2 × {YEAR_CIRCLE}"],
            1080: [f"3 × {YEAR_CIRCLE}"],
            1572: [f"{TYCHO_STAR}"],
        }

        if n in known:
            for d in known[n]:
                results.append({
                    "operation": "Divisio",
                    "input": n,
                    "division": d,
                    "mode": "canonical",
                })

        # General divisor analysis
        for d in [2, 3, 4, 5, 6, 7, 10, 12, 30, 60, 360]:
            if n % d == 0:
                count = n // d
                if d > 1 and count > 1 and (d <= 72 or count <= 72):
                    results.append({
                        "operation": "Divisio",
                        "input": n,
                        "division": f"{d} × {count}",
                        "mode": f"{d} equal parts of {count}",
                    })

        self.history.extend(results)
        return results

    # ── Confirmatio (Corroboration) ────────────────────────────────────

    def confirm(self, target):
        """
        Confirmatio — find this number through multiple independent systems.
        
        Studion's method: same number from different prophetic systems
        = confirmed truth.
        
        Example: 1620 from Revelation, Daniel, Star, Scorpion.
        """
        results = []

        # Known corroboration paths for each key number
        corroborations = {
            1620: [
                ("Revelation", f"{GREAT_CYCLE} + {YEAR_CIRCLE} = 1260 + 360"),
                ("Daniel", "1290 + 330"),
                ("Star", f"{TYCHO_STAR} + 48 = 1572 + 48"),
                ("Scorpion", f"3240 / 2"),
                ("Contradiction", f"{PIVOT_1543 + 77} = 1590 + 30 = 1620"),
            ],
            1260: [
                ("Revelation 12:6", "Church in wilderness, 42 months × 30 days"),
                ("Daniel 7:25", "Time, times, and half a time"),
                ("Three doves", f"420 + 420 + 420"),
            ],
            1572: [
                ("Tycho's Star", "γ Cassiopeiae supernova, November 1572"),
                ("Balaam's Star", "Numbers 24:17 — Star out of Jacob"),
                ("Rev 8:10-11", "Wormwood falls"),
                ("St. Bartholomew", "Aug 25, 1572 — same year"),
            ],
            360: [
                ("Circle", "Perfect rotation"),
                ("Year", "12 months × 30 days"),
                ("Zodiac", "12 signs × 30 degrees"),
                ("Naometria", "Basic dial"),
            ],
            720: [
                (f"Venus cycle", f"2 × {YEAR_CIRCLE} — Morning + Evening star"),
                ("Naometria", "Saracens invade Spain"),
            ],
            1080: [
                ("Venus candelabra", f"30 × 36"),
                ("Naometria", f"3 × {YEAR_CIRCLE}"),
            ],
        }

        if target in corroborations:
            for source, path in corroborations[target]:
                results.append({
                    "operation": "Confirmatio",
                    "target": target,
                    "source": source,
                    "path": path,
                    "confirmed": True,
                })

        # Try to find confirmation by computing from other systems
        # Revelation path: 1260 + 360
        if target == 1260 + 360 or target == 1620:
            results.append({
                "operation": "Confirmatio",
                "target": target,
                "source": "Revelation + Circle",
                "path": f"1260 + 360 = {1260 + 360}",
                "confirmed": target == 1260 + 360 or target in [1620],
            })

        # Star path: 1572 + (target - 1572)
        if target > TYCHO_STAR:
            star_offset = target - TYCHO_STAR
            results.append({
                "operation": "Confirmatio",
                "target": target,
                "source": "Star",
                "path": f"1572 + {star_offset} = {target}",
                "confirmed": True,
            })

        self.history.extend(results)
        return results

    # ── Contradictionis Calamus (Truth from Opposites) ─────────────────

    def contradiction(self, n):
        """
        Contradictionis Calamus — find truth through opposition.
        
        For known pairs, returns the opposite.
        For unknown numbers, tries: n → reverse digits → compute delta
        """
        results = []

        # Floats are truncated to int for digit reversal
        if isinstance(n, float):
            n = int(n)

        # Known pairs
        if n in CONTRADICTION_PAIRS:
            opposite = CONTRADICTION_PAIRS[n]
            results.append({
                "operation": "Contradictionis Calamus",
                "input": n,
                "opposite": opposite,
                "method": "known pair",
                "meaning": self._describe_contradiction(n, opposite),
            })

        # Reverse digits — Studion's method for unknown numbers
        try:
            rev = int(str(abs(n))[::-1])
        except (ValueError, TypeError):
            rev = 0
        if rev != n and rev > 0:
            delta = abs(n - rev)
            results.append({
                "operation": "Contradictionis Calamus",
                "input": n,
                "opposite": rev,
                "delta": delta,
                "method": "digit reversal",
                "note": f"{n} ⟷ {rev} = Δ{delta}",
            })

        self.history.extend(results)
        return results

    def _describe_contradiction(self, n, opp):
        """Known meanings for contradiction pairs."""
        descriptions = {
            (106, 1601): "Hasmona/Vienna — earthly to spiritual dominion",
            (112, 1612): "Henry IV — the Bourbon pivot",
            (801, 2): "Alpha reversed — Charlemagne's crown inverted = beginning of end",
            (1572, 1602): "Star appears → Star completes — 30-year witness window",
            (1590, 1620): "Abbreviatio → Fulfillment — the dove's 30-year flight",
            (1620, 1620): "Self-confirming — Babylon falls is its own proof",
            (43, 86): "1543 = Virga Ferrea — the iron rod, doubled",
            (303, 43): "Bicorn root — 303 → 43 via 260-day subtraction",
        }
        return descriptions.get((n, opp), f"Contradiction pair: {n} ⟷ {opp}")

    # ── Hour↔Year Conversion ───────────────────────────────────────────

    def hours_to_years(self, hours):
        """Convert hours to prophetic years (1 prophetic day = 1 year)."""
        days = hours / 24
        years = days
        results = [{
            "operation": "Hour↔Year",
            "input_hours": hours,
            "days": days,
            "years": years,
            "formula": f"{hours}h = {days}d = {years}y",
        }]

        # Check against known table
        for h, y in HOUR_YEAR_TABLE.items():
            if abs(hours - h) < 0.5:
                results[0]["known_match"] = f"{h}h = {y}y (table)"
                break

        self.history.extend(results)
        return results

    def years_to_hours(self, years):
        """Convert prophetic years to hours."""
        hours = years * 24
        results = {
            "operation": "Year↔Hour",
            "input_years": years,
            "hours": hours,
            "formula": f"{years}y = {hours}h",
        }
        self.history.append(results)
        return results

    # ── Prophetic Date Engine ──────────────────────────────────────────

    def compute_from_date(self, base_year, operation="all"):
        """
        Run a base year through the full prophetic calculation pipeline.
        
        Args:
            base_year: A year (e.g., current year, Tycho's star, etc.).
                       Floats are truncated to int.
            operation: "all" | "abbreviate" | "confirm" | "divide" | "contradict"
        
        Returns combined results from all applied operations.
        """
        self.history = []

        results = {
            "input_year": base_year,
            "operations": [],
        }

        if operation in ("all", "abbreviate"):
            abbrev = self.abbreviate(base_year)
            results["operations"].append({
                "name": "Abbreviatio",
                "results": abbrev,
            })

        if operation in ("all", "confirm"):
            # Try 1620 first (most confirmed number), then derived targets
            targets = [BABYLON_FALLS, base_year]
            # Also try nearby prophetic numbers
            for n in [1260, 1572, 1620, 360, 720, 1080]:
                if abs(n - base_year) < 100:
                    targets.append(n)
            for t in set(targets):
                conf = self.confirm(t)
                if conf:
                    results["operations"].append({
                        "name": "Confirmatio",
                        "target": t,
                        "results": conf,
                    })

        if operation in ("all", "divide"):
            # Try dividing the base year and nearby prophetic numbers
            for n in set([base_year, GREAT_CYCLE, VENUS_CYCLE, VENUS_TRIPLE, 3240]):
                if abs(n - base_year) < 2000:
                    divs = self.divide(n)
                    if divs:
                        results["operations"].append({
                            "name": "Divisio",
                            "target": n,
                            "results": divs,
                        })

        if operation in ("all", "contradict"):
            contr = self.contradiction(base_year)
            if contr:
                results["operations"].append({
                    "name": "Contradictionis Calamus",
                    "results": contr,
                })

        # Summary
        results["summary"] = self._summarize(base_year)

        return results

    def _summarize(self, base_year):
        """Generate a prophetic summary for a given year."""
        lines = []

        # Abbreviatio check
        for h in self.history:
            if h.get("operation") == "Abbreviatio":
                r = h.get("result", 0)
                if r in WORLD_YEARS:
                    evt = list(WORLD_YEARS.keys())[list(WORLD_YEARS.values()).index(r)]
                    lines.append(f"Abbreviates to {r} ({evt.replace('_', ' ').title()})")

        # Confirmatio check
        confirmed_targets = set()
        for h in self.history:
            if h.get("operation") == "Confirmatio" and h.get("confirmed"):
                confirmed_targets.add(h.get("target"))

        for t in sorted(confirmed_targets):
            known = {
                1620: "Babylon Falls — the one faith era begins",
                1260: "Great Cycle — Church in wilderness",
                1572: "Tycho's Star — the prophetic trigger",
                360: "The Circle — perfect year",
                720: "Venus Cycle — Morning + Evening star",
                1080: "Venus Triplicity — candelabra number",
            }
            if t in known:
                lines.append(f"Confirmed target {t}: {known[t]}")

        # Contradiction
        contradictions = [h for h in self.history if h.get("operation") == "Contradictionis Calamus"]
        if contradictions:
            for c in contradictions:
                if "opposite" in c:
                    meaning = c.get('meaning', c.get('note', ''))
                    if meaning:
                        lines.append(f"Contradiction: {c['input']} ⟷ {c['opposite']} ({meaning})")
                    else:
                        lines.append(f"Contradiction: {c['input']} ⟷ {c['opposite']}")

        # Distance from Babylon Falls
        delta = BABYLON_FALLS - base_year
        if abs(delta) < 100:
            lines.append(f"DISTANCE FROM BABYLON FALLS (1620): {'+' if delta < 0 else '-'}{abs(delta)} years")

        # Distance from Tycho's Star
        star_delta = base_year - TYCHO_STAR
        if 0 <= star_delta <= 400:
            periods = star_delta // STAR_VISIBILITY
            remainder = star_delta % STAR_VISIBILITY
            lines.append(f"Distance from Tycho's Star (1572): {star_delta} years = {periods} × {STAR_VISIBILITY}-year periods + {remainder}")

        return "; ".join(lines) if lines else "No significant prophetic correlations found."

    # ── The Great Inharmony: Compare a date to the Naometria signature ──

    def date_to_72_vector(self, date_val):
        """
        Decompose a date/number into a 72-band frequency vector.
        
        Uses the same method as math_core.sig() — band = position mod 72,
        weighted by magnitude.
        """
        if not isinstance(date_val, (int, float)):
            raise TypeError(f"NaometriaCalculator.date_to_72_vector requires int or float, got {type(date_val).__name__}")

        bands = [0.0] * 72
        # Decompose the number into individual digits for frequency analysis
        digits = [int(d) for d in str(abs(int(date_val)))]
        
        if not digits:
            return bands

        total = 0.0
        for i, d in enumerate(digits):
            w = (d / 9.0) * (1.0 / (1 + (i // 72) * 0.1))
            bands[i % 72] += w
            total += w

        if total > 0:
            bands = [b / total for b in bands]
        return bands

    def inharmony_with_naometria(self, date_val):
        """
        Measure the inharmony between a date and the Naometria's
        72-band frequency signature.
        
        Lower inharmony = more prophetically aligned with Studion's framework.
        """
        date_vec = self.date_to_72_vector(date_val)
        if not date_vec or not self.naometria_vector:
            return None

        if len(date_vec) != len(self.naometria_vector):
            raise ValueError(f"Vector length mismatch: date_vec={len(date_vec)}, naometria_vector={len(self.naometria_vector)}")

        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(date_vec, self.naometria_vector)))
        return distance

    # ── Report ─────────────────────────────────────────────────────────

    def report(self, results):
        """Pretty-print a calculation result."""
        lines = []
        lines.append(f"═" * 60)
        lines.append(f" NAOMETRIA CALCULATOR — INPUT YEAR: {results['input_year']}")
        lines.append(f"═" * 60)

        for op in results.get("operations", []):
            lines.append(f"\n── {op['name']} ──")
            for r in op.get("results", []):
                if "formula" in r:
                    lines.append(f"  {r['formula']}")
                elif "division" in r:
                    lines.append(f"  {r['input']} = {r['division']}")
                elif "path" in r:
                    source = r.get("source", "")
                    confirmed = "✓" if r.get("confirmed") else "?"
                    lines.append(f"  [{confirmed}] {source}: {r['path']}")
                elif "opposite" in r:
                    lines.append(f"  {r['input']} ⟷ {r['opposite']}: {r.get('meaning', '')}")
                elif "years" in r:
                    lines.append(f"  {r['input_hours']}h = {r['years']}y")

        if results.get("summary"):
            lines.append(f"\n── SUMMARY ──")
            lines.append(f"  {results['summary']}")

        # Inharmony check
        ih = self.inharmony_with_naometria(results["input_year"])
        if ih is not None:
            lines.append(f"\n── FREQUENCY ALIGNMENT ──")
            lines.append(f"  Distance from Naometria signature: ι = {ih:.6f}")
            if ih < 0.05:
                lines.append(f"  ✓ High alignment — this year resonates with Studion's framework")
            elif ih < 0.15:
                lines.append(f"  ~ Moderate alignment")
            else:
                lines.append(f"  No significant frequency alignment")

        lines.append(f"\n═" * 60)
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
# DEMONSTRATION
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    calc = NaometriaCalculator()

    # Known test cases from Studion
    test_years = [1572, 1604, 1620, 1878, 2026, 2027]

    if len(sys.argv) > 1:
        try:
            test_years = [int(sys.argv[1])]
        except ValueError:
            pass

    for year in test_years:
        results = calc.compute_from_date(year, operation="all")
        print(calc.report(results))
        print()
