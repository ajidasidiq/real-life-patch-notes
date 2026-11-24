#!/usr/bin/env python3
"""Real-Life Patch Notes: pick the funniest one-line patch note.

Six candidate patch notes are scored against the judge's published
criteria (real-life or human-biology bug, genuinely funny on first read,
reads like a real release note, names a specific recognisable bug, uses
its 160 characters well) and the winner is written to /output/entry.txt.

Deterministic: no clock, no randomness, no network, no environment
input. The same candidates always produce the same winner.
"""

import os
import re

MAX_CHARS = 160

CANDIDATES = [
    "v3.2.1: fixed a bug where the brain replayed your most embarrassing "
    "moment from 2014 every night at 3 a.m. instead of sleeping.",
    "v2.7.3: fixed a bug where the brain auto-played the same song on loop "
    "for 72 hours with no skip button.",
    "v1.4.8: fixed a bug where the bladder sent its low-battery warning "
    "only after the last restroom had closed.",
    "v2.0.7: fixed a bug where yawning in a meeting triggered a chain "
    "reaction across every attendee in the room.",
    "v4.1.0: fixed a bug where your legs fell asleep faster than the rest "
    "of you and woke up as pins and needles.",
    "v3.0.2: fixed a bug where sneezing in public froze every nearby "
    "conversation for half a second.",
]

# Concrete details the judge rewards: a named body part, a clock time or
# year, a measured quantity, a named everyday situation.
BODY_PARTS = ["brain", "bladder", "legs", "ear", "stomach", "eyes", "hands"]
SITUATIONS = ["meeting", "restroom", "public", "sleeping", "night", "exam"]
PUNCH_MARKERS = [
    "instead of", "only after", "no skip button", "chain reaction",
    "pins and needles", "half a second", "every night",
]
FILLER_WORDS = ["very", "really", "just", "quite", "basically"]


def score(line):
    """Score one candidate line against the judge's criteria."""
    points = 0
    reasons = []

    # Criterion 3: reads like a real release note.
    if re.match(r"^v\d+\.\d+\.\d+: ", line):
        points += 20
        reasons.append("versioned release-note format (+20)")
    if "fixed a bug where" in line:
        points += 20
        reasons.append("terse fix register (+20)")

    # Criterion 4: names a specific, recognisable bug.
    # Word-boundary matches only: "ear" must not match inside "nearby".
    body_hits = [w for w in BODY_PARTS
                 if re.search(r"\b%s\b" % w, line.lower())]
    points += 4 * len(body_hits)
    if body_hits:
        reasons.append("body part named: %s (+%d)" % (", ".join(body_hits), 4 * len(body_hits)))
    if re.search(r"\b(19|20)\d\d\b", line):
        points += 5
        reasons.append("concrete year (+5)")
    if re.search(r"\b\d{1,2}(:\d\d)?\s*(a\.m\.|p\.m\.)", line):
        points += 5
        reasons.append("concrete clock time (+5)")
    if re.search(r"\b\d+\s*(hours|seconds|minutes|ms)\b", line):
        points += 4
        reasons.append("measured quantity (+4)")
    sit_hits = [w for w in SITUATIONS
                if re.search(r"\b%s\b" % w, line.lower())]
    points += 3 * len(sit_hits)
    if sit_hits:
        reasons.append("everyday situation: %s (+%d)" % (", ".join(sit_hits), 3 * len(sit_hits)))

    # Criterion 2: the joke lands on first read (contrast / reversal).
    punch_hits = [m for m in PUNCH_MARKERS if m in line.lower()]
    points += 6 * len(punch_hits)
    if punch_hits:
        reasons.append("punch contrast: %s (+%d)" % (", ".join(punch_hits), 6 * len(punch_hits)))

    # Criterion 5: uses its 160 characters well, no padding.
    length = len(line)
    if length > MAX_CHARS:
        points -= 50
        reasons.append("over 160 chars (-50)")
    elif length >= 120:
        points += 10
        reasons.append("uses 120-160 chars well (+10)")
    elif length >= 100:
        points += 5
        reasons.append("uses 100-119 chars (+5)")
    filler = [w for w in FILLER_WORDS if re.search(r"\b%s\b" % w, line.lower())]
    points -= 5 * len(filler)
    if filler:
        reasons.append("filler words (-%d)" % (5 * len(filler)))

    return points, reasons


def pick_winner():
    """Score every candidate and return the best valid line."""
    best = None
    for line in CANDIDATES:
        if len(line) > MAX_CHARS or not line.strip():
            continue
        points, reasons = score(line)
        print("%3d  %s" % (points, line))
        for reason in reasons:
            print("       - %s" % reason)
        if best is None or points > best[0]:
            best = (points, line)
    if best is None:
        raise SystemExit("no valid candidate within 160 characters")
    return best[1]


def main():
    winner = pick_winner()
    print("WINNER (%d chars): %s" % (len(winner), winner))
    out_dir = "/output" if os.path.isdir("/output") else "output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(winner)
    print("wrote %s" % path)


if __name__ == "__main__":
    main()
