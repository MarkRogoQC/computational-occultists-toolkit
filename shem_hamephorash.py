#!/usr/bin/env python3
"""
SHEM HAMEPHORASH — THE 72 NAMES OF GOD ENCODER
═══════════════════════════════════════════════════════════
Three verses from Exodus 14:19-21:
Each 72 letters. Combined → 72 three-letter Names.
Each Name = one angel = one band in the 72-fold register.

"The 72 Names are the frequency channels through which
the divine speaks into matter."
  — Zohar, Shemot 2

Wired into the Code72 framework as the astrological/temporal layer:
  band(n) → Name(n) → Angel(n) → Gate(n) → Hour(n) → Season(n)
"""

import math
from datetime import datetime, timedelta

# ═══════════════════════════════════════════════════════════════════════════
# 1. THE 72 NAMES OF GOD (SHEM HAMEPHORASH)
# ═══════════════════════════════════════════════════════════════════════════
#
# Derived from Exodus 14:19-21:
#   Verse 19 (forward): 72 Hebrew letters
#   Verse 20 (backward): 72 Hebrew letters  
#   Verse 21 (forward):  72 Hebrew letters
#   Combined: Verse19[k] + Verse20[k] + Verse21[k] = 1 Name
#
# 72 three-letter Names. Each governs one of 72 angels,
# 6 per zodiac sign, one per decan.

