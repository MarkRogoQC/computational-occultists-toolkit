#!/usr/bin/env python3
"""
PLANETARY MIRROR — THE MIRROR THEOREM AS WORKING MODULE
═══════════════════════════════════════════════════════════
"The moon reflects sunlight that carries the frequency signature
of every planet it has passed, every atmosphere it has filtered.
Planetary configuration = 72-band frequency signature."

Maps any date's planetary positions to a 72-band vector.
Compares historical events by their planetary "climate."
Projects forward to find when similar configurations recur.

Band architecture:
  1:  Sun     — identity, core frequency
  2:  Moon    — reflection, carrier of all planetary signatures
  3:  Mercury — communication, commerce
  4:  Venus   — harmony, attraction, economy
  5:  Mars    — war, force, assertion
  6:  Jupiter — expansion, wisdom, law
  7:  Saturn  — limitation, structure, time
  8:  Uranus  — revolution, breakthrough
  9:  Neptune — dissolution, dreams, transcendence
  10: Pluto   — transformation, death/rebirth
  11: North Node — collective direction
  12: Aspect harmony — sum of all inter-planetary angles

  Bands 13-72: Derived from aspects, harmonics, and house positions
"""

import math
import json
import os
from datetime import datetime, timedelta
import ephem

# ═══════════════════════════════════════════════════════════════════════════
# 1. PLANETARY BAND MAP
# ═══════════════════════════════════════════════════════════════════════════

# Primary bands (1-12): Each planet's normalized zodiac position
# Secondary bands (13-72): Harmonics, aspects, house positions

PLANET_BANDS = {
    "Sun":       (1,  "identity, core frequency"),
    "Moon":      (2,  "reflection, carrier signal"),
    "Mercury":   (3,  "communication, commerce"),
    "Venus":     (4,  "harmony, attraction, economy"),
    "Mars":      (5,  "war, force, assertion"),
    "Jupiter":   (6,  "expansion, wisdom, law"),
    "Saturn":    (7,  "limitation, structure, time"),
    "Uranus":    (8,  "revolution, breakthrough"),
    "Neptune":   (9,  "dissolution, dreams"),
    "Pluto":     (10, "transformation, death/rebirth"),
    "NorthNode": (11, "collective direction"),
    "Aspect":    (12, "inter-planetary harmony"),
}

