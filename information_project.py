#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Information Theory Project – Python Implementation

Based exactly on Final Project_27_11_2024.pdf:
Part 1: Input  = "Text.txt"       → Output: list of symbols + probabilities
Part 2: Input  = "Text.txt" + Part 1 result → Output: binary sequence
Part 3: Input  = binary sequence from Part 2 → Output: text identical to "Text.txt"
Part 4: Input  = binary sequence from Part 2 → Output: Hamming-coded binary sequence
Part 5: Input  = Hamming-coded sequence from Part 4 → Output: sequence with errors
Part 6: Input  = sequence with errors from Part 5 → Output: binary sequence identical to Part 2
"""

import collections
import heapq
import random
from typing import Dict, List, Tuple

# ----------------------------------------
# File names (inputs/outputs of each part)
# ----------------------------------------

INPUT_TEXT_FILE = "Text.txt"

PART1_SYMBOLS_FILE = "part1_symbols.txt"
HUFFMAN_CODES_FILE = "huffman_codes.txt"

PART2_BITS_FILE = "part2_bits.txt"
PART3_DECODED_TEXT_FILE = "part3_decoded.txt"

PART4_HAMMING_BITS_FILE = "part4_hamming_bits.txt"
PART4_PAD_META_FILE = "part4_pad.txt"

PART5_CORRUPTED_BITS_FILE = "part5_corrupted_bits.txt"
PART6_RECOVERED_BITS_FILE = "part6_recovered_bits.txt"


# ==========================
# Helper: file I/O
# ==========================

def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_text_file(path: str, data: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)


# ==========================
# Part 1 – Symbol probabilities
# ==========================

def compute_symbol_probabilities(text: str) -> Dict[str, float]:
    if not text:
        return {}
    counts = collections.Counter(text)
    total = sum(counts.values())
    return {sym: counts[sym] / total for sym in counts}


def save_part1_output(probabilities: Dict[str, float], path: str) -> None:
    """
    Output format: each line = repr(symbol)\tprobability
    This matches: "list of all unique symbols from the text with their probabilities".
    """
    lines = ["# symbol\tprobability"]
    for sym, p in sorted(probabilities.items(), key=lambda kv: kv[0]):
        # Use repr so that space/newline/tab are clearly visible
        lines.append(f"{repr(sym)}\t{p:.10f}")
    write_text_file(path, "\n".join(lines))


# ==========================
# Huffman Coding (Parts 2 & 3)
# ==========================

class HuffmanNode:
    def __init__(self, symbol=None, prob: float = 0.0, left=None, right=None):
        self.symbol = symbol
        self.prob = prob
        self.left = left
        self.right = right

    def __lt__(self, other: "HuffmanNode") -> bool:
        return self.prob < other.prob


def build_huffman_tree(probabilities: Dict[str, float]) -> HuffmanNode:
    """Build Huffman tree from symbol probabilities."""
    heap: List[HuffmanNode] = [HuffmanNode(sym, p) for sym, p in probabilities.items()]
    if not heap:
        return None
    heapq.heapify(heap)

    # Edge case: only one symbol
    if len(heap) == 1:
        only = heap[0]
        return HuffmanNode(symbol=None, prob=only.prob, left=only, right=None)

    while len(heap) > 1:
        n1 = heapq.heappop(heap)
        n2 = heapq.heappop(heap)
        parent = HuffmanNode(symbol=None, prob=n1.prob + n2.prob, left=n1, right=n2)
        heapq.heappush(heap, parent)
    return heap[0]


def build_huffman_codes(root: HuffmanNode) -> Dict[str, str]:
    """Return mapping: symbol -> binary code."""
    codes: Dict[str, str] = {}
    if root is None:
        return codes

    def traverse(node: HuffmanNode, prefix: str) -> None:
        if node.symbol is not None:
            # Leaf
            codes[node.symbol] = prefix if prefix else "0"  # if only one symbol
            return
        if node.left:
            traverse(node.left, prefix + "0")
        if node.right:
            traverse(node.right, prefix + "1")

    traverse(root, "")
    return codes


def huffman_encode(text: str, codes: Dict[str, str]) -> str:
    return "".join(codes[ch] for ch in text)


def huffman_decode(bits: str, root: HuffmanNode) -> str:
    if root is None:
        return ""
    result: List[str] = []
    node = root
    for b in bits:
        node = node.left if b == "0" else node.right
        if node.symbol is not None:
            result.append(node.symbol)
            node = root
    return "".join(result)


def save_huffman_codes(codes: Dict[str, str], path: str) -> None:
    """
    Store codes for documentation:
    each line = repr(symbol)\tcode
    """
    lines = ["# symbol\tcode"]
    for sym, code in sorted(codes.items(), key=lambda kv: kv[0]):
        lines.append(f"{repr(sym)}\t{code}")
    write_text_file(path, "\n".join(lines))


# ==========================
# Part 4 & 6 – Hamming(7,4)
# ==========================

def _bitstr_to_int_list(bits: str) -> List[int]:
    return [1 if b == "1" else 0 for b in bits]


def _int_list_to_bitstr(bits: List[int]) -> str:
    return "".join("1" if b else "0" for b in bits)


def hamming_7_4_encode(bitstring: str) -> Tuple[str, int]:
    """
    Input (Part 4): binary sequence from Part 2.
    Output (Part 4): Hamming(7,4)-encoded binary sequence + pad_bits.

    pad_bits is how many '0's were added at the end of bitstring
    to make length multiple of 4.
    """
    if not bitstring:
        return "", 0

    pad_bits = (4 - (len(bitstring) % 4)) % 4
    bitstring_padded = bitstring + "0" * pad_bits

    encoded_bits: List[int] = []

    for i in range(0, len(bitstring_padded), 4):
        d1 = int(bitstring_padded[i])
        d2 = int(bitstring_padded[i + 1])
        d3 = int(bitstring_padded[i + 2])
        d4 = int(bitstring_padded[i + 3])

        # Hamming(7,4):
        # Positions: 1 2 3 4 5 6 7
        # Bits:     p1 p2 d1 p4 d2 d3 d4
        # Even parity:
        p1 = d1 ^ d2 ^ d4         # covers 1,3,5,7
        p2 = d1 ^ d3 ^ d4         # covers 2,3,6,7
        p4 = d2 ^ d3 ^ d4         # covers 4,5,6,7

        codeword = [p1, p2, d1, p4, d2, d3, d4]
        encoded_bits.extend(codeword)

    return _int_list_to_bitstr(encoded_bits), pad_bits


def hamming_7_4_decode(encoded_bits: str, pad_bits: int) -> str:
    """
    Input (Part 6): sequence of bits from Part 5 (after errors) or Part 4.
    Output (Part 6): corrected data bits; padding removed.
    """
    if not encoded_bits:
        return ""

    if len(encoded_bits) % 7 != 0:
        raise ValueError("Hamming(7,4) encoded length must be a multiple of 7.")

    bits = _bitstr_to_int_list(encoded_bits)
    data_bits: List[int] = []

    for i in range(0, len(bits), 7):
        b1, b2, b3, b4, b5, b6, b7 = bits[i:i + 7]

        # Syndrome (even parity)
        s1 = b1 ^ b3 ^ b5 ^ b7   # check positions 1,3,5,7
        s2 = b2 ^ b3 ^ b6 ^ b7   # check positions 2,3,6,7
        s4 = b4 ^ b5 ^ b6 ^ b7   # check positions 4,5,6,7

        error_pos = s1 + (s2 << 1) + (s4 << 2)  # 1..7 if error, 0 if none

        if error_pos != 0:
            idx = i + error_pos - 1
            bits[idx] ^= 1  # flip erroneous bit
            b1, b2, b3, b4, b5, b6, b7 = bits[i:i + 7]

        # Extract data bits d1,d2,d3,d4 = positions 3,5,6,7
        data_bits.extend([b3, b5, b6, b7])

    if pad_bits > 0:
        data_bits = data_bits[:-pad_bits]

    return _int_list_to_bitstr(data_bits)


# ==========================
# Part 5 – Add artificial errors
# ==========================

def add_errors(bitstring: str, interval: int = 50, seed: int = 123) -> str:
    """
    Input (Part 5): Hamming-coded sequence from Part 4.
    Goal: add errors with a certain interval.
    Output: binary sequence after Hamming code with artificially created errors.

    Implementation: flip one bit every 'interval' bits.
    """
    if not bitstring or interval <= 0:
        return bitstring

    random.seed(seed)
    bits = list(bitstring)

    # Optional random offset so we don't always start at index 0
    start_index = random.randint(0, max(0, interval - 1)) if interval > 1 else 0

    for i in range(start_index, len(bits), interval):
        bits[i] = "0" if bits[i] == "1" else "1"

    return "".join(bits)


# ==========================
# Full pipeline driver
# ==========================

def main() -> None:
    # -------------------------
    # Part 1: Symbol probabilities
    # -------------------------
    text = read_text_file(INPUT_TEXT_FILE)
    probabilities = compute_symbol_probabilities(text)
    save_part1_output(probabilities, PART1_SYMBOLS_FILE)

    # -------------------------
    # Part 2: Huffman encoding
    # -------------------------
    huff_root = build_huffman_tree(probabilities)
    huff_codes = build_huffman_codes(huff_root)
    save_huffman_codes(huff_codes, HUFFMAN_CODES_FILE)

    encoded_bits = huffman_encode(text, huff_codes)
    write_text_file(PART2_BITS_FILE, encoded_bits)

    # -------------------------
    # Part 3: Huffman decoding
    # -------------------------
    decoded_text = huffman_decode(encoded_bits, huff_root)
    write_text_file(PART3_DECODED_TEXT_FILE, decoded_text)

    # Optionally, you can check equality manually:
    #   diff = (decoded_text == text)

    # -------------------------
    # Part 4: Hamming encoding
    # -------------------------
    hamming_bits, pad_bits = hamming_7_4_encode(encoded_bits)
    write_text_file(PART4_HAMMING_BITS_FILE, hamming_bits)
    write_text_file(PART4_PAD_META_FILE, str(pad_bits))

    # -------------------------
    # Part 5: Add errors
    # -------------------------
    # Choose any interval you want; keep it visible in the report.
    error_interval = 50
    corrupted_bits = add_errors(hamming_bits, interval=error_interval, seed=2024)
    write_text_file(PART5_CORRUPTED_BITS_FILE, corrupted_bits)

    # -------------------------
    # Part 6: Hamming decoding and correction
    # -------------------------
    recovered_bits = hamming_7_4_decode(corrupted_bits, pad_bits)
    write_text_file(PART6_RECOVERED_BITS_FILE, recovered_bits)

    # Now:
    #  - PART2_BITS_FILE and PART6_RECOVERED_BITS_FILE must be identical.
    #  - If you decode recovered_bits with Huffman, you get exactly Text.txt again.


if __name__ == "__main__":
    main()