# Format: (Name, Angel, Meaning, Band Category)
SHEM_72 = [
    # Aries (Bands 1-6) — Planetary / Initiating
    ("Vahav",      "Vehuiah",       "God who is exalted above all",                      "Planetary"),
    ("Yelay",      "Jeliel",        "God who is gracious and merciful",                  "Planetary"),
    ("Sayit",      "Sitael",        "God who is the hope of all creation",               "Planetary"),
    ("Aulam",      "Elemiah",       "God who hides and reveals",                         "Planetary"),
    ("Mashah",     "Mahasiah",      "God who saves and delivers",                        "Planetary"),
    ("Lahah",      "Lelahel",       "God who raises from the dust",                      "Planetary"),

    # Taurus (Bands 7-12) — Planetary / Stabilizing
    ("Ahaav",      "Achaiah",       "God who is patient and enduring",                   "Planetary"),
    ("Kaatav",     "Cahetel",       "God who is worshipped by creation",                 "Planetary"),
    ("Aizi",       "Haziel",        "God who is merciful to the fallen",                 "Planetary"),
    ("Aladm",      "Aladiah",       "God who forgives sins",                             "Planetary"),
    ("Lavav",      "Lauviah",       "God who is praised in heaven",                      "Planetary"),
    ("Hahayah",    "Hahaiah",       "God who is the refuge of the soul",                 "Planetary"),

    # Gemini (Bands 13-18) — Hermetic / Communicating
    ("Yazal",      "Iezalel",       "God who reunites separated souls",                  "Hermetic"),
    ("Mebah",      "Mebahel",       "God who preserves the universe",                    "Hermetic"),
    ("Vayav",      "Hariel",        "God who is the master of all forces",               "Hermetic"),
    ("Hakam",      "Hakamiah",      "God who is the source of wisdom",                   "Hermetic"),
    ("Lavay",      "Lauviah",       "God who sanctions vows",                            "Hermetic"),
    ("Kali",       "Caliel",        "God who triumphs over falsehood",                   "Hermetic"),

    # Cancer (Bands 19-24) — Hermetic / Protecting
    ("Luvah",      "Leuviah",       "God who is the God of abundance",                   "Hermetic"),
    ("Pahal",      "Pahaliah",      "God who is the redeemer of the righteous",          "Hermetic"),
    ("Nalakh",     "Nelchael",      "God who is the God of knowledge",                   "Hermetic"),
    ("Yayi",       "Yeyayel",       "God who strengthens the weak",                      "Hermetic"),
    ("Melah",      "Melahel",       "God who heals the sick",                            "Hermetic"),
    ("Hahav",      "Haheuiah",      "God who is the God of mercy",                       "Hermetic"),

    # Leo (Bands 25-30) — Religious / Radiating
    ("Nithah",     "Nithael",       "God who governs the ages",                          "Religious"),
    ("Haaah",      "Haaiah",        "God who is the God of the universe",                "Religious"),
    ("Yarat",      "Yerathel",      "God who gives light to the angels",                 "Religious"),
    ("Shaah",      "Sehehiah",      "God who heals all infirmities",                     "Religious"),
    ("Raiy",       "Reiyel",        "God who is the God of the just",                    "Religious"),
    ("Aumam",      "Omael",         "God who endures forever",                           "Religious"),

    # Virgo (Bands 31-36) — Religious / Purifying
    ("Lakab",      "Lecabel",       "God who governs vegetation",                        "Religious"),
    ("Vashar",     "Vasariah",      "God who is the God of justice",                     "Religious"),
    ("Yahu",       "Yehuiah",       "God who is the God of all virtues",                 "Religious"),
    ("Lahak",      "Lehahiah",      "God who is invoked by the penitent",                "Religious"),
    ("Kavak",      "Cavakiah",      "God who is the God of forgiveness",                 "Religious"),
    ("Manad",      "Mendael",       "God who is praised by all creatures",               "Religious"),

    # Libra (Bands 37-42) — Cosmic / Balancing
    ("Ani",        "Aniuel",        "God who is the God of elegance",                    "Cosmic"),
    ("Haam",       "Haamiah",       "God who is the God of reconciliation",              "Cosmic"),
    ("Reha",       "Rehael",        "God who protects from affliction",                  "Cosmic"),
    ("Iyaz",       "Yeiazel",       "God who comforts the afflicted",                    "Cosmic"),
    ("Hahah",      "Hahahel",       "God who is the worship of the holy",                "Cosmic"),
    ("Mikah",      "Michael",       "God who is like unto God — prince of all angels",   "Cosmic"),

    # Scorpio (Bands 43-48) — Cosmic / Transforming
    ("Vavalyah",   "Veuliah",       "God who triumphs over adversaries",                 "Cosmic"),
    ("Yelah",      "Yelahiah",      "God who governs fortune",                           "Cosmic"),
    ("Saal",       "Sealiah",       "God who moves the heart",                           "Cosmic"),
    ("Ariy",       "Ariel",         "God who is the lion of God",                        "Cosmic"),
    ("Aisal",      "Asaliah",       "God who is worthy of adoration",                    "Cosmic"),
    ("Mihah",      "Mihael",        "God who governs harmony",                           "Cosmic"),

    # Sagittarius (Bands 49-54) — Human / Expanding
    ("Vahav",      "Vahuel",        "God who is the God of ascension",                   "Human"),
    ("Dani",       "Daniel",        "God who judges with mercy",                         "Human"),
    ("Haad",       "Hadasiah",      "God who is the God of health",                      "Human"),
    ("Heeah",      "Heuiah",        "God who is the God of the faithful",                "Human"),
    ("Nuni",       "Nunael",        "God who is the God of conversion",                  "Human"),
    ("Nimah",      "Nithael",       "God who governs the senses",                        "Human"),

    # Capricorn (Bands 55-60) — Human / Structuring
    ("Mevahi",     "Mebahiah",      "God who is the God of return",                      "Human"),
    ("Poyali",     "Poyel",         "God who assists with grace",                        "Human"),
    ("Nuam",       "Nemamiah",      "God who governs fortune",                           "Human"),
    ("Yali",       "Yeyalel",       "God who hears the cry of the oppressed",            "Human"),
    ("Harak",      "Harahel",       "God who watches over children",                     "Human"),
    ("Mitzah",     "Mitzrael",      "God who protects the oppressed",                    "Human"),

    # Aquarius (Bands 61-66) — Meta / Liberating
    ("Umam",       "Umabel",        "God who governs friendship",                        "Meta"),
    ("Yahah",      "Yahhel",        "God who is the God of solitude",                    "Meta"),
    ("Anavayah",   "Anauel",        "God who grants patience",                           "Meta"),
    ("Mehe",       "Mehiel",        "God who gives life and vitality",                   "Meta"),
    ("Damabi",     "Damabiah",      "God who is the fount of wisdom",                    "Meta"),
    ("Manak",      "Menakel",       "God who protects against danger",                   "Meta"),

    # Pisces (Bands 67-72) — Meta / Completing
    ("Ayah",       "Ayauel",        "God who is the God of all ages",                    "Meta"),
    ("Shavah",     "Shebuiel",      "God who guards the just",                           "Meta"),
    ("Rana",       "Ranael",        "God who governs the stars",                         "Meta"),
    ("Yam",        "Iamiel",        "God who is the God of eternity",                    "Meta"),
    ("Hahayah",    "Hahaeiah",      "God who is the God of the universe",                "Meta"),
    ("Mavah",      "Mikael",        "God who helps the virtuous",                        "Meta"),
]


# ═══════════════════════════════════════════════════════════════════════════
# 2. PLANETARY HOURS — TIMING LAYER
# ═══════════════════════════════════════════════════════════════════════════

PLANETARY_HOURS = [
    "Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"
]