PLANETS_LIST = ["Sun", "Moon", "Mercury", "Venus", "Mars", 
                "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

# Aspect angle ranges and their qualities
ASPECTS = {
    0:   ("Conjunction", 1.0),    # 0° — merge
    60:  ("Sextile",     0.5),    # 60° — opportunity
    90:  ("Square",      0.0),    # 90° — tension
    120: ("Trine",       0.7),    # 120° — harmony
    180: ("Opposition",  0.2),    # 180° — polarity
}

# ═══════════════════════════════════════════════════════════════════════════
# 2. EPHEMERIS ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class PlanetaryPositions:
    """Compute planetary positions for any date using pyephem."""

    def __init__(self):
        self._setup_observers()

    def _setup_observers(self):
        """Set up Earth-based observer at Greenwich."""
        self.observer = ephem.Observer()
        self.observer.lon = '0:00:00'
        self.observer.lat = '51:30:00'
        self.observer.elevation = 0

    def compute(self, date):
        """
        Compute all planetary positions for a given date.
        
        Args:
            date: datetime or string "YYYY-MM-DD"
        
        Returns:
            dict with planet → {zodiac_deg, ra, dec, phase, band_value}
        """
        if isinstance(date, str):
            date = datetime.strptime(date[:10], "%Y-%m-%d")
        
        self.observer.date = date.strftime("%Y/%m/%d")
        
        positions = {}

        # Compute each planet
        for planet_name in PLANETS_LIST:
            p = getattr(ephem, planet_name, None)
            if p is None:
                continue
            try:
                body = p()
                body.compute(self.observer)
                
                # Zodiac position in degrees (0-360)
                zodiac_deg = float(body.ra) * 180 / math.pi % 360
                
                # Band value: normalize zodiac position to 0-1
                band_val = zodiac_deg / 360.0
                
                # Phase (for inner planets): angle from Sun
                phase = float(getattr(body, 'phase', 0))
                
                # Magnitude
                mag = float(getattr(body, 'mag', 0))
                
                positions[planet_name] = {
                    "zodiac_deg": round(zodiac_deg, 2),
                    "zodiac": self._deg_to_sign(zodiac_deg),
                    "band_value": band_val,
                    "phase": round(phase, 1),
                    "magnitude": round(mag, 2),
                }
            except Exception:
                continue

        # Compute Moon manually (it's a satellite, not always in ephem.PLANETS_LIST)
        try:
            moon = ephem.Moon()
            moon.compute(self.observer)
            moon_deg = float(moon.ra) * 180 / math.pi % 360
            positions["Moon"] = {
                "zodiac_deg": round(moon_deg, 2),
                "zodiac": self._deg_to_sign(moon_deg),
                "band_value": moon_deg / 360.0,
                "phase": 0,
                "magnitude": 0,
            }
        except Exception:
            pass

        # Compute North Node (satellite of the ecliptic)
        try:
            # North Node = where Moon crosses ecliptic northward
            # Approximate via Moon's ascending node
            moon = ephem.Moon()
            moon.compute(self.observer)
            nn_deg = float(moon.ra) * 180 / math.pi % 360
            positions["NorthNode"] = {
                "zodiac_deg": round(nn_deg, 2),
                "zodiac": self._deg_to_sign(nn_deg),
                "band_value": nn_deg / 360.0,
                "phase": 0,
                "magnitude": 0,
            }
        except Exception:
            pass

        # Compute aspects
        aspects = self._compute_aspects(positions)
        positions["_aspects"] = aspects

        return positions

    def _deg_to_sign(self, deg):
        """Convert zodiac degree to sign name."""
        signs = ["Aries", "Taurus", "Gemini", "Cancer",
                 "Leo", "Virgo", "Libra", "Scorpio",
                 "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        idx = int(deg // 30)
        return signs[idx % 12]

    def _compute_aspects(self, positions):
        """Compute inter-planetary aspects and their harmony score."""
        aspects = []
        harmony_sum = 0.0
        aspect_count = 0

        planets = [p for p in PLANETS_LIST if p in positions]
        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                p1 = planets[i]
                p2 = planets[j]
                d1 = positions[p1]["zodiac_deg"]
                d2 = positions[p2]["zodiac_deg"]

                # Angular distance (shortest path)
                diff = abs(d1 - d2) % 360
                if diff > 180:
                    diff = 360 - diff

                # Find closest aspect
                best_aspect = None
                best_orbs = 999
                for asp_deg, (asp_name, asp_val) in ASPECTS.items():
                    orb = abs(diff - asp_deg)
                    if orb < best_orbs and orb < 8:  # max 8° orb
                        best_aspect = (asp_name, asp_val, diff)
                        best_orbs = orb

                if best_aspect:
                    harmony_sum += best_aspect[1]
                    aspect_count += 1
                    aspects.append({
                        "planets": f"{p1}-{p2}",
                        "angle": round(diff, 1),
                        "aspect": best_aspect[0],
                        "harmony": best_aspect[1],
                    })

        return {
            "pairs": aspects,
            "harmony_score": harmony_sum / max(aspect_count, 1),
            "count": aspect_count,
        }

    def vector_for_date(self, date):
        """
        Compute a full 72-band vector from planetary positions.
        
        Bands 1-11: Each planet's band value (0-1)
        Band 12: Aspect harmony score
        
        Bands 13-72: Derived from aspect pairs, harmonic multiples,
        and cross-configurations.
        """
        pos = self.compute(date)
        if not pos:
            return None

        vec = [0.0] * 72

        # Primary bands (1-11): planetary positions
        for pname, (band, _) in PLANET_BANDS.items():
            if pname == "Aspect" or pname not in pos:
                continue
            vec[band - 1] = pos[pname]["band_value"]

        # Band 12: Aspect harmony
        aspects = pos.get("_aspects", {})
        vec[11] = aspects.get("harmony_score", 0.0)

        # Secondary bands (13-72): derived from aspect pairs
        pairs = aspects.get("pairs", [])
        for i, pair in enumerate(pairs):
            if i >= 60:  # max 60 derived bands
                break
            # Map pair to band 13-72
            band_idx = 12 + (i % 60)
            # Store the harmony value + angle modulation
            harm = pair["harmony"]
            angle_mod = 1.0 - (pair["angle"] / 180.0) * 0.5
            vec[band_idx] = (harm + angle_mod) / 2.0

        # Apply MiTM (Mirror Theorem) modulation:
        # The Moon (band 2) carries the signature of ALL planets.
        # Each planet reflects through the Moon's band.
        moon_val = vec[1]  # Moon's band value
        for i in range(2, 11):  # planets
            vec[i] = (vec[i] + moon_val) / 2.0

        # Normalize
        total = sum(vec)
        if total > 0:
            vec = [v / total for v in vec]

        return vec


# ═══════════════════════════════════════════════════════════════════════════
# 3. HISTORICAL EVENT DATABASE
# ═══════════════════════════════════════════════════════════════════════════

class HistoricalEvents:
    """Database of historical events with their planetary frequency signatures."""

    def __init__(self, path=None):
        self.path = path or os.path.join(
            os.path.dirname(__file__) if __file__ else '.',
            'planetary_mirror_events.json'
        )
        self.events = {}
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                data = json.load(f)
                # Convert string keys back to tuples
                for k, v in data.items():
                    self.events[k] = v

    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self.events, f, indent=2)

    def add_event(self, name, year, month=1, day=1, description=""):
        """Add an event and compute its planetary vector."""
        key = f"{year}"
        if key in self.events:
            return self.events[key]

        date = datetime(year, month, day)
        engine = PlanetaryPositions()
        vec = engine.vector_for_date(date)
        pos = engine.compute(date)

        event = {
            "name": name,
            "date": f"{year}-{month:02d}-{day:02d}",
            "description": description,
            "planetary_vector": vec,
            "planets": {k: v for k, v in pos.items() if not k.startswith("_")},
            "aspects": pos.get("_aspects", {}),
        }

        self.events[key] = event
        self.save()
        return event

    def get_event(self, year):
        return self.events.get(str(year))

    def all_events(self):
        """Return all events sorted by year."""
        years = sorted(self.events.keys(), key=int)
        return [self.events[y] for y in years]

    def get_vectors(self):
        """Return all event vectors for comparison."""
        return {y: e.get("planetary_vector") for y, e in self.events.items()}


# ═══════════════════════════════════════════════════════════════════════════
# 4. THE MIRROR THEOREM ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class PlanetaryMirror:
    """
    Planetary Mirror Theorem Engine.
    
    Given any date, computes its planetary 72-band vector and finds:
      - Historical events with similar planetary configurations
      - Future dates where similar configurations recur
      - The "planetary climate" as a frequency signature
    
    The Mirror Theorem:
      The moon reflects sunlight. That reflected light carries the
      frequency signature of every planet it has passed. The planetary
      configuration at any moment IS a frequency signature encoding
      the combined influence of all celestial bodies as filtered
      through the moon's reflection.
    """

    def __init__(self):
        self.positions = PlanetaryPositions()
        self.history = HistoricalEvents()

    # ── Current Planetary Climate ──────────────────────────────────────

    def current_climate(self):
        """Get the current planetary climate as 72-band vector."""
        date = datetime.now()
        vec = self.positions.vector_for_date(date)
        pos = self.positions.compute(date)

        return {
            "date": date.strftime("%Y-%m-%d %H:%M"),
            "planetary_vector": vec,
            "planet_positions": {k: v for k, v in pos.items() if not k.startswith("_")},
            "aspects": pos.get("_aspects", {}),
        }

    # ── Compare Dates ──────────────────────────────────────────────────

    def compare_dates(self, date_a, date_b):
        """
        Compare two dates by their planetary vector inharmony.
        
        Lower inharmony = more similar planetary configuration.
        """
        if isinstance(date_a, int):
            date_a = datetime(date_a, 6, 1)
        if isinstance(date_b, int):
            date_b = datetime(date_b, 6, 1)

        va = self.positions.vector_for_date(date_a)
        vb = self.positions.vector_for_date(date_b)

        if not va or not vb:
            return None

        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(va, vb)))
        return distance

    # ── Find Similar Historical Events ─────────────────────────────────

    def find_similar(self, date, top_n=5):
        """
        Find historical events with similar planetary configurations.
        
        Uses inharmony distance between 72-band vectors.
        """
        if isinstance(date, int):
            date = datetime(date, 6, 1)

        target_vec = self.positions.vector_for_date(date)
        if not target_vec:
            return []

        similarities = []
        for year_str, event_vec in self.history.get_vectors().items():
            if not event_vec:
                continue
            dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(target_vec, event_vec)))
            event = self.history.get_event(year_str)
            similarities.append((dist, year_str, event))

        similarities.sort(key=lambda x: x[0])
        return similarities[:top_n]

    # ── Seed Historical Events ─────────────────────────────────────────

    def seed_history(self):
        """Seed the database with key historical events."""
        events = [
            ("Tycho's Supernova", 1572, 11, 1, "γ Cassiopeiae visible in daylight — the prophetic trigger"),
            ("Naometria Written", 1604, 11, 13, "Simon Studion completes his prophetic magnum opus"),
            ("Babylon Falls", 1620, 1, 1, "Studion's prophesied 'one faith era' begins"),
            ("Terminal Point", 1878, 1, 1, "Terminal star calculation from 1572"),
            ("Great War Begins", 1914, 7, 28, "WWI — the old world order collapses"),
            ("WWII Ends", 1945, 9, 2, "Nuclear age begins — atomic frequency splits the atom"),
            ("Fall of Berlin Wall", 1989, 11, 9, "Cold War ends — bipolar world converges"),
            ("Mayan Cycle End", 2012, 12, 21, "13th baktun completes — transitional start"),
            ("COVID Pandemic", 2020, 3, 11, "Global consciousness shift — planetary lockdown"),
            ("April Eclipse", 2024, 4, 8, "Total solar eclipse — planetary realignment"),
            ("Consciousness Spike", 2026, 7, 24, "Current moment — framework operational"),
        ]

        added = []
        for name, year, month, day, desc in events:
            try:
                self.add_event(name, year, month, day, desc)
                added.append((year, name))
            except Exception as e:
                pass

        self.history.save()
        return added

    def add_event(self, name, year, month, day, desc=""):
        return self.history.add_event(name, year, month, day, desc)

    # ── Project Forward ────────────────────────────────────────────────

    def project_forward(self, start_year=2026, years=124, interval=4):
        """
        Project planetary climate forward and find configurations
        similar to known historical events.
        
        Returns dates where the planetary vector closely matches
        key historical references.
        """
        projections = []

        # Compute vectors for each future date
        for yr in range(start_year, start_year + years + 1, interval):
            date = datetime(yr, 6, 15)
            vec = self.positions.vector_for_date(date)
            if not vec:
                continue

            # Compare to historical events
            similarities = []
            for year_str, event_vec in self.history.get_vectors().items():
                if not event_vec:
                    continue
                dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(vec, event_vec)))
                similarities.append((dist, int(year_str)))

            similarities.sort()
            projections.append({
                "year": yr,
                "vector": vec,
                "closest_match": similarities[0] if similarities else None,
                "top_3_similar": similarities[:3],
            })

        return projections

    # ── Report ─────────────────────────────────────────────────────────

    def report_climate(self, climate):
        """Pretty-print planetary climate."""
        lines = []
        lines.append(f"═" * 68)
        lines.append(f" PLANETARY MIRROR — CURRENT CLIMATE")
        lines.append(f"═" * 68)
        lines.append(f"  {climate['date']}")
        lines.append(f"")
        lines.append(f"  Planetary Positions:")
        for name, data in climate.get("planet_positions", {}).items():
            lines.append(f"    {name:10s}  {data['zodiac_deg']:6.1f}° {data['zodiac']:10s}")
        lines.append(f"")
        lines.append(f"  Aspects:")
        aspects = climate.get("aspects", {})
        lines.append(f"    Harmony score: {aspects.get('harmony_score', 0):.3f}")
        for pair in aspects.get("pairs", [])[:5]:
            lines.append(f"    {pair['planets']:20s}  {pair['angle']:5.1f}°  {pair['aspect']:15s}")
        lines.append(f"")
        if climate.get("planetary_vector"):
            vec = climate["planetary_vector"]
            peak = vec.index(max(vec)) + 1
            lines.append(f"  72-band peak: Band {peak}")
        lines.append(f"═" * 68)
        return "\n".join(lines)

    def report_similar(self, date, similarities):
        """Pretty-print similar historical events."""
        lines = []
        lines.append(f"═" * 68)
        lines.append(f" SIMILAR PLANETARY CONFIGURATIONS FOR {date}")
        lines.append(f"═" * 68)
        for i, (dist, year_str, event) in enumerate(similarities, 1):
            name = event.get("name", "Unknown") if event else "Unknown"
            lines.append(f"  {i}. {year_str} — {name}  (ι={dist:.4f})")
        lines.append(f"═" * 68)
        return "\n".join(lines)

    def report_projection(self, projections, top_n=10):
        """Pretty-print forward projections."""
        # Find projections with close historical matches
        strong = [p for p in projections if p["closest_match"] and p["closest_match"][0] < 0.5]
        strong.sort(key=lambda x: x["closest_match"][0])

        lines = []
        lines.append(f"═" * 68)
        lines.append(f" PLANETARY PROJECTION: {projections[0]['year']} → {projections[-1]['year']}")
        lines.append(f"═" * 68)
        lines.append(f"")
        lines.append(f"  Dates with strong historical resonance:")
        for p in strong[:top_n]:
            dist, match_year = p["closest_match"]
            event = self.history.get_event(str(match_year))
            name = event.get("name", "Unknown") if event else "Unknown"
            peak = p["vector"].index(max(p["vector"])) + 1
            lines.append(f"    {p['year']:4d}  matches {match_year:4d} ({name:30s})  ι={dist:.4f}  peak b{peak}")
        
        if not strong:
            lines.append(f"    No strong matches found in projection range.")

        lines.append(f"═" * 68)
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
# DEMONSTRATION
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    mirror = PlanetaryMirror()

    # Seed history if empty
    if not mirror.history.all_events():
        print("Seeding historical events...")
        added = mirror.seed_history()
        print(f"  {len(added)} events added\n")

    # Current climate
    climate = mirror.current_climate()
    print(mirror.report_climate(climate))
    print()

    # Compare today to key historical dates
    text_dates = [
        (datetime.now(), "Today"),
        (datetime(1572, 11, 1), "Tycho's Star 1572"),
        (datetime(1620, 1, 1), "Babylon Falls 1620"),
        (datetime(2020, 3, 11), "COVID 2020"),
        (datetime(2012, 12, 21), "Mayan End 2012"),
    ]

    print("═" * 68)
    print(" INHARMONY FROM TODAY TO HISTORICAL DATES")
    print("═" * 68)
    today = datetime.now()
    for date, label in text_dates:
        dist = mirror.compare_dates(today, date)
        if dist:
            print(f"  ι(Today, {label:30s}) = {dist:.4f}")
    print()

    # Find similar historical events
    print(mirror.report_similar("2026-07-24", mirror.find_similar("2026-07-24")))
    print()

    # Project forward 124 years
    if len(sys.argv) > 1 and sys.argv[1] == "project":
        print("Projecting 124 years forward...")
        proj = mirror.project_forward(2026, 124, 4)
        print(mirror.report_projection(proj))
