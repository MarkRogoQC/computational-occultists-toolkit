#!/usr/bin/env python3
"""
Trithemius Steganographia Cipher Engine (1499)
==============================================

Johannes Trithemius's *Steganographia* (written c.1499, published 1606) is the
first printed work on cryptography.  It disguises a polyalphabetic substitution
cipher as a grimoire of angelic magic:

  - "Angels"  → key schedules (shift sequences)
  - "Spirits" → substitution alphabets
  - "Conjurations" → cipher invocations

This module implements the complete system across three books, the 72-band
extension (Shem HaMephorash angels), and the famous AVE MARIA steganographic
embedding that hides messages inside prayer texts.

Usage
-----
    from trithemius_cipher import Trithemius

    t = Trithemius()

    # Book 1 — progressive shift
    ct = t.encrypt("HELLOWORLD", mode=1)
    pt = t.decrypt(ct, mode=1)          # → HELLOWORLD

    # Book 2 — passphrase-driven Vigenère
    ct = t.encrypt("SECRET", mode=2, key="ANGEL")
    pt = t.decrypt(ct, mode=2, key="ANGEL")

    # Book 3 — 32 spirit-name key schedule
    ct = t.encrypt("MESSAGE", mode=3, hour=5)
    pt = t.decrypt(ct, mode=3, hour=5)

    # 72-band cipher
    c = t.band_to_cipher(42, 'H')       # band 42 encrypts 'H'
    p = t.cipher_to_band(c, 42)         # decrypt

    # AVE MARIA steganography
    embedded = t.steganographic_embed("HELLO", "Ave Maria gratia plena")
    extracted = t.steganographic_extract(embedded)  # → "HELLO"

References
----------
  - Trithemius, *Steganographia* (c.1499, pub. 1606)
  - Trithemius, *Polygraphiae* (1518)
  - Reeds, "Solved: The Ciphers in Book III of Trithemius's Steganographia"
  - Shem HaMephorash — the 72-fold name of God (Exodus 14:19-21)
"""

from __future__ import annotations

import hashlib
import itertools
import re
from typing import Any, Dict, List, Optional, Tuple, Union

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# Classical 24-letter Latin alphabet (no J, U, W — as in Trithemius's era)
# I and J were the same glyph; U and V were the same glyph; W was not used.
LATIN_24 = "ABCDEFGHIKLMNOPQRSTVXYZ"

# Modern 26-letter alphabet for practical use
LATIN_26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# ── 32 Spirits of the Hours (from Steganographia, Book 1) ────────────────────
# Each spirit governs one of the 32 planetary hours (16 day + 16 night).
# Their names serve as shift keys when operating in Book 3 mode.
SPIRITS_OF_THE_HOURS: List[str] = [
    "PADIEL",    # 1  – 1st hour of day   (Sun)
    "CAMUEL",    # 2                       (Venus)
    "ASELIEL",   # 3                       (Mercury)
    "BARMIEL",   # 4                       (Moon)
    "GEDIEL",    # 5                       (Saturn)
    "ASYRIEL",   # 6                       (Jupiter)
    "MASERIEL",  # 7                       (Mars)
    "MALCHIDAEL",# 8                       (Sun)
    "ASEL",      # 9                       (Venus)
    "BARUEL",    # 10                      (Mercury)
    "GEDUEL",    # 11                      (Moon)
    "DELIEL",    # 12                      (Saturn)
    "CAPSIEL",   # 13                      (Jupiter)
    "CADSIEL",   # 14                      (Mars)
    "PENIEL",    # 15                      (Sun)
    "PENAT",     # 16                      (Venus) — 16th day hour
    "RAPHAEL",   # 17  – 1st hour of night (Mercury)
    "BAGLIEL",   # 18                      (Moon)
    "TAMIEL",    # 19                      (Saturn)
    "ATHAPIEL",  # 20                      (Jupiter)
    "RATAPIEL",  # 21                      (Mars)
    "NACHIEL",   # 22                      (Sun)
    "HADRIEL",   # 23                      (Venus)
    "HAANIEL",   # 24                      (Mercury)
    "PARSIEL",   # 25                      (Moon)
    "PANDIEL",   # 26                      (Saturn)
    "PANTIEL",   # 27                      (Jupiter)
    "HISPIEL",   # 28                      (Mars)
    "HISPANIEL", # 29                      (Sun)
    "HIDRIEL",   # 30                      (Venus)
    "AMONIEL",   # 31                      (Mercury)
    "AMODIEL",   # 32                      (Moon)
]