PLANETARY_GODS = {
    "Sun":     "Ra / Helios — consciousness, illumination",
    "Moon":    "Sin / Luna — intuition, cycles, emotion",
    "Mercury": "Thoth / Hermes — communication, alchemy",
    "Venus":   "Hathor / Aphrodite — love, harmony, attraction",
    "Mars":    "Sekhmet / Ares — war, force, assertion",
    "Jupiter": "Amun / Zeus — expansion, wisdom, kingship",
    "Saturn":  "Kronos — limitation, structure, time",
}

PLANETARY_COLORS = {
    "Sun":     "Gold",      # Band 17 — Hermetic rhythm
    "Moon":    "Silver",    # Band 2
    "Mercury": "Yellow",    # Band 11
    "Venus":   "Green",     # Band 6
    "Mars":    "Red",       # Band 5
    "Jupiter": "Blue",      # Band 10
    "Saturn":  "Black",     # Band 3
}

# ═══════════════════════════════════════════════════════════════════════════
# 3. THE 72 ANGEL CORRESPONDENCES
# ═══════════════════════════════════════════════════════════════════════════

# Choir hierarchy — 9 choirs × 8 = 72
ANGEL_CHOIRS = [
    "Seraphim",    # Bands 1-8    — the burning ones
    "Cherubim",    # Bands 9-16   — the guardians
    "Thrones",     # Bands 17-24  — the wheels
    "Dominions",   # Bands 25-32  — the governors
    "Virtues",     # Bands 33-40  — the power holders
    "Powers",      # Bands 41-48  — the warriors
    "Principalities", # Bands 49-56 — the rulers
    "Archangels",  # Bands 57-64  — the messengers
    "Angels",      # Bands 65-72  — the watchers
]

def get_choir(band):
    """Return the angelic choir for a 1-indexed band."""
    idx = (band - 1) // 8
    return ANGEL_CHOIRS[idx] if idx < len(ANGEL_CHOIRS) else "Unknown"


# ═══════════════════════════════════════════════════════════════════════════
# 4. THE ENCODER
# ═══════════════════════════════════════════════════════════════════════════

