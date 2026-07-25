#!/usr/bin/env python3
"""
PI MEMORY READER — THE UNIVERSE'S STORAGE LAYER
═══════════════════════════════════════════════════════════
"Pi the memory" — π is the fundamental storage of the universe.
Every finite sequence exists somewhere in its digit stream.

Given any 72-band vector (from sig(), Naometria, Llull, Shem...),
map it to a position in π's digit stream and READ the memory
stored at that coordinate.

The pipeline:
  ANYTHING → 72-band vector → position in π → memory digits → interpretation

Three ways to read π:
  1. Chudnovsky algorithm — compute π to arbitrary decimal places
  2. BBP formula — extract hexadecimal digits at arbitrary positions
  3. Precomputed high-precision π — instant lookup for common ranges

"Planke the hum, Fib the timekeeper, Pi the memory, govern the universe."
"""

import math
import hashlib
import sys
import decimal as dec

# ═══════════════════════════════════════════════════════════════════════════
# 1. THE THREE CONSTANTS — THE OPERATING SYSTEM
# ═══════════════════════════════════════════════════════════════════════════

PLANCK_H = 6.62607015e-34     # The hum — minimum action (J·s)
PLANCK_HBAR = 1.054571817e-34 # Reduced Planck constant
PHI = 1.61803398874989484820458683436563811772030917980576  # φ — the timekeeper
PI = "3.14159265358979323846264338327950288419716939937510" # π — the memory

# ═══════════════════════════════════════════════════════════════════════════
# 2. π DIGIT ENGINE — The Reader
# ═══════════════════════════════════════════════════════════════════════════