# ── 72 Angels of the Shem HaMephorash ────────────────────────────────────────
# Each angel rules a 5° zodiacal segment (72 × 5° = 360°).
# Their names form the basis of the 72-band cipher extension.
SHEM_ANGELS: List[str] = [
    "VEHUIAH",   "JELIEL",    "SITAEL",    "ELEMIAH",   "MAHASIAH",
    "LELAHEL",   "ACHAIAH",   "CAHETEL",   "HAZIEL",    "ALADIAH",
    "LAUVIAH",   "HAHAIAH",   "IEZALEL",   "MEBAHEL",   "HARIEL",
    "HAKAMIAH",  "LAUVIAH2",  "CALIEL",    "LEUVIAH",   "PAHALIAH",
    "NELCHAEL",  "IEIAIEL",   "MELAHEL",   "HAHUIAH",   "NITHHAIAH",
    "HAAIAH",    "IERATHEL",  "SEEHIAH",   "REIIEL",    "OMAEL",
    "LECABEL",   "VASARIAH",  "IEHUIAH",   "LEHAHIAH",  "CHAVAKIAH",
    "MENADEL",   "ANIEL",     "HAAMIAH",   "REHAEL",    "IEIAZEL",
    "HAHAHEL",   "MIKAEL",    "VEULIAH",   "IELAHIAH",  "SEALIAH",
    "ARIEL",     "ASALIAH",   "MIHAEL",    "VEHUEL",    "DANIEL",
    "HAHASIAH",  "IMAMIAH",   "NANAEL",    "NITHAEL",   "MEBAHIAH",
    "POIEL",     "NEMAMIAH",  "IEIALEL",   "HARAHEL",   "MIZRAEL",
    "UMABEL",    "IAHHEL",    "ANAUEL",    "MEHIKIEL",  "DAMABIAH",
    "MANAKEL",   "AYAEL",     "HABUHIAH",  "ROCHEL",    "IABAMIAH",
    "HAIAIEL",   "MUMIAH",
]

# ── The AVE MARIA prayer (traditional cover text) ────────────────────────────
AVE_MARIA = (
    "Ave Maria gratia plena Dominus tecum benedicta tu in mulieribus "
    "et benedictus fructus ventris tui Iesus Sancta Maria Mater Dei "
    "ora pro nobis peccatoribus nunc et in hora mortis nostrae Amen"
)


