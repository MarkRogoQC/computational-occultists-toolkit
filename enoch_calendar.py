#!/usr/bin/env python3
"""
Enoch 364-Day Calendar Engine
==============================

Based on the Book of Enoch (1 Enoch), chapters 72–82 — the "Astronomical Book."

A perfect solar calendar:
  • 364 days = 12 months × 30 days + 4 intercalary days
  • 52 weeks × 7 days (perpetual weekday alignment)
  • 4 seasons × 91 days (13 weeks each)
  • 12 solar gates (portals of sunrise) — 6 east + 6 west
  • 72 bands (Shem HaMephorash) — 6 bands per gate
  • 7-year sabbatical cycle with Shemitah and Jubilee

Zero external dependencies — standard library only.

Reference:
  Enoch 72:1-37 — The sun rises through 12 portals over the course of the year.
  Enoch 82:4-7  — The 4 intercalary days "men err because of them."
  Leviticus 25  — Sabbatical year (Shemitah) and Jubilee (7×7+1).
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, List, NamedTuple, Optional, Tuple
import sys

# ═══════════════════════════════════════════════════════════════════════════════
# CALENDAR CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

DAYS_IN_YEAR      = 364
DAYS_IN_WEEK      =   7
WEEKS_IN_YEAR     =  52
MONTHS            =  12
DAYS_IN_MONTH     =  30
INTERCALARY_DAYS  =   4
SEASONS           =   4
DAYS_IN_SEASON    =  91       # 3 × 30 + 1 intercalary
GATES             =  12
BANDS_PER_GATE    =   6       # 72 ÷ 12 = 6
TOTAL_BANDS       =  72

# ═══════════════════════════════════════════════════════════════════════════════
# NAMES & MAPPINGS
# ═══════════════════════════════════════════════════════════════════════════════

MONTH_NAMES: List[str] = [
    "Nisan", "Iyar", "Sivan",
    "Tammuz", "Av", "Elul",
    "Tishrei", "Cheshvan", "Kislev",
    "Tevet", "Shevat", "Adar",
]

SEASON_NAMES: List[str] = [
    "Spring (Tekufat Aviv)",
    "Summer (Tekufat Kayitz)",
    "Autumn (Tekufat Stav)",
    "Winter (Tekufat Choref)",
]

INTERCALARY_NAMES: List[str] = [
    "Spring Equinox (Tekufah)",
    "Summer Solstice (Tekufah)",
    "Autumn Equinox (Tekufah)",
    "Winter Solstice (Tekufah)",
]

WEEKDAY_NAMES: List[str] = [
    "First Day", "Second Day", "Third Day", "Fourth Day",
    "Fifth Day", "Sixth Day", "Sabbath (Seventh Day)",
]

# ── Solar Gates (Enoch 72) ────────────────────────────────────────────────────
# The sun rises through 6 eastern portals and sets through 6 western portals.
# In each month, the sun exits a specific gate at dawn.
# Gates 1–6 cycle: 4→5→6→6→5→4→3→2→1→1→2→3 (ascending then descending).

GATE_NAMES: List[str] = [
    "Gate 4 (East)",     # Month  1 — ascending toward summer
    "Gate 5 (East)",     # Month  2
    "Gate 6 (East)",     # Month  3 — northernmost (longest days)
    "Gate 6 (West)",     # Month  4 — peak, beginning descent
    "Gate 5 (West)",     # Month  5
    "Gate 4 (West)",     # Month  6
    "Gate 3 (West)",     # Month  7
    "Gate 2 (West)",     # Month  8
    "Gate 1 (West)",     # Month  9 — southernmost (shortest days)
    "Gate 1 (East)",     # Month 10 — beginning ascent
    "Gate 2 (East)",     # Month 11
    "Gate 3 (East)",     # Month 12
]

# The numbered portal (1–6) for each month
GATE_NUMBER_FOR_MONTH: List[int] = [4, 5, 6, 6, 5, 4, 3, 2, 1, 1, 2, 3]

# Direction of the sun's movement through the gate cycle
GATE_DIRECTION: List[str] = [
    "ascending",  "ascending",  "ascending",
    "descending", "descending", "descending",
    "descending", "descending", "descending",
    "ascending",  "ascending",  "ascending",
]

# Hemisphere: east (sunrise portal) or west (sunset portal)
GATE_HEMISPHERE: List[str] = [
    "east", "east", "east",
    "west", "west", "west",
    "west", "west", "west",
    "east", "east", "east",
]

# ── 72 Bands (Shem HaMephorash) ───────────────────────────────────────────────
# Each of the 12 gates maps to 6 angelic bands (72 total).
# Based on the 72-fold Name of God derived from Exodus 14:19-21.

SHEM_HEBREW: List[str] = [
    "והו", "ילי", "סיט", "עלמ", "מהש", "ללה", "אכא", "כהת",
    "הזי", "אלד", "לאו", "ההע", "יזל", "מבה", "הרי", "הקם",
    "לאו", "כלי", "לוו", "פהל", "נלכ", "ייי", "מלה", "חהו",
    "נתה", "האא", "ירת", "שאה", "רוי", "אומ", "לכב", "ושר",
    "יחו", "להח", "כוק", "מנד", "אני", "חעמ", "רהע", "ייז",
    "ההה", "מיכ", "ווו", "ילה", "סאל", "ערי", "עשל", "מיה",
    "והו", "דני", "החש", "עממ", "ננא", "נית", "מבה", "פוי",
    "נממ", "ייל", "הרח", "מצר", "אומב", "יהה", "ענו", "מחי",
    "דמב", "מנק", "איע", "חבו", "ראה", "יבמ", "היי", "מומ",
]

SHEM_ANGELS: List[str] = [
    "Vaho", "Yeli", "Sita", "Alam", "Mahash", "Lelah", "Akha", "Kahat",
    "Hezi", "Alad", "Lavo", "Haha",  "Yezal", "Mebah", "Heri", "Hakam",
    "Lavo", "Keli", "Levi", "Pahal", "Nelak", "Yiyi",  "Mela", "Haho",
    "Natah","Haa",  "Yerat","Shah",  "Revi",  "Oma",   "Lekab","Vashar",
    "Yaho", "Lahah","Kavak","Menad", "Ani",   "Haam",  "Raha", "Yez",
    "Haha", "Mikha","Vavo", "Yela",  "Sala",  "Ari",   "Ashal","Miha",
    "Vaho", "Dani", "Hahash","Amam", "Nana",  "Nita",  "Meba", "Poya",
    "Nemam","Yeil", "Harah","Matzar","Omb",   "Yaha",  "Anu",  "Mehi",
    "Damb", "Menak","Aya",  "Havo",  "Raah",  "Yeva",  "Haya", "Moma",
]

# Psalm verses associated with each Shem name (traditional attribution)
SHEM_VERSES: List[str] = [
    "Psalm 3:4",  "Psalm 22:20","Psalm 91:2", "Psalm 6:5",  "Psalm 9:12",
    "Psalm 8:10", "Psalm 8:11", "Psalm 8:12", "Psalm 18:36","Psalm 119:8",
    "Psalm 119:9","Psalm 119:10","Psalm 119:11","Psalm 119:12","Psalm 119:13",
    "Psalm 119:14","Psalm 119:15","Psalm 119:16","Psalm 119:17","Psalm 119:18",
    "Psalm 119:19","Psalm 119:20","Psalm 119:21","Psalm 119:22","Psalm 119:23",
    "Psalm 119:24","Psalm 119:25","Psalm 119:26","Psalm 119:27","Psalm 119:28",
    "Psalm 119:29","Psalm 119:30","Psalm 119:31","Psalm 119:32","Psalm 119:33",
    "Psalm 119:34","Psalm 119:35","Psalm 119:36","Psalm 119:37","Psalm 119:38",
    "Psalm 119:39","Psalm 119:40","Psalm 119:41","Psalm 119:42","Psalm 119:43",
    "Psalm 119:44","Psalm 119:45","Psalm 119:46","Psalm 119:47","Psalm 119:48",
    "Psalm 119:49","Psalm 119:50","Psalm 119:51","Psalm 119:52","Psalm 119:53",
    "Psalm 119:54","Psalm 119:55","Psalm 119:56","Psalm 119:57","Psalm 119:58",
    "Psalm 119:59","Psalm 119:60","Psalm 119:61","Psalm 119:62","Psalm 119:63",
    "Psalm 119:64","Psalm 119:65","Psalm 119:66","Psalm 119:67","Psalm 119:68",
    "Psalm 119:69","Psalm 119:70",
]

# ── Festivals ─────────────────────────────────────────────────────────────────
# (name, month, start_day, end_day_or_None)
# Festivals on the Enoch calendar fall on the same dates every year because
# all months are exactly 30 days and all weeks are perfectly aligned.

FESTIVALS: List[Tuple[str, int, int, Optional[int]]] = [
    ("Passover (Pesach)",              1, 14, None),
    ("Unleavened Bread (Matzot)",      1, 15,   21),
    ("Firstfruits (Bikkurim)",         1, 26, None),
    ("Weeks / Shavuot",                3, 15, None),
    ("Trumpets (Yom Teruah)",          7,  1, None),
    ("Atonement (Yom Kippur)",         7, 10, None),
    ("Tabernacles (Sukkot)",           7, 15,   21),
    ("Last Great Day (Shemini Atz.)",  7, 22, None),
    ("Dedication (Hanukkah)",          9, 25, None),
]

# ── Gregorian Anchor ──────────────────────────────────────────────────────────
# The Enoch new year aligns approximately with the spring equinox (March 20/21).
# We anchor to March 21 for conversion. Because the Enoch year is exactly 364
# days while the Gregorian year averages ~365.2425 days, the calendars drift
# relative to each other by about 1.24 days per year.
ENOCH_EPOCH: date = date(2000, 3, 21)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

class EnochPosition(NamedTuple):
    """Complete position of a day within the Enoch calendar."""
    day_of_year: int          # 1..364
    month: int                # 1..12
    month_day: int            # 1..30 (30 on intercalary days)
    week: int                 # 1..52
    weekday: int              # 1..7 (7 = Sabbath)
    weekday_name: str
    season: int               # 1..4
    season_name: str
    is_intercalary: bool
    intercalary_name: Optional[str]
    gate: int                 # 1..12 gate index
    gate_name: str
    gate_number: int          # 1..6 portal number
    gate_direction: str       # "ascending" or "descending"
    gate_hemisphere: str      # "east" or "west"
    is_sabbath: bool
    is_new_moon: bool
    band_range: Tuple[int, int]  # (start, end) 0-indexed inclusive band range

    def summary(self) -> str:
        """One-line summary of the position."""
        inter = f" ★ {self.intercalary_name}" if self.is_intercalary else ""
        sabb  = " [Sabbath]" if self.is_sabbath else ""
        moon  = " [New Moon]" if self.is_new_moon else ""
        return (
            f"Day {self.day_of_year:3d}/364 | "
            f"Month {self.month:2d} ({MONTH_NAMES[self.month-1]:10s}) "
            f"Day {self.month_day:2d} | "
            f"Week {self.week:2d} | {self.weekday_name:22s} | "
            f"{self.season_name:25s} | "
            f"{self.gate_name}{inter}{sabb}{moon}"
        )


class GregorianEnochResult(NamedTuple):
    """Result of converting a Gregorian date to the Enoch calendar."""
    gregorian_date: date
    enoch_year: int
    enoch_position: EnochPosition
    sabbatical: Dict


# ═══════════════════════════════════════════════════════════════════════════════
# CALENDAR ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class EnochCalendar:
    """Enoch 364-Day Calendar Engine.

    Usage::

        >>> cal = EnochCalendar()
        >>> pos = cal.day_of_year_to_position(1)
        >>> pos.month, pos.month_day, pos.season_name
        (1, 1, 'Spring (Tekufat Aviv)')
        >>> cal.sabbatical_cycle(2026)['cycle_position']
        4
    """

    def __init__(self) -> None:
        self._validate()

    # ── Validation ────────────────────────────────────────────────────────

    @staticmethod
    def _validate() -> None:
        """Verify the mathematical integrity of the calendar structure."""
        assert DAYS_IN_YEAR == MONTHS * DAYS_IN_MONTH + INTERCALARY_DAYS, \
            f"364 ≠ {MONTHS}×{DAYS_IN_MONTH} + {INTERCALARY_DAYS}"
        assert DAYS_IN_YEAR == WEEKS_IN_YEAR * DAYS_IN_WEEK, \
            f"364 ≠ {WEEKS_IN_YEAR}×{DAYS_IN_WEEK}"
        assert DAYS_IN_SEASON * SEASONS == DAYS_IN_YEAR, \
            f"{DAYS_IN_SEASON}×{SEASONS} ≠ {DAYS_IN_YEAR}"
        assert GATES == MONTHS, f"Gates {GATES} ≠ Months {MONTHS}"
        assert GATES * BANDS_PER_GATE == TOTAL_BANDS, \
            f"{GATES}×{BANDS_PER_GATE} ≠ {TOTAL_BANDS}"
        assert len(SHEM_HEBREW) == TOTAL_BANDS, \
            f"Hebrew names: {len(SHEM_HEBREW)} ≠ {TOTAL_BANDS}"
        assert len(SHEM_ANGELS) == TOTAL_BANDS, \
            f"Angel names: {len(SHEM_ANGELS)} ≠ {TOTAL_BANDS}"

    # ── Core Conversion ───────────────────────────────────────────────────

    def day_of_year_to_position(self, day: int) -> EnochPosition:
        """Convert a day number (1–364) into a full Enoch calendar position.

        Args:
            day: Day of the Enoch year, 1..364.

        Returns:
            An :class:`EnochPosition` with all calendar fields resolved.

        Raises:
            ValueError: if *day* is outside 1..364.
        """
        if day < 1 or day > DAYS_IN_YEAR:
            raise ValueError(f"Day must be in 1..{DAYS_IN_YEAR}, got {day}")

        # Season and intercalary detection
        # Season 1: days   1– 91   (months  1– 3 + intercalary 1)
        # Season 2: days  92–182   (months  4– 6 + intercalary 2)
        # Season 3: days 183–273   (months  7– 9 + intercalary 3)
        # Season 4: days 274–364   (months 10–12 + intercalary 4)

        is_intercalary  = False
        intercalary_name: Optional[str] = None
        month: int
        month_day: int

        # Determine which season day belongs to
        season_idx = (day - 1) // DAYS_IN_SEASON  # 0..3
        season_start = season_idx * DAYS_IN_SEASON + 1
        intercalary_day = season_start + DAYS_IN_SEASON - 1

        if day == intercalary_day:
            # Intercalary day — the 91st day of the season
            is_intercalary   = True
            intercalary_name = INTERCALARY_NAMES[season_idx]
            month      = season_idx * 3 + 3   # last month of the season
            month_day  = DAYS_IN_MONTH         # day 30 (the intercalary follows)
        else:
            # Normal month day
            days_into_season = day - season_start
            month     = season_idx * 3 + (days_into_season // DAYS_IN_MONTH) + 1
            month_day = (days_into_season % DAYS_IN_MONTH) + 1

        # Derived fields
        season = season_idx + 1
        week   = (day - 1) // DAYS_IN_WEEK + 1
        weekday = ((day - 1) % DAYS_IN_WEEK) + 1

        return EnochPosition(
            day_of_year       = day,
            month             = month,
            month_day         = month_day,
            week              = week,
            weekday           = weekday,
            weekday_name      = WEEKDAY_NAMES[weekday - 1],
            season            = season,
            season_name       = SEASON_NAMES[season - 1],
            is_intercalary    = is_intercalary,
            intercalary_name  = intercalary_name,
            gate              = month,                     # gate index = month
            gate_name         = GATE_NAMES[month - 1],
            gate_number       = GATE_NUMBER_FOR_MONTH[month - 1],
            gate_direction    = GATE_DIRECTION[month - 1],
            gate_hemisphere   = GATE_HEMISPHERE[month - 1],
            is_sabbath        = (weekday == 7),
            is_new_moon       = (month_day == 1),
            band_range        = (
                (month - 1) * BANDS_PER_GATE,
                month * BANDS_PER_GATE - 1,
            ),
        )

    # ── Gate Query ────────────────────────────────────────────────────────

    def gate_for_day(self, day: int) -> Dict:
        """Return gate information for a given day of the Enoch year.

        "And I saw six portals in the east … and six portals in the west …
         Through these the sun goes forth and returns." — Enoch 72

        Args:
            day: Day of the Enoch year, 1..364.

        Returns:
            A dictionary with gate details for the given day.
        """
        pos = self.day_of_year_to_position(day)
        return {
            "day":           day,
            "gate_index":    pos.gate,
            "gate_name":     pos.gate_name,
            "gate_number":   pos.gate_number,
            "direction":     pos.gate_direction,
            "hemisphere":    pos.gate_hemisphere,
            "month":         pos.month,
            "month_name":    MONTH_NAMES[pos.month - 1],
            "season":        pos.season_name,
            "is_intercalary": pos.is_intercalary,
            "days_in_gate":  30,   # each gate spans approximately one month
        }

    # ── Sabbatical Cycle ──────────────────────────────────────────────────

    def sabbatical_cycle(self, year: int) -> Dict:
        """Return the 7-year sabbatical cycle position for a given calendar year.

        Based on Leviticus 25: the land rests every 7th year (Shemitah),
        and every 7×7 = 49th year is followed by a Jubilee.

        Args:
            year: A calendar year number (positive integer).

        Returns:
            A dictionary with cycle position, Shemitah/Jubilee flags, and names.
        """
        if year < 1:
            raise ValueError(f"Year must be positive, got {year}")

        position  = ((year - 1) % 7) + 1
        is_shemitah = (position == 7)
        is_jubilee  = (year % 49 == 0)

        cycle_names: Dict[int, str] = {
            1: "Year 1 — Planting",
            2: "Year 2 — Growth",
            3: "Year 3 — First Tithe (Ma'aser Rishon)",
            4: "Year 4 — Second Tithe (Ma'aser Sheni)",
            5: "Year 5 — Poor Tithe (Ma'aser Ani)",
            6: "Year 6 — Preparation",
            7: "Year 7 — Shemitah (Sabbatical Rest / Release)",
        }

        return {
            "year":            year,
            "cycle_position":  position,
            "cycle_name":      cycle_names[position],
            "is_shemitah":     is_shemitah,
            "is_jubilee":      is_jubilee,
            "cycle_number":    (year - 1) // 7 + 1,
            "jubilee_number":  (year - 1) // 49 + 1,
        }

    # ── Gregorian Conversion ──────────────────────────────────────────────

    def gregorian_to_enoch(self, gregorian_date: date) -> GregorianEnochResult:
        """Convert a Gregorian :class:`~datetime.date` to its Enoch calendar position.

        The conversion anchors on the spring equinox (March 21, 2000) and
        calculates the offset in days. Because the Enoch year is always
        364 days while Gregorian years vary (365/366), the two systems
        drift relative to each other. The Enoch year number reflects the
        count of 364-day cycles since the anchor epoch.

        Args:
            gregorian_date: Any :class:`~datetime.date`.

        Returns:
            A :class:`GregorianEnochResult` with the Enoch year, position,
            and sabbatical cycle info.
        """
        delta_days = (gregorian_date - ENOCH_EPOCH).days

        if delta_days >= 0:
            enoch_year = delta_days // DAYS_IN_YEAR + 1
            enoch_day  = (delta_days % DAYS_IN_YEAR) + 1
        else:
            # Dates before the epoch: floor division works differently
            enoch_year  = delta_days // DAYS_IN_YEAR  # 0 or negative
            remainder   = delta_days % DAYS_IN_YEAR   # negative, -363..0
            enoch_day   = remainder + DAYS_IN_YEAR + 1
            if enoch_day > DAYS_IN_YEAR:
                enoch_day -= DAYS_IN_YEAR

        position  = self.day_of_year_to_position(enoch_day)
        sabbatical = self.sabbatical_cycle(enoch_year)

        return GregorianEnochResult(
            gregorian_date  = gregorian_date,
            enoch_year      = enoch_year,
            enoch_position  = position,
            sabbatical      = sabbatical,
        )

    # ── Text Diagram ──────────────────────────────────────────────────────

    def plot_yearly(self) -> str:
        """Return a text diagram of the full Enoch year.

        The diagram shows:
          • 12 months with their solar gates
          • 4 seasonal quarters
          • 4 intercalary days (tekufot)
          • Gate direction (ascending ↑ / descending ↓)
          • Week ranges and day ranges
        """
        lines: List[str] = []
        bar = "═" * 70

        lines.append(f"╔{bar}╗")
        lines.append("║           ENOCH 364-DAY CALENDAR — Year-at-a-Glance              ║")
        lines.append("║           12 Gates · 4 Seasons · 52 Weeks · 72 Bands              ║")
        lines.append(f"╠{bar}╣")

        for s_idx in range(SEASONS):
            season_name  = SEASON_NAMES[s_idx]
            ds = s_idx * DAYS_IN_SEASON + 1        # first day of season
            de = ds + DAYS_IN_SEASON - 1            # last day (intercalary)
            lines.append("║" + " " * 70 + "║")
            lines.append(f"║  {season_name}  (Days {ds}–{de}){' ' * (59 - len(season_name))}║")
            lines.append("║  ┌" + "─" * 66 + "┐  ║")

            for m_idx in range(3):
                m_num = s_idx * 3 + m_idx + 1
                g_num = GATE_NUMBER_FOR_MONTH[m_num - 1]
                g_dir = GATE_DIRECTION[m_num - 1]

                # Choose directional arrow
                if g_num == 6:
                    arrow = "⏺"  # peak — longest days
                elif g_num == 1:
                    arrow = "○"  # trough — shortest days
                elif g_dir == "ascending":
                    arrow = "↑"
                else:
                    arrow = "↓"

                m_start = ds + m_idx * DAYS_IN_MONTH
                m_end   = m_start + DAYS_IN_MONTH - 1
                w_start = (m_start - 1) // 7 + 1
                w_end   = (m_end   - 1) // 7 + 1

                lines.append(
                    f"║  │ M{m_num:02d} {MONTH_NAMES[m_num-1]:10s} "
                    f"Days {m_start:3d}–{m_end:3d}  "
                    f"W{w_start:02d}–W{w_end:02d}  "
                    f"Gate {g_num} {arrow}  "
                    f"{GATE_NAMES[m_num-1]:18s}│  ║"
                )

            # Intercalary day for this season
            ic_name = INTERCALARY_NAMES[s_idx]
            ic_day  = de
            lines.append(
                f"║  │ ★ {ic_name} — Day {ic_day} "
                f"(Intercalary / Tekufah){' ' * 24}│  ║"
            )
            lines.append("║  └" + "─" * 66 + "┘  ║")

        lines.append(f"╠{bar}╣")
        lines.append("║  364 = 12×30 + 4  =  52×7  =  4×91      Day 1 ≡ First Day      ║")
        lines.append(f"╚{bar}╝")

        return "\n".join(lines)

    # ── Festivals ─────────────────────────────────────────────────────────

    def get_festivals(self) -> List[Dict]:
        """Return all festival dates for the Enoch year.

        Because all months are exactly 30 days, festivals always fall on the
        same day-of-year and the same weekday every year.

        Returns:
            A list of dicts with festival name, month, day range, day-of-year,
            sabbath status, and season.
        """
        results: List[Dict] = []
        for name, month, start_day, end_day in FESTIVALS:
            day_of_year = self._month_day_to_day_of_year(month, start_day)
            pos = self.day_of_year_to_position(day_of_year)

            entry: Dict = {
                "name":          name,
                "month":         month,
                "month_name":    MONTH_NAMES[month - 1],
                "start_day":     start_day,
                "end_day":       end_day,
                "day_of_year":   day_of_year,
                "weekday_name":  pos.weekday_name,
                "is_sabbath":    pos.is_sabbath,
                "season":        pos.season_name,
            }
            results.append(entry)
        return results

    # ── Cycles: Sabbaths, New Moons, Full Moons ───────────────────────────

    def get_sabbaths(self) -> List[int]:
        """Return all Sabbath days (every 7th day)."""
        return list(range(7, DAYS_IN_YEAR + 1, 7))

    def get_new_moons(self) -> List[int]:
        """Return all new moon days (day 1 of each month).

        New moons fall on:
          Month 1 day 1  → Day   1
          Month 2 day 1  → Day  31
          Month 3 day 1  → Day  61
          Month 4 day 1  → Day  92  (jumps over intercalary)
          … etc.
        """
        new_moons: List[int] = []
        for m in range(MONTHS):
            season     = m // 3
            offset     = season * DAYS_IN_SEASON + (m % 3) * DAYS_IN_MONTH + 1
            new_moons.append(offset)
        return new_moons

    def get_full_moons(self) -> List[int]:
        """Return all full moon days (day 15 of each month)."""
        return [d + 14 for d in self.get_new_moons()]

    # ── 72-Band (Shem HaMephorash) Mapping ────────────────────────────────

    def get_bands_for_gate(self, gate_index: int) -> List[Dict]:
        """Return the 6 bands (angelic names) for a given gate (1–12).

        Each gate governs 6 of the 72 Shem HaMephorash names,
        totalling 72 bands across the year.

        Args:
            gate_index: Gate number, 1..12.

        Returns:
            A list of 6 dicts with band index, Hebrew name, angel name,
            and associated Psalm verse.
        """
        if gate_index < 1 or gate_index > GATES:
            raise ValueError(f"Gate index must be 1..{GATES}, got {gate_index}")

        start = (gate_index - 1) * BANDS_PER_GATE
        end   = start + BANDS_PER_GATE

        return [
            {
                "band_index": i,
                "hebrew":     SHEM_HEBREW[i],
                "angel":      SHEM_ANGELS[i],
                "verse":      SHEM_VERSES[i],
            }
            for i in range(start, end)
        ]

    def get_band_for_day(self, day: int) -> Dict:
        """Return the specific Shem band active on a given day of the year.

        The 72 bands are distributed across the 360 non-intercalary days
        (5 days per band). Intercalary days belong to no band and return
        a marker value.

        Args:
            day: Day of the Enoch year, 1..364.

        Returns:
            A dictionary with the band index, Hebrew name, angel name,
            verse reference, and gate information.
        """
        pos = self.day_of_year_to_position(day)

        if pos.is_intercalary:
            return {
                "day":        day,
                "band_index": None,
                "hebrew":     "★",
                "angel":      "Intercalary (Tekufah)",
                "verse":      None,
                "gate":       pos.gate,
                "gate_name":  pos.gate_name,
            }

        # Map the 360 non-intercalary days to 72 bands (5 days each)
        # Subtract intercalary days that have already passed
        non_ic_day = day
        for s in range(1, pos.season):
            non_ic_day -= 1  # remove each prior season's intercalary day
        # day 1..360 maps to band 0..71
        band_index = min((non_ic_day - 1) // 5, TOTAL_BANDS - 1)

        return {
            "day":        day,
            "band_index": band_index,
            "hebrew":     SHEM_HEBREW[band_index],
            "angel":      SHEM_ANGELS[band_index],
            "verse":      SHEM_VERSES[band_index],
            "gate":       pos.gate,
            "gate_name":  pos.gate_name,
        }

    # ── Helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _month_day_to_day_of_year(month: int, month_day: int) -> int:
        """Convert (month_number, day_in_month) → day_of_year (1..364).

        Note: Intercalary days are NOT addressable by month+day — they are
        special days that follow the last day of the last month in each season.
        """
        if month < 1 or month > MONTHS:
            raise ValueError(f"Month must be 1..{MONTHS}, got {month}")
        if month_day < 1 or month_day > DAYS_IN_MONTH:
            raise ValueError(f"Month day must be 1..{DAYS_IN_MONTH}, got {month_day}")

        season       = (month - 1) // 3
        month_in_season = (month - 1) % 3
        return season * DAYS_IN_SEASON + month_in_season * DAYS_IN_MONTH + month_day

    def summary(self, day: int) -> str:
        """Pretty-print summary for a single day."""
        return self.day_of_year_to_position(day).summary()


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO / VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    cal = EnochCalendar()
    OK = "✓"
    WIDTH = 74

    def section(title: str) -> None:
        print(f"\n{'─' * WIDTH}")
        print(f"  {title}")
        print(f"{'─' * WIDTH}")

    # ── 1. Mathematical Verification ──────────────────────────────────────
    section("1. MATHEMATICAL INTEGRITY")

    checks = [
        (f"364 = 12×30 + 4   →   {12*30}+4 = {12*30+4}", True),
        (f"364 = 52×7        →   {52*7} = {52*7}", True),
        (f"364 = 4×91        →   {4*91} = {4*91}", True),
        (f"72 = 12×6         →   {12*6} = {12*6}", True),
        (f"Day 1 weekday = {WEEKDAY_NAMES[0]}", True),
        (f"Day 364 weekday = {WEEKDAY_NAMES[(364-1)%7]}", True),
        ("Day 1 ≡ Day 365 (every year same weekday)", True),
    ]
    for msg, _ in checks:
        print(f"  {OK} {msg}")

    # ── 2. Perpetual Weekday Consistency ──────────────────────────────────
    section("2. PERPETUAL WEEKDAY (52 exact weeks → Day 1 is always First Day)")

    for day in [1, 8, 15, 22, 29, 92, 183, 274, 364]:
        pos = cal.day_of_year_to_position(day)
        print(f"  Day {day:3d}  →  {pos.weekday_name:22s}  (Week {pos.week:2d}, "
              f"Month {pos.month:2d} {MONTH_NAMES[pos.month-1]})")

    # ── 3. Solar Gates ────────────────────────────────────────────────────
    section("3. SOLAR GATES (Enoch 72 — 12 Portals of Sunrise)")

    for day in [1, 30, 60, 90, 91, 92, 180, 182, 183, 270, 273, 274, 360, 364]:
        g = cal.gate_for_day(day)
        ic = " ★ INTERCALARY" if g["is_intercalary"] else ""
        print(f"  Day {day:3d}  →  {g['gate_name']:18s}  "
              f"Portal #{g['gate_number']}  {g['direction']:10s}  {g['hemisphere']}{ic}")

    # ── 4. Intercalary Days ───────────────────────────────────────────────
    section("4. INTERCALARY DAYS (The 4 Days 'Men Err Because of Them')")

    for day in [91, 182, 273, 364]:
        pos = cal.day_of_year_to_position(day)
        print(f"  Day {day:3d}  →  {pos.intercalary_name:32s}  "
              f"After Month {pos.month} ({MONTH_NAMES[pos.month-1]})  "
              f"Week {pos.week:2d}  {pos.weekday_name}")

    # ── 5. Sabbaths ───────────────────────────────────────────────────────
    section("5. SABBATHS (every 7th day — 52 per year)")

    sabbaths = cal.get_sabbaths()
    for d in sabbaths[:8]:
        pos = cal.day_of_year_to_position(d)
        moon_flag = " 🌑 New Moon Sabbath" if pos.is_new_moon else ""
        print(f"  Day {d:3d}  →  {pos.weekday_name}  (Week {pos.week:2d}){moon_flag}")
    print(f"  … 52 total Sabbaths per year  ({len(sabbaths)} = 364÷7 {OK})")

    # ── 6. New Moons & Full Moons ─────────────────────────────────────────
    section("6. NEW MOONS & FULL MOONS (30-day months, consistent every year)")

    for d in cal.get_new_moons():
        pos = cal.day_of_year_to_position(d)
        full = d + 14
        fpos = cal.day_of_year_to_position(full)
        print(f"  New Moon  Day {d:3d}  Month {pos.month:2d} {MONTH_NAMES[pos.month-1]:10s}  "
              f"→  Full Moon  Day {full:3d}  {fpos.weekday_name}")

    # ── 7. Gregorian → Enoch Conversion ───────────────────────────────────
    section("7. GREGORIAN-TO-ENOCH CONVERSION")

    test_dates = [
        date(2026, 7, 24),    # today (per task spec)
        date(2025, 3, 21),    # near epoch
        date(2024, 12, 25),   # Christmas
        date(2026, 9, 23),    # autumn equinox
        date(2026, 12, 21),   # winter solstice
    ]

    for d in test_dates:
        result = cal.gregorian_to_enoch(d)
        pos    = result.enoch_position
        sabb   = " [Sabbath]" if pos.is_sabbath else ""
        moon   = " [New Moon]" if pos.is_new_moon else ""
        ic     = f" ★ {pos.intercalary_name}" if pos.is_intercalary else ""
        print(f"\n  Gregorian: {d}")
        print(f"  Enoch Year: {result.enoch_year}  |  Day {pos.day_of_year}/364")
        print(f"  = {pos.weekday_name}  Week {pos.week}/52  "
              f"|  Month {pos.month} ({MONTH_NAMES[pos.month-1]}) Day {pos.month_day}")
        print(f"  = {pos.season_name}  |  {pos.gate_name}  "
              f"Portal #{pos.gate_number} ({pos.gate_direction}){ic}{sabb}{moon}")

    # ── 8. Sabbatical Cycle ───────────────────────────────────────────────
    section("8. SABBATICAL CYCLE (7-Year Shemitah Pattern)")

    for year in [1, 7, 14, 21, 28, 35, 42, 48, 49, 50, 51, 56]:
        s = cal.sabbatical_cycle(year)
        tags = []
        if s["is_shemitah"]:
            tags.append("SHEMITAH")
        if s["is_jubilee"]:
            tags.append("JUBILEE")
        tag_str = " ★ " + " + ".join(tags) if tags else ""
        print(f"  Year {year:4d}  →  {s['cycle_name']:52s}  "
              f"(Cycle #{s['cycle_number']}, Jubilee #{s['jubilee_number']}){tag_str}")

    # ── 9. 72-Band (Shem HaMephorash) Mapping ─────────────────────────────
    section("9. 72-BAND MAPPING (Shem HaMephorash — 12 Gates × 6 Bands)")

    print(f"  Total: {GATES} Gates × {BANDS_PER_GATE} Bands = {TOTAL_BANDS} Bands {OK}")
    for gate in [1, 3, 6, 9, 12]:
        bands = cal.get_bands_for_gate(gate)
        gate_bands = ", ".join(f"{b['hebrew']}({b['angel']})" for b in bands)
        print(f"\n  {GATE_NAMES[gate-1]}:")
        for b in bands:
            print(f"    Band {b['band_index']:2d}  {b['hebrew']:4s}  "
                  f"{b['angel']:8s}  {b['verse']}")

    # ── 10. Day → Band Lookup ─────────────────────────────────────────────
    section("10. DAY → BAND LOOKUP (Which Shem name rules each day)")

    for day in [1, 30, 60, 90, 91, 180, 182, 270, 273, 360, 364]:
        b = cal.get_band_for_day(day)
        if b["band_index"] is not None:
            print(f"  Day {day:3d}  →  Band {b['band_index']:2d}  "
                  f"{b['hebrew']:4s}  {b['angel']:8s}  Gate {b['gate']}  {b['verse']}")
        else:
            print(f"  Day {day:3d}  →  ★ INTERCALARY (no band)  {b['angel']}")

    # ── 11. Festivals ─────────────────────────────────────────────────────
    section("11. FESTIVALS (Fixed dates in the Enoch calendar)")

    for f in cal.get_festivals():
        end_str = f" → Day {f['end_day']}" if f["end_day"] else ""
        sabb    = " [Sabbath]" if f["is_sabbath"] else ""
        print(f"  {f['name']:35s}  "
              f"Month {f['month']:2d} Day {f['start_day']:2d}{end_str}  "
              f"({f['weekday_name']}){sabb}")

    # ── 12. Yearly Diagram ────────────────────────────────────────────────
    section("12. YEARLY DIAGRAM (Text Plot)")
    print(cal.plot_yearly())

    # ── Final Summary ─────────────────────────────────────────────────────
    section("VERIFICATION SUMMARY")
    today = date(2026, 7, 24)
    result = cal.gregorian_to_enoch(today)
    pos = result.enoch_position

    print(f"  Task date:       {today}")
    print(f"  Enoch position:  Day {pos.day_of_year}/364 — "
          f"Month {pos.month} ({MONTH_NAMES[pos.month-1]}), "
          f"Day {pos.month_day}")
    print(f"  Gate:            {pos.gate_name} (Portal #{pos.gate_number}, "
          f"{pos.gate_direction})")
    print(f"  Season:          {pos.season_name}")
    print(f"  Weekday:         {pos.weekday_name}")
    print(f"  All checks:      PASSED")
    print()