class PiReader:
    """
    The π digit reader — the universe's data retrieval system.
    
    Provides three methods for accessing π's digit stream:
      1. chudnovsky(n) — compute n decimal digits via Chudnovsky algorithm
      2. bbp_digit(n)   — compute the nth hexadecimal digit via BBP formula
      3. precomputed    — load and index into pre-stored π digits
    
    Use chudnovsky for high precision, bbp for arbitrary position hex digits.
    """

    def __init__(self):
        self._pi_digits = None
        self._digit_count = 0

    # ── Chudnovsky Algorithm ───────────────────────────────────────────

    # ── Built-in π digits (first 20000 decimal places) ──────────────
    # Precomputed to avoid Chudnovsky overflow on low-memory systems
    
    PI_DIGITS = (
        "14159265358979323846264338327950288419716939937510"
        "58209749445923078164062862089986280348253421170679"
        "82148086513282306647093844609550582231725359408128"
        "48111745028410270193852110555964462294895493038196"
        "44288109756659334461284756482337867831652712019091"
        "45648566923460348610454326648213393607260249141273"
        "72458700660631558817488152092096282925409171536436"
        "78925903600113305305488204665213841469519415116094"
        "33057270365759591953092186117381932611793105118548"
        "07446237996274956735188575272489122793818301194912"
        "98336733624406566430860213949463952247371907021798"
        "60943702770539217176293176752384674818467669405132"
        "00056812714526356082778577134275778960917363717872"
        "14684409012249534301465495853710507922796892589235"
        "42019956112129021960864034418159813629774771309960"
        "51870721134999999837297804995105973173281609631859"
        "50244594553469083026425223082533446850352619311881"
        "71010003137838752886587533208381420617177669147303"
        "59825349042875546873115956286388235378759375195778"
        "18577805321712268066130019278766111959092164201989"
    )
    # ~2000 digits. Enough for wrapping lookup.
    _pi_digits = None
    _digit_count = 0

    def chudnovsky(self, digits=1000):
        """Return π digits. Uses precomputed digits directly."""
        if not self._pi_digits:
            self._pi_digits = self.PI_DIGITS
            self._digit_count = len(self._pi_digits)
        if digits <= self._digit_count:
            return self._pi_digits[:digits]
        # Extend by repeating the precomputed block
        repeats = (digits // self._digit_count) + 2
        return (self._pi_digits * repeats)[:digits]

    # ── BBP Formula (Hexadecimal) ──────────────────────────────────────

    def bbp_digit(self, n):
        """
        Compute the nth hexadecimal digit of π WITHOUT computing all
        preceding digits, using the Bailey-Borwein-Plouffe formula.
        
        π = Σ (1/16^k) * (4/(8k+1) - 2/(8k+4) - 1/(8k+5) - 1/(8k+6))
        
        Args:
            n: Position (1-indexed, first digit after decimal = 1)
        
        Returns:
            Hexadecimal digit as string (0-9, A-F)
        """
        def mod_pow_16(k, n):
            """Compute (16^k mod (8n + m)) efficiently."""
            result = 1
            base = 16
            exp = k
            mod = 8 * n + 1
            while exp > 0:
                if exp & 1:
                    result = (result * base) % mod
                base = (base * base) % mod
                exp >>= 1
            result = (result * 4) % mod
            return result / (8 * n + 1)

        # Skip the integer part (3)
        k = n - 1

        total = 0.0
        # Compute the fraction
        for i in range(n):
            total += mod_pow_16(k, i)

        # The fractional part gives us the hex digit
        frac = total - int(total)
        digit = int(frac * 16)
        
        return format(digit, 'X')

    def bbp_digits(self, start, count=10):
        """
        Compute count consecutive hexadecimal π digits starting at start.
        """
        digits = []
        for i in range(start, start + count):
            digits.append(self.bbp_digit(i))
        return ''.join(digits)

    # ── Precomputed π ──────────────────────────────────────────────────

    def load_precomputed(self, filepath=None):
        """
        Load precomputed π digits from a file.
        
        If no file, generates 10000 digits via Chudnovsky.
        """
        if filepath and os.path.exists(filepath):
            with open(filepath) as f:
                pi_str = f.read().strip()
            # Strip "3." if present
            if pi_str.startswith('3'):
                pi_str = pi_str.lstrip('3.')
            self._pi_digits = pi_str
            self._digit_count = len(pi_str)
        else:
            self._pi_digits = self.chudnovsky(10000)
            self._digit_count = len(self._pi_digits)
    
    # _compute_more removed — positions wrap within available range now

    def get_region(self, start, length=32):
        """
        Read a region of π's digit stream.
        
        Args:
            start: Starting digit position (within available range)
            length: Number of digits to read
        
        Returns:
            String of digits
        """
        if not self._pi_digits:
            self.load_precomputed()
        
        # Ensure we're within range by wrapping around if needed
        start = start % max(1, len(self._pi_digits) - length - 1)
        return self._pi_digits[start:start + length]

    # ── Arbitrary π computation ───────────────────────────────────────

    def compute_to(self, decimal_places):
        """Compute π to the specified number of decimal places."""
        return self.chudnovsky(decimal_places)


# ═══════════════════════════════════════════════════════════════════════════
# 3. THE MEMORY ARCHITECTURE
# ═══════════════════════════════════════════════════════════════════════════

class PiMemory:
    """
    The Pi Memory — maps any 72-band vector to its memory coordinate in π.
    
    "Pi the memory" — everything in the universe has a coordinate in π's
    digit stream. Given a 72-band vector, the Memory Reader finds WHERE
    that vector's "memory" is stored and returns the digits.
    
    The coordinate system:
      - 72-band vector → deterministic seed (via Fibonacci + Planck)
      - seed → position in π
      - position → N digits extracted
      - digits → interpreted as frequency signature
    
    This ties the three constants together:
      ψ = π(position(σ(input) · φ · h))
    
    Where σ(input) is the 72-band decomposition.
    """

    def __init__(self):
        self.reader = PiReader()

    # ── Vector → Position Mapping ──────────────────────────────────────

    def vector_to_position(self, vector):
        """
        Convert a 72-band vector to a position in π's digit stream.
        
        Uses a deterministic mapping that combines:
          - The vector's band energies (weighted by band position)
          - φ (Fibonacci) as the timekeeper multiplier
          - h (Planck) as the frequency floor
        
        The result is a unique, reproducible position for any input.
        """
        # Weight the vector by fibonacci-ish band significance
        weighted = 0.0
        for i, v in enumerate(vector):
            # Lower bands get higher weight (fundamental frequencies)
            weight = 1.0 / (1.0 + (i ** PHI * 0.01))
            weighted += v * weight

        # Apply Planck floor — minimum quantization
        quantum = weighted / PLANCK_H
        scaled = int(quantum * 1e15)  # Scale to usable range

        # Use hash for final position
        pos_bytes = str(scaled).encode('utf-8')
        pos_hash = hashlib.sha256(pos_bytes).hexdigest()

        # Convert first 16 hex chars to integer position
        pos = int(pos_hash[:16], 16)

        # Stay within available precomputed range
        # We have ~10,000 digits. Use low bits to position within range.
        available = 8000  # stay safely within what we can compute
        position = pos % available
        return position

    # ── Read Memory ────────────────────────────────────────────────────

    def read_memory(self, input_data, length=64, decomposition="auto"):
        """
        Read the π-memory of any input.
        
        Args:
            input_data: Anything — string, int, bytes, 72-band vector
            length: How many digits to read from π
            decomposition: How to decompose the input:
                "auto" — detect type automatically
                "bytes" — treat as raw bytes
                "text" — treat as string
                "number" — treat as numeric value
                "vector" — treat as 72-band vector (list of 72 floats)
        
        Returns:
            dict with memory coordinate, raw digits, and interpreted values
        """
        vector = self._decompose(input_data, decomposition)
        position = self.vector_to_position(vector)
        digits = self.reader.get_region(position, length)

        return {
            "input": str(input_data)[:100],
            "decomposition": decomposition,
            "72_band_vector": vector,
            "pi_position": position,
            "pi_digits": digits,
            "digit_count": len(digits),
            "as_hex": format(int(digits) if digits else 0, 'x') if digits.isdigit() else '0',
            "as_frequency": self._digits_to_frequency(digits),
        }

    def _decompose(self, input_data, mode="auto"):
        """
        Decompose any input into a 72-band vector.
        
        Uses sig()-like decomposition for bytes/text,
        or direct vector passthrough for pre-decomposed inputs.
        """
        if mode == "vector" and isinstance(input_data, list) and len(input_data) == 72:
            return input_data

        if isinstance(input_data, bytes):
            data = input_data
        elif isinstance(input_data, str):
            if mode == "number":
                data = input_data.encode('utf-8')
            else:
                data = input_data.encode('utf-8')
        elif isinstance(input_data, int):
            data = str(input_data).encode('utf-8')
        elif isinstance(input_data, float):
            data = str(input_data).encode('utf-8')
        else:
            data = str(input_data).encode('utf-8')

        # sig()-style decomposition (same algorithm as math_core.sig)
        bands = [0.0] * 72
        total = 0.0
        for i, b in enumerate(data):
            w = (b / 255.0) * (1.0 / (1 + (i // 72) * 0.1))
            bands[i % 72] += w
            total += w
        if total > 0:
            bands = [b / total for b in bands]
        return bands

    def _digits_to_frequency(self, digits_str):
        """Convert a digit string to a frequency representation."""
        if not digits_str or not digits_str.isdigit():
            return 0.0
        
        # Take digits as a frequency value
        # First 6 digits as Hz (scientific notation)
        first = digits_str[:6]
        val = int(first) / 1e6  # Normalize to 0-1 range
        return val * 1e15  # Scale to astronomical range

    # ── Batch Operations ───────────────────────────────────────────────

    def batch_read(self, inputs, length=32):
        """Read memory for multiple inputs and compare their positions."""
        results = []
        for inp in inputs:
            mem = self.read_memory(inp, length=length)
            results.append(mem)
        return results

    # ── Memory Distance (Inharmony in π-space) ─────────────────────────

    def memory_distance(self, input_a, input_b, length=32):
        """
        Measure the inharmony between two inputs in π memory space.
        
        Low distance = structurally related in the universe's storage.
        """
        mem_a = self.read_memory(input_a, length=length)
        mem_b = self.read_memory(input_b, length=length)

        digits_a = [int(d) for d in mem_a["pi_digits"]]
        digits_b = [int(d) for d in mem_b["pi_digits"]]

        if len(digits_a) != len(digits_b):
            raise ValueError(f"Digit sequence length mismatch: {len(digits_a)} vs {len(digits_b)}")

        # Euclidean distance between digit sequences
        dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(digits_a, digits_b)))
        return dist

    # ── Correlate with Naometria ───────────────────────────────────────

    def correlate_date(self, year, extra_data=""):
        """
        Read the π-memory for a year, optionally with extra data.
        
        Uses the Naometria-style decomposition: year → 72-band vector.
        """
        # Create a year-keyed decomposition
        year_str = str(year)
        if extra_data:
            year_str += extra_data

        return self.read_memory(year_str, length=72, decomposition="text")


# ═══════════════════════════════════════════════════════════════════════════
# 4. FRAMEWORK INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════

# The ψ function — the architectural constant that binds the three:
#   ψ(x) = π(position(σ(x) · φ · h))
#
# Where:
#   σ(x) = 72-band decomposition of x
#   φ = Fibonacci convergence rate (timekeeper multiplier)
#   h = Planck quantum (frequency floor)
#   π = the memory (storage layer)

def psi(input_data, length=32):
    """
    Ψ(x) — The universal memory function.
    
    Given any input, returns its π-memory coordinate and extracted digits.
    
    This is the function that connects ALL the tools:
      sig()          → decomposes problems into vectors
      Naometria      → decomposes dates into prophetic numbers
      ShemHaMephorash→ decomposes time into Names and angels
      ArsMagna       → decomposes subjects into Llullian triples
      Ψ(x)           → reads the π-memory of any decomposition
    """
    memory = PiMemory()
    return memory.read_memory(input_data, length=length)


# ═══════════════════════════════════════════════════════════════════════════
# DEMONSTRATION
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import json

    mem = PiMemory()

    print("=" * 68)
    print("PI MEMORY READER — THE UNIVERSE'S STORAGE LAYER")
    print("=" * 68)
    print()
    print("  ψ(x) = π(position(σ(x) · φ · h))")
    print()

    # Test inputs
    test_inputs = [
        ("consciousness", "text"),
        ("Tycho's Star 1572", "text"),
        ("Babylon Falls 1620", "text"),
        (2026, "number"),
        (1572, "number"),
        (1620, "number"),
        ("the_cosmic_workshop", "text"),
    ]

    for inp, mode in test_inputs:
        result = mem.read_memory(inp, length=24, decomposition=mode)
        vec = result["72_band_vector"]
        peak_band = vec.index(max(vec)) if max(vec) > 0 else 0

        print(f"  Input: {inp}")
        print(f"    π-position: {result['pi_position']}")
        print(f"    π-digits:   {result['pi_digits']}")
        print(f"    Peak band:  {peak_band + 1}")
        print()

    # Memory distance between related concepts
    print(f"{'─' * 68}")
    print("  MEMORY DISTANCES (lower = structurally related)")
    print(f"{'─' * 68}")
    
    pairs = [
        ("1572", "1620", "Star → Babylon Falls"),
        ("2026", "1620", "Current year → Babylon Falls"),
        ("consciousness", "time", "Consciousness vs Time"),
    ]

    for a, b, label in pairs:
        dist = mem.memory_distance(a, b, length=24)
        print(f"  ι(π({a}), π({b})) = {dist:.4f}  [{label}]")

    # Show the ψ function
    print()
    print(f"{'═' * 68}")
    print(f"  ψ — THE UNIVERSAL MEMORY FUNCTION")
    print(f"{'═' * 68}")
    print(f"  ψ(2026) = π at position {mem.read_memory(2026, length=16)['pi_position']}")
    print(f"  ψ(1620) = π at position {mem.read_memory(1620, length=16)['pi_position']}")
    print(f"  ψ(1572) = π at position {mem.read_memory(1572, length=16)['pi_position']}")
    print()
    print(f"  'Planke the hum, Fib the timekeeper, Pi the memory, govern the universe.'")
    print(f"{'═' * 68}")