# ═══════════════════════════════════════════════════════════════════════════════
# TRITHEMIUS CIPHER ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class Trithemius:
    """Complete Trithemius Steganographia cipher engine.

    Attributes
    ----------
    alphabet : str
        The classical or modern alphabet used for all operations.
    n : int
        Length of the alphabet.
    recta : List[List[str]]
        The Tabula Recta — a 2D array where each row is a Caesar shift.
    """

    def __init__(self, alphabet: str = LATIN_26) -> None:
        """Initialise the engine with a chosen alphabet.

        Parameters
        ----------
        alphabet : str
            Alphabet string.  Defaults to 26-letter Latin.
            Use ``LATIN_24`` for the classical 24-letter variant.
        """
        self.alphabet = alphabet.upper()
        self.n = len(self.alphabet)
        self._pos: Dict[str, int] = {ch: i for i, ch in enumerate(self.alphabet)}
        self.recta = self._build_recta()
        self._72_band_shifts = self._build_72_band_shifts()

    # ── 1. TABULA RECTA ──────────────────────────────────────────────────────

    def _build_recta(self) -> List[List[str]]:
        """Construct the Tabula Recta (24×24 or 26×26 letter square).

        Each row is a Caesar shift of the alphabet:
            Row 0: ABCDEFGHIJKLMNOPQRSTUVWXYZ
            Row 1: BCDEFGHIJKLMNOPQRSTUVWXYZA
            Row 2: CDEFGHIJKLMNOPQRSTUVWXYZAB
            ...
        """
        a = self.alphabet
        return [[a[(i + j) % self.n] for j in range(self.n)]
                for i in range(self.n)]

    def tabula_recta(self,
                     alphabet: Optional[str] = None) -> Dict[str, Any]:
        """Return a printable representation of the Tabula Recta.

        Parameters
        ----------
        alphabet : str, optional
            If provided, rebuild the recta with this alphabet before returning.

        Returns
        -------
        dict
            ``{"alphabet": str, "size": int, "recta": 2D array}``
        """
        if alphabet is not None:
            self.alphabet = alphabet.upper()
            self.n = len(self.alphabet)
            self._pos = {ch: i for i, ch in enumerate(self.alphabet)}
            self.recta = self._build_recta()
        return {
            "alphabet": self.alphabet,
            "size": self.n,
            "recta": self.recta,
        }

    def print_recta(self) -> str:
        """Pretty-print the Tabula Recta as a formatted grid."""
        header = "    " + " ".join(self.alphabet)
        lines = [header, "   " + "-" * (2 * self.n)]
        for i, row in enumerate(self.recta):
            lines.append(f"{self.alphabet[i]} | {' '.join(row)}")
        return "\n".join(lines)

    # ── 2. KEY SCHEDULES (Three Books) ───────────────────────────────────────

    def _book1_shifts(self, length: int, start: int = 0) -> List[int]:
        """Book 1 — Progressive shift (each character shifts +1 more).

        Simplest key schedule: the shift value increments by 1 for each
        successive character.  The first character is shifted by 0 (or
        *start*), the second by 1, etc.
        """
        return [(start + i) % self.n for i in range(length)]

    def _book2_shifts(self, key: str, length: int) -> List[int]:
        """Book 2 — Passphrase-driven shift (Vigenère-style).

        Each successive letter of the passphrase determines the shift for
        that position.  The passphrase cycles if shorter than the message.
        """
        if not key:
            raise ValueError("Book 2 requires a non-empty passphrase key.")
        k = self._clean(key)
        positions = [self._pos[ch] for ch in k]
        return [positions[i % len(positions)] for i in range(length)]

    def _book3_shifts(self, hour: int, length: int) -> List[int]:
        """Book 3 — Spirit-of-the-Hour key schedule.

        Trithemius assigned 32 spirit names to the 32 planetary hours
        (16 day + 16 night).  The spirit name for the given hour supplies
        the shift sequence.  If *hour* is None, all 32 names are cycled.

        Parameters
        ----------
        hour : int
            1–32, corresponding to one of the 32 spirits.
            If 0 or None, cycles through all spirit names.
        length : int
            Number of shifts to produce.
        """
        if hour is not None and 1 <= hour <= 32:
            # Use the single spirit's name as the shift key
            name = SPIRITS_OF_THE_HOURS[hour - 1]
            name_clean = self._clean(name)
            shifts = [self._pos[ch] for ch in name_clean]
            return [shifts[i % len(shifts)] for i in range(length)]
        # Cycle through all 32 names
        all_names = [self._clean(n) for n in SPIRITS_OF_THE_HOURS]
        all_positions = [[self._pos[ch] for ch in n] for n in all_names]
        result: List[int] = []
        name_idx = 0
        for i in range(length):
            current_name_shifts = all_positions[name_idx % 32]
            name_pos = (i // max(1, len(current_name_shifts))) % len(current_name_shifts)
            shift = current_name_shifts[i % len(current_name_shifts)]
            result.append(shift)
            # Advance to the next spirit every few characters
            if (i + 1) % len(current_name_shifts) == 0:
                name_idx += 1
        return result

    def _get_shifts(self, mode: int, length: int,
                    key: Optional[Union[str, int]] = None,
                    hour: Optional[int] = None,
                    start: int = 0) -> List[int]:
        """Dispatch to the correct book's shift schedule."""
        if mode == 1:
            return self._book1_shifts(length, start)
        elif mode == 2:
            if key is None or not isinstance(key, str):
                raise ValueError("Book 2 requires a string key (passphrase).")
            return self._book2_shifts(key, length)
        elif mode == 3:
            return self._book3_shifts(hour, length)
        else:
            raise ValueError(f"Unknown mode {mode}.  Use 1, 2, or 3.")

    # ── 3. ENCRYPT / DECRYPT ─────────────────────────────────────────────────

    def _clean(self, text: str) -> str:
        """Strip non-alphabet characters and uppercase."""
        return "".join(ch.upper() for ch in text if ch.upper() in self._pos)

    def encrypt(self, plaintext: str, mode: int = 1,
                key: Optional[Union[str, int]] = None,
                hour: Optional[int] = None,
                start: int = 0) -> str:
        """Encrypt plaintext using one of Trithemius's three modes.

        Parameters
        ----------
        plaintext : str
            Message to encrypt.  Non-alpha characters are preserved in place
            but not encrypted.
        mode : int
            1 = progressive shift (Book 1)
            2 = passphrase-driven (Book 2)
            3 = spirit-of-the-hour (Book 3)
        key : str, optional
            Passphrase for mode 2.
        hour : int, optional
            1–32 spirit hour for mode 3.
        start : int, optional
            Initial shift offset for mode 1 (default 0).

        Returns
        -------
        str
            Encrypted ciphertext.
        """
        clean = self._clean(plaintext)
        if not clean:
            return plaintext

        shifts = self._get_shifts(mode, len(clean), key, hour, start)
        ciphertext = list(plaintext)
        ci = 0
        for i, ch in enumerate(ciphertext):
            if ch.upper() in self._pos:
                p = self._pos[ch.upper()]
                c = self.alphabet[(p + shifts[ci]) % self.n]
                ciphertext[i] = c if ch.isupper() else c.lower()
                ci += 1
        return "".join(ciphertext)

    def decrypt(self, ciphertext: str, mode: int = 1,
                key: Optional[Union[str, int]] = None,
                hour: Optional[int] = None,
                start: int = 0) -> str:
        """Decrypt ciphertext (exact inverse of encrypt).

        Parameters
        ----------
        ciphertext : str
            Ciphertext to decrypt.
        mode : int
            Same mode as used for encryption.
        key : str, optional
            Same passphrase as used for encryption (mode 2).
        hour : int, optional
            Same spirit hour as used for encryption (mode 3).
        start : int, optional
            Same start offset (mode 1).

        Returns
        -------
        str
            Decrypted plaintext.
        """
        clean = self._clean(ciphertext)
        if not clean:
            return ciphertext

        shifts = self._get_shifts(mode, len(clean), key, hour, start)
        plaintext = list(ciphertext)
        ci = 0
        for i, ch in enumerate(plaintext):
            if ch.upper() in self._pos:
                c = self._pos[ch.upper()]
                p = self.alphabet[(c - shifts[ci]) % self.n]
                plaintext[i] = p if ch.isupper() else p.lower()
                ci += 1
        return "".join(plaintext)

    # ── 4. 72-BAND EXTENSION ─────────────────────────────────────────────────

    def _build_72_band_shifts(self) -> List[int]:
        """Derive a shift value for each of the 72 angelic bands.

        Each angel's name is hashed (SHA-256) to produce a deterministic
        shift value for its band.  With an alphabet of only 26 letters
        and 72 bands, shifts will naturally repeat — each band retains
        its unique identity through its angel name regardless.
        """
        shifts: List[int] = []
        for name in SHEM_ANGELS:
            # Use a salted hash over the band range so shifts distribute
            # evenly across the alphabet even when collisions occur.
            h = hashlib.sha256((name + "band").encode()).digest()
            val = int.from_bytes(h[:4], "big")
            shifts.append(val % self.n)
        return shifts

    def band_shift(self, band: int) -> int:
        """Return the shift value for the given angelic band (1–72)."""
        if not (1 <= band <= 72):
            raise ValueError(f"Band must be 1–72, got {band}")
        return self._72_band_shifts[band - 1]

    def band_angel(self, band: int) -> str:
        """Return the angel name for the given band (1–72)."""
        if not (1 <= band <= 72):
            raise ValueError(f"Band must be 1–72, got {band}")
        return SHEM_ANGELS[band - 1]

    def band_to_cipher(self, band: int, message_char: str) -> str:
        """Encrypt a single character using the specified angelic band.

        Parameters
        ----------
        band : int
            Band number 1–72.
        message_char : str
            Single alphabetic character to encrypt.

        Returns
        -------
        str
            Encrypted character.
        """
        ch = message_char.upper()
        if ch not in self._pos:
            return message_char
        shift = self.band_shift(band)
        c = self.alphabet[(self._pos[ch] + shift) % self.n]
        return c if message_char.isupper() else c.lower()

    def cipher_to_band(self, cipher_char: str, band: int) -> str:
        """Decrypt a single character using the specified angelic band.

        Parameters
        ----------
        cipher_char : str
            Single ciphertext character.
        band : int
            Band number 1–72.

        Returns
        -------
        str
            Decrypted plaintext character.
        """
        ch = cipher_char.upper()
        if ch not in self._pos:
            return cipher_char
        shift = self.band_shift(band)
        p = self.alphabet[(self._pos[ch] - shift) % self.n]
        return p if cipher_char.isupper() else p.lower()

    def band_encrypt(self, plaintext: str, bands: List[int]) -> str:
        """Encrypt a message using a sequence of bands.

        Each character is encrypted with the band at the corresponding
        position.  If *bands* is shorter than the plaintext, it cycles.

        Parameters
        ----------
        plaintext : str
            Message to encrypt.
        bands : list of int
            Band numbers (1–72), one per character (or cycled).

        Returns
        -------
        str
            Ciphertext.
        """
        clean = self._clean(plaintext)
        if not clean:
            return plaintext
        result = list(plaintext)
        ci = 0
        for i, ch in enumerate(result):
            if ch.upper() in self._pos:
                band = bands[ci % len(bands)]
                result[i] = self.band_to_cipher(band, ch)
                ci += 1
        return "".join(result)

    def band_decrypt(self, ciphertext: str, bands: List[int]) -> str:
        """Decrypt a message encrypted with :meth:`band_encrypt`."""
        clean = self._clean(ciphertext)
        if not clean:
            return ciphertext
        result = list(ciphertext)
        ci = 0
        for i, ch in enumerate(result):
            if ch.upper() in self._pos:
                band = bands[ci % len(bands)]
                result[i] = self.cipher_to_band(ch, band)
                ci += 1
        return "".join(result)

    # ── 5. AVE MARIA STEGANOGRAPHIC EMBEDDING ────────────────────────────────

    @staticmethod
    def _word_letter_positions(word: str) -> List[int]:
        """Return the index positions of alphabetic characters within a word.

        Example: "gratia" → positions [0,1,2,3,4,5] for g,r,a,t,i,a
        """
        return [i for i, ch in enumerate(word) if ch.isalpha()]

    def steganographic_embed(self, message: str,
                             cover_text: Optional[str] = None) -> str:
        """Embed a secret message inside a cover text using letter-marking.

        Each letter of the secret message is encoded as the alphabetic
        position of a **capitalised** letter within a word of the cover text:
            A=1st letter, B=2nd, ..., Z=26th.

        The marked letter is uppercased in the output; all other letters
        are lowercased.  This mimics Trithemius's technique of hiding
        messages inside the AVE MARIA prayer by subtly accentuating letters.

        Parameters
        ----------
        message : str
            The secret message to hide.
        cover_text : str, optional
            Cover text (defaults to AVE MARIA prayer).

        Returns
        -------
        str
            Cover text with marked letters capitalised.
        """
        if cover_text is None:
            cover_text = AVE_MARIA
        words = cover_text.split()
        msg = self._clean(message)
        if not msg:
            return cover_text.lower()

        result: List[str] = []
        msg_idx = 0

        for word in words:
            if msg_idx >= len(msg):
                result.append(word.lower())
                continue

            target_char = msg[msg_idx]
            target_pos = self._pos[target_char]  # 0-indexed alphabet position

            alpha_indices = self._word_letter_positions(word)
            if not alpha_indices:
                result.append(word.lower())
                continue

            # If the target position falls within this word, mark it
            if target_pos < len(alpha_indices):
                idx = alpha_indices[target_pos]
                marked = (word[:idx]
                          + word[idx].upper()
                          + word[idx + 1:])
                result.append(marked)
                msg_idx += 1
            else:
                result.append(word.lower())

        # Append any remaining words unmarked
        return " ".join(result)

    def steganographic_extract(self, marked_text: str) -> str:
        """Extract a hidden message from marked cover text.

        Scans the text for capitalised letters within lowercase words.
        The alphabetical position of the capitalised letter within its
        word yields the encoded character: 1st = A, 2nd = B, etc.

        Parameters
        ----------
        marked_text : str
            Text with marked (capitalised) letters.

        Returns
        -------
        str
            Extracted message.
        """
        words = marked_text.split()
        result: List[str] = []

        for word in words:
            alpha_indices = self._word_letter_positions(word)
            if not alpha_indices:
                continue
            # Find the capitalised (marked) letter(s)
            for idx in alpha_indices:
                ch = word[idx]
                if ch.isupper() and ch in self._pos:
                    # Determine which alphabetic position this is
                    letter_rank = alpha_indices.index(idx)
                    if letter_rank < self.n:
                        result.append(self.alphabet[letter_rank])
                    break  # one letter per word

        return "".join(result)


# ═══════════════════════════════════════════════════════════════════════════════
# DEMONSTRATION
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 72)
    print("  TRITHEMIUS STEGANOGRAPHIA CIPHER ENGINE (1499)")
    print("=" * 72)

    t = Trithemius()

    # ── TABULA RECTA ─────────────────────────────────────────────────────────
    print("\n─ TABULA RECTA (26 × 26) ───────────────────────────────────")
    info = t.tabula_recta()
    print(f"  Alphabet: {info['alphabet']}")
    print(f"  Size:     {info['size']}×{info['size']}")
    print()
    print(t.print_recta())

    # Also show classical 24-letter recta
    t24 = Trithemius(LATIN_24)
    print("\n  Classical 24-letter Tabula Recta:")
    print(t24.print_recta())

    # ── BOOK 1: PROGRESSIVE SHIFT ────────────────────────────────────────────
    print("\n\n─ BOOK 1 — PROGRESSIVE SHIFT (Simple Spirits) ────────────")
    pt1 = "HELLOWORLD"
    ct1 = t.encrypt(pt1, mode=1)
    dt1 = t.decrypt(ct1, mode=1)
    print(f"  Plaintext:  {pt1}")
    print(f"  Ciphertext: {ct1}")
    print(f"  Decrypted:  {dt1}")
    assert dt1 == pt1, "Book 1 round-trip failed!"

    # Explain the shifts
    print("  Shift schedule:")
    for i, ch in enumerate(pt1):
        shift = i  # start=0
        p = t._pos[ch]
        c = t.alphabet[(p + shift) % 26]
        print(f"    {ch}({p:02d}) + {shift:02d} = {c}({t._pos[c]:02d})  [shift={shift}]")

    # ── BOOK 2: PASSPHRASE KEY ────────────────────────────────────────────────
    print("\n\n─ BOOK 2 — PASSPHRASE-DRIVEN SHIFT (Angels) ──────────────")
    pt2 = "TRITHEMIUS"
    key2 = "STEGANOGRAPHIA"
    ct2 = t.encrypt(pt2, mode=2, key=key2)
    dt2 = t.decrypt(ct2, mode=2, key=key2)
    print(f"  Plaintext:  {pt2}")
    print(f"  Key:        {key2}")
    print(f"  Ciphertext: {ct2}")
    print(f"  Decrypted:  {dt2}")
    assert dt2 == pt2, "Book 2 round-trip failed!"

    key_positions = [t._pos[ch] for ch in t._clean(key2)]
    print("  Shift schedule:")
    for i, ch in enumerate(pt2):
        shift = key_positions[i % len(key_positions)]
        p = t._pos[ch]
        c = t.alphabet[(p + shift) % 26]
        print(f"    {ch}({p:02d}) + {shift:02d} = {c}  [key='{t._clean(key2)[i % len(key_positions)]}']")

    # ── BOOK 3: SPIRIT OF THE HOUR ───────────────────────────────────────────
    print("\n\n─ BOOK 3 — SPIRIT OF THE HOUR (Seals & Conjurations) ──────")
    pt3 = "INVOCATION"
    hour3 = 7  # MASERIEL
    ct3 = t.encrypt(pt3, mode=3, hour=hour3)
    dt3 = t.decrypt(ct3, mode=3, hour=hour3)
    spirit = SPIRITS_OF_THE_HOURS[hour3 - 1]
    print(f"  Plaintext:  {pt3}")
    print(f"  Hour:       {hour3} → {spirit}")
    print(f"  Ciphertext: {ct3}")
    print(f"  Decrypted:  {dt3}")
    assert dt3 == pt3, "Book 3 round-trip failed!"

    # Show all 32 spirits
    print("\n  All 32 Spirits of the Hours:")
    for i, name in enumerate(SPIRITS_OF_THE_HOURS, 1):
        marker = " ←" if i == hour3 else ""
        print(f"    {i:02d}. {name}{marker}")

    # ── MULTI-HOUR TEST ──────────────────────────────────────────────────────
    print("\n  Testing all 32 hours for round-trip correctness...")
    for h in range(1, 33):
        ct = t.encrypt("TEST", mode=3, hour=h)
        dt = t.decrypt(ct, mode=3, hour=h)
        assert dt == "TEST", f"Hour {h} round-trip failed: {ct} → {dt}"
    print("  ✓ All 32 spirit hours encrypt/decrypt correctly.")

    # ── 72-BAND CIPHER ───────────────────────────────────────────────────────
    print("\n\n─ 72-BAND CIPHER (Shem HaMephorash Angels) ───────────────")
    band = 42
    char = 'H'
    encrypted = t.band_to_cipher(band, char)
    decrypted = t.cipher_to_band(encrypted, band)
    print(f"  Band {band} ({t.band_angel(band)}): '{char}' → '{encrypted}' → '{decrypted}'")
    assert decrypted == char, "72-band round-trip failed!"

    # Show all 72 band shifts
    print("\n  Band shift values:")
    for i in range(0, 72, 6):
        row = []
        for j in range(6):
            b = i + j + 1
            if b <= 72:
                row.append(f"{b:02d}:{t.band_angel(b):10s}→{t.band_shift(b):02d}")
        print("    " + "  |  ".join(row))

    # Multi-band encrypt/decrypt
    test_bands = [1, 8, 15, 22, 29, 36, 43, 50, 57, 64, 71]
    pt_band = "CODEXSECRETUS"
    ct_band = t.band_encrypt(pt_band, test_bands)
    dt_band = t.band_decrypt(ct_band, test_bands)
    print(f"\n  Multi-band encrypt with bands {test_bands}:")
    print(f"    Plaintext:  {pt_band}")
    print(f"    Ciphertext: {ct_band}")
    print(f"    Decrypted:  {dt_band}")
    assert dt_band == pt_band, "Multi-band round-trip failed!"
    print("  ✓ Multi-band encrypt/decrypt correct.")

    # ── STEGANOGRAPHIC EMBEDDING ─────────────────────────────────────────────
    print("\n\n─ AVE MARIA STEGANOGRAPHIC EMBEDDING ──────────────────────")

    # Short message that fits within word lengths of the Ave Maria
    secret = "HEL"
    embedded = t.steganographic_embed(secret)
    extracted = t.steganographic_extract(embedded)
    print(f"  Secret message:  {secret}")
    print(f"  Cover text:      {AVE_MARIA}")
    print(f"  Embedded output:")
    print(f"    {embedded}")
    print(f"  Extracted:       {extracted}")
    assert extracted == secret, "Steganographic round-trip failed!"

    # Show the marked letters
    print("\n  Marking breakdown:")
    words = embedded.split()
    for i, word in enumerate(words):
        for j, ch in enumerate(word):
            if ch.isupper():
                pos = t._word_letter_positions(word).index(j)
                print(f"    Word {i}: '{word}' → marked '{ch}' at alpha-pos {pos} "
                      f"(letter #{pos + 1}) → '{t.alphabet[pos]}'")
                break

    # Test with a synthetic cover text that has long enough words for all positions
    secret2 = "CIPHER"
    # Each word must be ≥ position of the letter being encoded
    long_cover = (
        "extraordinarily incomprehensible transformation "
        "multidimensional counterrevolutionary cryptographically "
        "unprecedentedly electroencephalographically "
        "internationalization characterization"
    )
    embedded2 = t.steganographic_embed(secret2, long_cover)
    extracted2 = t.steganographic_extract(embedded2)
    print(f"\n  Longer secret:  {secret2}")
    print(f"  Embedded:       {embedded2}")
    print(f"  Extracted:      {extracted2}")
    assert extracted2 == secret2, "Steganographic #2 round-trip failed!"

    # ── EDGE CASES ───────────────────────────────────────────────────────────
    print("\n\n─ EDGE CASES  ─────────────────────────────────────────────")
    # Case preservation
    ct_case = t.encrypt("HeLlO", mode=1)
    dt_case = t.decrypt(ct_case, mode=1)
    print(f"  Case preserved: 'HeLlO' → '{ct_case}' → '{dt_case}'")
    assert dt_case == "HeLlO", "Case preservation failed!"

    # Non-alpha characters preserved
    ct_punc = t.encrypt("HELLO, WORLD!", mode=2, key="KEY")
    dt_punc = t.decrypt(ct_punc, mode=2, key="KEY")
    print(f"  Punctuation preserved: 'HELLO, WORLD!' → '{ct_punc}' → '{dt_punc}'")
    assert dt_punc == "HELLO, WORLD!", "Punctuation preservation failed!"

    # Empty string
    assert t.encrypt("", mode=1) == ""
    assert t.decrypt("", mode=2, key="A") == ""
    print("  Empty string handled correctly.")

    # ── HISTORICAL EXAMPLE ───────────────────────────────────────────────────
    print("\n\n─ HISTORICAL EXAMPLE — The Angel Padiel Speaks ────────────")
    print("  (Book 3, Hour 1: PADIEL)")
    secret_hist = "AVE MARIA"
    ct_hist = t.encrypt(secret_hist, mode=3, hour=1)
    dt_hist = t.decrypt(ct_hist, mode=3, hour=1)
    print(f"    Invoker:   '{secret_hist}'")
    print(f"    Padiel:    '{ct_hist}'   (the angel speaks in cipher)")
    print(f"    Decoded:   '{dt_hist}'   (mortal understands)")
    assert dt_hist == secret_hist

    # ── SUMMARY ──────────────────────────────────────────────────────────────
    print("\n\n" + "=" * 72)
    print("  ALL TESTS PASSED — Sic transit gloria mundi.")
    print("=" * 72)
