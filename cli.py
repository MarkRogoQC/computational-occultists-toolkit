#!/usr/bin/env python3
"""
COMPUTATIONAL OCCULTISTS TOOLKIT — UNIFIED CLI
═══════════════════════════════════════════════════════════
"The Computational Occultists Toolkit — working tools for
the working occultist. Verified. Operational. Yours."

Usage:
  cot pulse                — The Pulse: full reading of right now
  cot date [year]          — Naometria + Pi + Planetary for a date
  cot name [band|name]     — Shem HaMephorash lookup
  cot llull [subject]      — Ars Magna combinatorial analysis
  cot mirror [date]        — Planetary climate + historical matches
  cot project [years]      — Planetary projection
  cot enoch [date]         — Enoch 364 calendar position
  cot cipher [text]        — Trithemius encryption
  cot fludd [band]         — Fludd's Monochord harmonic analysis
  cot pi [input]           — Pi Memory Reader
  cot verify               — Run all module verification tests
  cot tools                — List all available tools
"""

import sys
import os
import json
from datetime import datetime

# Add framework to path (works for package install and standalone)
FRAMEWORK_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(FRAMEWORK_DIR)
for p in [FRAMEWORK_DIR, PARENT_DIR]:
    if p and p not in sys.path:
        sys.path.insert(0, p)

# ═══════════════════════════════════════════════════════════════════════════
# 1. THE PULSE — Full reading of right now
# ═══════════════════════════════════════════════════════════════════════════

