#!/usr/bin/env python3
"""
TRACE — Event Waveform Tracing Engine
═══════════════════════════════════════════════════════════
Decompose any event into its 72-band waveform. Compare against
history, symbols, and cycles.

Pipeline: event → vector → Pi Memory + Planetary Mirror + Symbols
"""

import sys, os, json, math
from datetime import datetime

FRAMEWORK_DIR = os.path.dirname(os.path.abspath(__file__))
SYM_DB_PATH = None
for p in [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'repos', 'symbol-frequency-decoder', 'omni_translator', 'omni_symbol_db.json'),
    os.path.join(FRAMEWORK_DIR, '..', 'repos', 'symbol-frequency-decoder', 'omni_translator', 'omni_symbol_db.json'),
]:
    if os.path.exists(p):
        SYM_DB_PATH = p
        break

def sig(data: bytes) -> list:
    bands = [0.0] * 72
    if not data: return bands
    total = 0.0
    for i, b in enumerate(data):
        w = (b / 255.0) * (1.0 / (1 + (i // 72) * 0.1))
        bands[i % 72] += w; total += w
    return [b / total for b in bands] if total > 0 else bands

def event_to_vector(name, year, month=6, day=15, desc=""):
    return sig(f"{year}-{month:02d}-{day:02d}|{name}|{desc}".encode('utf-8'))


# ═══════════════════════════════════════════════════════════════════════════
# RICH HISTORICAL EVENT DATABASE
# ═══════════════════════════════════════════════════════════════════════════

HISTORICAL_EVENTS = [
    ("Persian Wars", -490, 9, "Greece vs Persia"),
    ("Peloponnesian War", -431, 4, "Athens vs Sparta"),
    ("Alexander's Empire", -336, 7, "Conquest from Greece to India"),
    ("Punic Wars", -264, 3, "Rome vs Carthage"),
    ("Fall of Western Rome", 476, 9, "Antiquity ends"),
    ("Rise of Islam", 622, 7, "Hijra — Arabia unified"),
    ("Charlemagne Crowned", 800, 12, "Holy Roman Empire"),
    ("Magna Carta", 1215, 6, "Limits on royal power"),
    ("Black Death", 1347, 10, "Feudalism breaks"),
    ("Fall of Constantinople", 1453, 5, "Ottoman age begins"),
    ("Gutenberg Bible", 1455, 2, "Printing revolution"),
    ("Columbus Lands", 1492, 10, "Two worlds collide"),
    ("Protestant Reformation", 1517, 10, "Christendom splits"),
    ("Copernicus Heliocentric", 1543, 5, "Universe recentered"),
    ("Spanish Armada", 1588, 7, "Naval power shifts"),
    ("Tycho's Supernova", 1572, 11, "Prophetic trigger"),
    ("Naometria Written", 1604, 11, "Studion completes magnum opus"),
    ("Thirty Years' War", 1618, 5, "Modern state system born"),
    ("Babylon Falls", 1620, 1, "One faith era begins"),
    ("English Civil War", 1642, 8, "Parliament vs Crown"),
    ("Newton Principia", 1687, 7, "Mechanistic universe"),
    ("American Revolution", 1776, 7, "First modern republic"),
    ("French Revolution", 1789, 7, "Monarchy to republic"),
    ("Napoleonic Wars", 1803, 5, "Nationalism born"),
    ("Darwin Origin", 1859, 11, "Evolution transforms biology"),
    ("US Civil War", 1861, 4, "Slavery abolished"),
    ("Terminal Point", 1878, 1, "Studion's terminal year"),
    ("Einstein Annus Mirabilis", 1905, 9, "E=mc², physics transformed"),
    ("Great War Begins", 1914, 7, "Old world order collapses"),
    ("Russian Revolution", 1917, 10, "Communist era begins"),
    ("Great Depression", 1929, 10, "Global economic collapse"),
    ("WWII Begins", 1939, 9, "World war"),
    ("Atomic Age", 1945, 7, "Nuclear age begins"),
    ("Cold War", 1947, 3, "Bipolar world order"),
    ("Sputnik", 1957, 10, "Space age begins"),
    ("Moon Landing", 1969, 7, "Humanity reaches another world"),
    ("Internet Born", 1969, 10, "Network age dawns"),
    ("Fall of Berlin Wall", 1989, 11, "Cold War ends"),
    ("World Wide Web", 1991, 8, "Information age explodes"),
    ("9/11 Attacks", 2001, 9, "War on Terror begins"),
    ("Global Financial Crisis", 2008, 9, "Neoliberal order cracks"),
    ("Mayan Cycle End", 2012, 12, "Transitional period begins"),
    ("COVID-19 Pandemic", 2020, 3, "Global lockdown, consciousness shift"),
    ("Ukraine Invasion", 2022, 2, "Post-Cold War order fractures"),
    ("Consciousness Spike", 2026, 7, "Framework operational"),
]


# ═══════════════════════════════════════════════════════════════════════════
# SYMBOL MATCHER
# ═══════════════════════════════════════════════════════════════════════════

class SymbolMatcher:
    def __init__(self):
        self.db = self._load_db()

    def _load_db(self):
        try:
            with open(SYM_DB_PATH) as f:
                data = json.load(f)
            return data.get('entries', data if isinstance(data, list) else [])
        except (FileNotFoundError, json.JSONDecodeError): return []

    def estimate_vector(self, entry):
        cz = entry.get("cz_ratio", 1.0)
        band = entry.get("band", 36)
        vector = [0.0] * 72
        idx = max(0, min(71, band - 1))
        vector[idx] = 1.0
        spread = max(1, int(cz * 3))
        for d in range(1, spread + 1):
            a = math.exp(-d*d/(cz*cz+0.1))*0.5
            if idx-d>=0: vector[idx-d] = a
            if idx+d<72: vector[idx+d] = a
        # Type modulation
        type_mod = {"framework":1.5,"constructed":1.4,"symbol_system":1.3,
                    "script":1.2,"proto_script":1.1,"notation":1.1,
                    "inscription":1.0,"petroglyph":0.9,"signaling":0.9,
                    "cave_art":0.8,"wayfinding":0.8,"geoglyph":0.7,"hazard":0.6}
        t = entry.get("type","")
        mod = type_mod.get(t, 1.0)
        if mod != 1.0:
            s = int((mod-1.0)*6)
            if s: vector[max(0,min(71,idx+s))] += vector[idx]*0.3
        mag = math.sqrt(sum(v*v for v in vector))
        return [v/mag for v in vector] if mag > 0 else vector

    def inharmony(self, a, b):
        return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))

    def find_matches(self, qv, top_n=10):
        m = []
        for e in self.db:
            ev = self.estimate_vector(e)
            m.append((self.inharmony(qv, ev), e))
        m.sort(key=lambda x:x[0])
        return m[:top_n]


# ═══════════════════════════════════════════════════════════════════════════
# EVENT TRACER
# ═══════════════════════════════════════════════════════════════════════════

class EventTracer:
    def __init__(self):
        self.symbols = SymbolMatcher()

    def trace(self, name, year, month=6, day=15, desc=""):
        ev = event_to_vector(name, year, month, day, desc)
        peak = ev.index(max(ev)) + 1
        
        # Symbol matches
        sym = self.symbols.find_matches(ev, top_n=8)
        # Historical waveform matches
        hist = []
        for hn, hy, hm, hd in HISTORICAL_EVENTS:
            hv = event_to_vector(hn, hy, hm, 15, hd)
            d = math.sqrt(sum((a-b)**2 for a,b in zip(ev, hv)))
            hist.append((d, hy, hn, hd))
        hist.sort(key=lambda x:x[0])
        
        # Planetary (if available)
        plan = []
        try:
            from planetary_mirror import PlanetaryMirror
            pm = PlanetaryMirror()
            for d, yr, evt in pm.find_similar(datetime(year,month,day), top_n=5):
                if evt: plan.append({"year":yr,"name":evt.get("name",yr),"inharmony":d})
        except ImportError:
            pass
        
        # Pi memory
        pi = {}
        try:
            from pi_memory_reader import PiMemory
            r = PiMemory().read_memory(f"{year}-{month:02d}-{day:02d}", 32)
            pi = {"pos":r["pi_position"],"digits":r["pi_digits"]}
        except ImportError:
            pass
        
        return {
            "event": name, "date": f"{year}-{month:02d}-{day:02d}",
            "peak_band": peak,
            "peak_register": "Planetary" if peak<=12 else "Hermetic" if peak<=24 else "Religious" if peak<=36 else "Cosmic" if peak<=48 else "Human" if peak<=60 else "Meta",
            "pi": pi,
            "planetary_matches": plan,
            "historical_waveform_matches": [{"inharmony":d,"year":y,"event":n}
                                            for d,y,n,_ in hist[:6]],
            "symbol_matches": [{"inharmony":d,"name":e.get("name","?"),"family":e.get("family","?")[:20]}
                              for d,e in sym[:6]],
        }

    def trace_event(self, name, year, month=6, day=15):
        return self.trace(name, year, month, day, "")

    def batch_trace(self, events):
        return [self.trace(n,y,m,15) for n,y,m,_ in events]

    def report(self, r):
        lines = [f"{'='*68}", f" TRACE: {r['event']} ({r['date']})", f"{'='*68}"]
        lines.append(f"  Peak band: {r['peak_band']} ({r['peak_register']})")
        pi = r.get("pi",{})
        if pi: lines.append(f"  π-memory: pos {pi['pos']}, digits {pi['digits'][:16]}...")
        lines.append(f"\n  HISTORICAL WAVEFORM MATCHES:")
        for hm in r.get("historical_waveform_matches",[])[:5]:
            lines.append(f"    ι={hm['inharmony']:.4f}  {hm['year']:5d}  {hm['event'][:50]}")
        lines.append(f"\n  PLANETARY MATCHES:")
        for pm in r.get("planetary_matches",[])[:3]:
            lines.append(f"    ι={pm['inharmony']:.4f}  {pm['year']:4s}  {pm['name'][:50]}")
        lines.append(f"\n  SYMBOL FREQUENCY MATCHES:")
        for sm in r.get("symbol_matches",[])[:4]:
            lines.append(f"    ι={sm['inharmony']:.4f}  {sm['name'][:30]:30s}  [{sm['family']}]")
        lines.append(f"{'='*68}")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    t = EventTracer()
    print(f"Symbols: {len(t.symbols.db)} entries")
    print(f"History: {len(HISTORICAL_EVENTS)} events\n")

    # Trace current war
    war = t.trace("Ukraine Invasion", 2022, 2, 24, "Russia invades Ukraine")
    print(t.report(war))
    print()

    # Trace COVID
    cov = t.trace("COVID-19", 2020, 3, 11, "Global pandemic")
    print(t.report(cov))
    print()

    # Trace 9/11
    nine = t.trace("9/11 Attacks", 2001, 9, 11, "World Trade Center falls")
    print(t.report(nine))
    print()

    # Trace 2040
    fi = t.trace("Convergence Point", 2040, 1, 1, "Babylon Falls mirror")
    print(t.report(fi))