class ShemHaMephorash:
    """
    The 72 Names encoder and temporal mapper.
    
    Maps any band or datetime to its corresponding:
      - Name of God
      - Angel
      - Angelic choir
      - Planetary hour
      - Zodiac gate
      - Archetypal meaning
    
    Wires into the Code72 framework's BAND_NAMES and categories.
    """

    def __init__(self):
        self.names = SHEM_72  # 72 entries, 0-indexed = bands 0-71

    # ── Band Lookup ────────────────────────────────────────────────────

    def band_to_name(self, band):
        """
        Return the Shem HaMephorash Name for a given band (1-72 or 0-71).
        
        Args:
            band: Band number (1-72 or 0-71)
        
        Returns dict with:
            band, name, angel, meaning, category, zodiac, choir
        """
        idx = band - 1 if band > 0 and band <= 72 else band
        if idx < 0 or idx >= 72:
            return None
        
        name_data = self.names[idx]
        zodiac_idx = idx // 6
        zodiacs = [
            "Aries", "Taurus", "Gemini", "Cancer",
            "Leo", "Virgo", "Libra", "Scorpio",
            "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        
        return {
            "band": idx + 1,
            "name": name_data[0],
            "angel": name_data[1],
            "meaning": name_data[2],
            "category": name_data[3],
            "zodiac": zodiacs[zodiac_idx] if zodiac_idx < 12 else "Unknown",
            "choir": get_choir(idx + 1),
        }

    def name_to_band(self, name_or_angel):
        """
        Find band(s) matching a Name or Angel.
        Case-insensitive, partial matching supported.
        """
        results = []
        for i, n in enumerate(self.names):
            if name_or_angel.lower() in n[0].lower() or \
               name_or_angel.lower() in n[1].lower():
                info = self.band_to_name(i)
                if info:
                    results.append(info)
        return results

    # ── Temporal Mapping ───────────────────────────────────────────────

    def datetime_to_band(self, dt=None):
        """
        Map a datetime to the active band in the 72-fold register.
        
        Uses planetary hour + season + moon phase to determine
        which Name/angel is currently governing.
        
        Returns band info + planetary context.
        """
        if dt is None:
            dt = datetime.now()

        # Day of year (1-366)
        doy = dt.timetuple().tm_yday

        # Solar position — which 5-day period = which band
        # 72 bands × ~5.07 days each through the solar year
        solar_band = (doy // 5) % 72

        # Hour (0-23)
        hour = dt.hour

        # Planetary hour: sunrise-based
        # Simplified: hour mod 7 maps to planetary ruler
        planetary_idx = (hour % 7)
        planet = PLANETARY_HOURS[planetary_idx]

        # Combine: solar band + hour modulation
        effective_band = (solar_band + planetary_idx) % 72

        name_info = self.band_to_name(effective_band)

        return {
            "datetime": dt.isoformat(),
            "effective_band": effective_band + 1,  # 1-indexed
            "solar_band": solar_band + 1,
            "planetary_hour": planet,
            "planetary_god": PLANETARY_GODS.get(planet, ""),
            "name_info": name_info,
        }

    def today(self):
        """Get the active Name/angel for right now."""
        return self.datetime_to_band()

    # ── Zodiac Gate System ─────────────────────────────────────────────

    def zodiac_gate(self, zodiac_sign):
        """
        Return all Names/angels governing a zodiac sign (6 per sign).
        """
        zodiacs = [
            "Aries", "Taurus", "Gemini", "Cancer",
            "Leo", "Virgo", "Libra", "Scorpio",
            "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        
        if zodiac_sign.title() not in zodiacs:
            return []

        idx = zodiacs.index(zodiac_sign.title())
        start = idx * 6
        end = start + 6
        return [self.band_to_name(i) for i in range(start, end)]

    def list_all(self):
        """Return all 72 Names with full correspondences."""
        return [self.band_to_name(i) for i in range(72)]

    # ── Frequency Signature ────────────────────────────────────────────

    def name_to_72_vector(self, name_or_angel=""):
        """
        Convert a Name or angel name into a 72-band frequency vector.
        
        Uses gematria-style letter-to-number mapping:
        Each letter → position in alphabet → band assignment
        """
        if not name_or_angel:
            return [1.0 / 72] * 72  # flat baseline

        bands = [0.0] * 72
        target = name_or_angel.lower()
        total = 0.0

        for i, ch in enumerate(target):
            if ch.isalpha():
                val = ord(ch) - ord('a') + 1
                band = (i * 7 + val) % 72  # mix position + letter value
                w = val / 26.0
                bands[band] += w
                total += w

        if total > 0:
            bands = [b / total for b in bands]
        return bands

    # ── Report ─────────────────────────────────────────────────────────

    def report_name(self, band):
        """Pretty-print a single Name's full correspondences."""
        info = self.band_to_name(band)
        if not info:
            return f"No data for band {band}"

        lines = []
        lines.append(f"═" * 60)
        lines.append(f" SHEM HAMEPHORASH — BAND {info['band']}")
        lines.append(f"═" * 60)
        lines.append(f"  Name:       {info['name']}")
        lines.append(f"  Angel:      {info['angel']}")
        lines.append(f"  Meaning:    {info['meaning']}")
        lines.append(f"  Category:   {info['category']}")
        lines.append(f"  Zodiac:     {info['zodiac']}")
        lines.append(f"  Choir:      {info['choir']}")
        lines.append(f"═" * 60)
        return "\n".join(lines)

    def report_temporal(self, dt=None):
        """Pretty-print the current temporal mapping."""
        info = self.datetime_to_band(dt)
        ni = info.get("name_info", {})

        lines = []
        lines.append(f"═" * 60)
        lines.append(f" TEMPORAL GATE — {info['datetime']}")
        lines.append(f"═" * 60)
        lines.append(f"  Active Band:    {info['effective_band']}")
        lines.append(f"  Active Name:    {ni.get('name', '?')}")
        lines.append(f"  Active Angel:   {ni.get('angel', '?')}")
        lines.append(f"  Meaning:        {ni.get('meaning', '?')}")
        lines.append(f"  Zodiac Gate:    {ni.get('zodiac', '?')}")
        lines.append(f"  Angel Choir:    {ni.get('choir', '?')}")
        lines.append(f"  Planetary Hour: {info['planetary_hour']}")
        lines.append(f"  God:            {info['planetary_god']}")
        lines.append(f"═" * 60)
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
# 5. INTEGRATION TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    shm = ShemHaMephorash()

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        try:
            band = int(arg)
            print(shm.report_name(band))
        except ValueError:
            results = shm.name_to_band(arg)
            if results:
                for r in results:
                    print(shm.report_name(r["band"]))
                    print()
            else:
                print(f"No results for '{arg}'")
    else:
        # Show current temporal gate
        print(shm.report_temporal())

        print(f"\n{'═' * 60}")
        print(f" ALL 72 NAMES — QUICK REFERENCE")
        print(f"{'═' * 60}")
        for i in range(72):
            info = shm.band_to_name(i)
            print(f"  {info['band']:2d}. {info['name']:8s} → {info['angel']:12s} | {info['zodiac']:10s} | {info['choir']}")