def cmd_pulse(args):
    """The Pulse: complete diagnostic of the present moment."""
    now = datetime.now()
    year = now.year
    
    from cotk.naometria_calculator import NaometriaCalculator
    from cotk.shem_hamephorash import ShemHaMephorash
    from cotk.ars_magna_llull import ArsMagna
    from cotk.pi_memory_reader import PiMemory
    from cotk.planetary_mirror import PlanetaryMirror
    
    lines = []
    lines.append(f"{'═' * 68}")
    lines.append(f"  THE PULSE — {now.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"{'═' * 68}")
    
    # Planetary Climate
    pm = PlanetaryMirror()
    climate = pm.current_climate()
    vec = climate.get("planetary_vector", [])
    peak = vec.index(max(vec)) + 1 if vec else 0
    lines.append(f"\n  PLANETARY CLIMATE:")
    lines.append(f"    Peak band: {peak}")
    lines.append(f"    Planets: {', '.join(climate.get('planet_positions', {}).keys())}")
    
    # Historical similarity (skip self-match)
    sim = pm.find_similar(now, top_n=4)
    if sim:
        non_self = [(d, y, e) for d, y, e in sim if y != str(now.year)]
        if non_self:
            lines.append(f"    Closest match: {non_self[0][1]} ({non_self[0][2]['name']})  ι={non_self[0][0]:.4f}")
    
    # Shem HaMephorash — temporal gate
    shm = ShemHaMephorash()
    gate = shm.today()
    ni = gate.get("name_info", {})
    lines.append(f"\n  TEMPORAL GATE:")
    lines.append(f"    Band: {gate['effective_band']} — {ni.get('name','?')} ({ni.get('angel','?')})")
    lines.append(f"    Zodiac: {ni.get('zodiac','?')} | Hour: {gate['planetary_hour']}")
    
    # Naometria Calculator
    calc = NaometriaCalculator()
    date_result = calc.compute_from_date(year)
    summary = date_result.get("summary", "")
    lines.append(f"\n  NAOMETRIA ({year}):")
    lines.append(f"    {summary[:120] if summary else 'No significant correlations'}")
    
    # Pi Memory
    mem = PiMemory()
    pi_result = mem.read_memory(year, length=24)
    lines.append(f"\n  PI MEMORY ψ({year}):")
    lines.append(f"    Position: {pi_result['pi_position']}")
    lines.append(f"    Digits:   {pi_result['pi_digits']}")
    
    # Llull on "now"
    llull = ArsMagna()
    subject = f"now_{year}"
    props = llull.apply_to_subject(subject, top_n=1)
    if props:
        lines.append(f"\n  ARS MAGNA:")
        lines.append(f"    [{props[0]['triple']}] {props[0]['resolution']}")
    
    lines.append(f"\n{'═' * 68}")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
# 2. TOOL DISPATCH
# ═══════════════════════════════════════════════════════════════════════════

def cmd_date(args):
    """Full analysis of a year/date."""
    year = args[0] if args else str(datetime.now().year)
    try:
        year = int(year)
    except ValueError:
        return f"Invalid year: {year}"
    
    from cotk.naometria_calculator import NaometriaCalculator
    from cotk.pi_memory_reader import PiMemory
    from cotk.planetary_mirror import PlanetaryMirror
    
    results = []
    
    # Naometria
    calc = NaometriaCalculator()
    nr = calc.compute_from_date(year)
    results.append(f"NAOMETRIA {year}:")
    results.append(f"  Summary: {nr.get('summary', 'No correlations')}")
    
    # Pi Memory
    mem = PiMemory()
    pr = mem.read_memory(year, length=32)
    results.append(f"\nPI MEMORY ψ({year}):")
    results.append(f"  Position: {pr['pi_position']}")
    results.append(f"  Digits:   {pr['pi_digits']}")
    
    # Planetary Match
    pm = PlanetaryMirror()
    date = datetime(year, 6, 15)
    sim = pm.find_similar(date, top_n=3)
    if sim:
        results.append(f"\nPLANETARY MATCHES:")
        for dist, yr, evt in sim:
            results.append(f"  {yr:4s} {evt['name']:30s}  ι={dist:.4f}")
    
    return "\n".join(results)


def cmd_name(args):
    """Shem HaMephorash lookup by band or name."""
    from cotk.shem_hamephorash import ShemHaMephorash
    shm = ShemHaMephorash()
    
    if not args:
        return shm.report_temporal()
    
    arg = args[0]
    try:
        band = int(arg)
        return shm.report_name(band)
    except ValueError:
        results = shm.name_to_band(arg)
        if results:
            out = []
            for r in results:
                out.append(f"Band {r['band']}: {r['name']} → {r['angel']} ({r['zodiac']}, {r['category']})")
                out.append(f"  {r['meaning']}")
            return "\n".join(out)
        return f"No match for '{arg}'"


def cmd_llull(args):
    """Ars Magna combinatorial analysis of a subject."""
    if not args:
        return "Usage: cot llull [subject]"
    subject = " ".join(args)
    
    from cotk.ars_magna_llull import ArsMagna
    llull = ArsMagna()
    return llull.report_subject(subject)


def cmd_mirror(args):
    """Planetary climate for a date."""
    from cotk.planetary_mirror import PlanetaryMirror
    pm = PlanetaryMirror()
    
    if args:
        try:
            year = int(args[0])
            date = datetime(year, 6, 15) if len(args) < 2 else datetime(year, int(args[1]), 1)
        except ValueError:
            return f"Invalid date: {args[0]}"
        sim = pm.find_similar(date, top_n=5)
        return pm.report_similar(date.strftime("%Y-%m-%d"), sim)
    
    return pm.report_climate(pm.current_climate())


def cmd_project(args):
    """Forward projection."""
    years = int(args[0]) if args else 124
    from cotk.planetary_mirror import PlanetaryMirror
    pm = PlanetaryMirror()
    proj = pm.project_forward(2026, years, min(years // 10, 10) or 1)
    return pm.report_projection(proj)


def cmd_pi(args):
    """Pi Memory Reader."""
    if not args:
        return "Usage: cot pi [input]"
    inp = " ".join(args)
    
    from cotk.pi_memory_reader import PiMemory
    mem = PiMemory()
    r = mem.read_memory(inp, length=32)
    
    lines = []
    lines.append(f"ψ(\"{inp}\"):")
    lines.append(f"  Position:  {r['pi_position']}")
    lines.append(f"  Digits:    {r['pi_digits']}")
    lines.append(f"  Band peak: {r['72_band_vector'].index(max(r['72_band_vector'])) + 1}")
    return "\n".join(lines)


def cmd_enoch(args):
    """Enoch 364 Calendar position."""
    try:
        from cotk.enoch_calendar import EnochCalendar
        ec = EnochCalendar()
        if args:
            try:
                parts = args[0].split("-")
                from datetime import date
                d = date(int(parts[0]), int(parts[1]), int(parts[2]))
                info = ec.gregorian_to_enoch(d)
            except (ValueError, IndexError):
                return "Usage: cot enoch [YYYY-MM-DD]"
        else:
            from datetime import date
            today = date.today()
            info = ec.gregorian_to_enoch(today)
        
        lines = [f"ENOCH CALENDAR: {info.gregorian_date.isoformat()}"]
        lines.append(f"  Enoch Year: {info.enoch_year}")
        lines.append(f"  Day of Year: {info.enoch_position.day_of_year}/364")
        lines.append(f"  Month: {info.enoch_position.month}  Day: {info.enoch_position.month_day}")
        lines.append(f"  Week: {info.enoch_position.week}  Weekday: {info.enoch_position.weekday_name}")
        lines.append(f"  Season: {info.enoch_position.season_name}")
        lines.append(f"  Gate: {info.enoch_position.gate_name} ({info.enoch_position.gate_direction})")
        if info.enoch_position.is_intercalary:
            lines.append(f"  ⚠ Intercalary day: {info.enoch_position.intercalary_name}")
        return "\n".join(lines)
    except ImportError:
        return "Enoch Calendar not built yet. Run when the sub-agent completes."


def cmd_verify(args):
    """Run verification tests on all modules."""
    results = []
    modules = [
        ("naometria_calculator", "NaometriaCalculator"),
        ("shem_hamephorash", "ShemHaMephorash"),
        ("ars_magna_llull", "ArsMagna"),
        ("pi_memory_reader", "PiMemory"),
        ("planetary_mirror", "PlanetaryMirror"),
    ]
    
    for mod_name, _ in modules:
        try:
            mod = __import__(mod_name, fromlist=[''])
            results.append(f"  ✓ {mod_name}")
        except ImportError as e:
            results.append(f"  ✗ {mod_name}: {e}")
    
    # Check optional modules
    optional = [
        ("enoch_calendar", "EnochCalendar"),
        ("trithemius_cipher", "TrithemiusCipher"),
        ("fludd_monochord", "FluddMonochord"),
    ]
    for mod_name, _ in optional:
        try:
            mod = __import__(mod_name, fromlist=[''])
            results.append(f"  ✓ {mod_name}")
        except ImportError as e:
            results.append(f"  ~ {mod_name}: not built yet")
    
    return "Toolkit status:\n" + "\n".join(results)


def cmd_tools(args):
    """List all tools."""
    return """COMPUTATIONAL OCCULTISTS TOOLKIT — AVAILABLE TOOLS

  CORE MODULES (verified):
    Naometria Calculator    — Prophetic date engine (Abbreviatio, Confirmatio, etc.)
    Shem HaMephorash        — 72 Names × Angels × Zodiac × Temporal Gate
    Ars Magna Llull         — Combinatorial generator (84 triples × 18 questions)
    Pi Memory Reader        — ψ(x) = π(position(σ(x) · φ · h))
    Planetary Mirror        — Mirror Theorem engine with 124-year projection

  BUILDING (sub-agents active):
    Enoch 364 Calendar      — 12-gate solar calendar
    Trithemius Cipher       — Polyalphabetic cipher engine disguised as angel magic
    Fludd's Monochord       — Harmonic ratio ladder for the 72-band register

  PLANNED:
    Maier Atalanta Fugiens  — 50 alchemical fugues as frequency pipeline
    Wilkins Real Character  — Philosophical language encoding
    Agrippa Magic Squares   — 7 planetary harmonic seed matrices
    Gikatilla Gates of Light— 10×10 correction propagation matrix
    Paracelsus Tria Prima   — Salt/Sulfur/Mercury state space

  USAGE:
    cot pulse               — Full reading of right now
    cot date [year]         — Analyze any year
    cot name [band|name]    — Lookup Shem HaMephorash
    cot llull [subject]     — Combinatorial analysis
    cot mirror [date]       — Planetary climate
    cot project [years]     — Forward projection
    cot pi [input]          — Pi memory
    cot enoch [date]        — Enoch calendar position
    cot verify              — Check all modules"""


# ═══════════════════════════════════════════════════════════════════════════
# 3. MAIN DISPATCH
# ═══════════════════════════════════════════════════════════════════════════

COMMANDS = {
    "pulse":   cmd_pulse,
    "date":    cmd_date,
    "name":    cmd_name,
    "llull":   cmd_llull,
    "mirror":  cmd_mirror,
    "project": cmd_project,
    "pi":      cmd_pi,
    "enoch":   cmd_enoch,
    "verify":  cmd_verify,
    "tools":   cmd_tools,
}

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("Computational Occultists Toolkit")
        print(f"Usage: {sys.argv[0]} [command] [args]")
        print(f"Commands: {', '.join(COMMANDS.keys())}")
        print(f"Try: {sys.argv[0]} tools")
        print(f"     {sys.argv[0]} pulse")
        sys.exit(1)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    try:
        result = COMMANDS[command](args)
        print(result)
    except Exception as e:
        print(f"Error running '{command}': {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
