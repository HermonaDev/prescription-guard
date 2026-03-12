# src/guard_logic.py
"""Core guard logic for prescription safety.

This module provides a fast lookup for drug‑drug interactions and a
`check_safety` function that evaluates a new drug against a list of
current medications and known allergies.

The processed interaction data is stored in ``data/processed_ddi.pkl``
as a pandas DataFrame with the columns:

- ``Drug 1``
- ``Drug 2``
- ``Interaction Description``
- ``Severity`` ("Major", "Moderate", "Minor")

The ``Severity`` column is mapped to a colour code used by the guard:

- ``Major``   → ``Red``
- ``Moderate``→ ``Yellow``
- ``Minor``   → ``Green``
- ``Unknown`` → ``Gray`` (drug not present in the database)
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple

# ---------------------------------------------------------------------------
# Load processed data (executed once at import time)
# ---------------------------------------------------------------------------

_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "processed_ddi.pkl"

if not _DATA_PATH.is_file():
    raise FileNotFoundError(f"Processed interaction file not found at {_DATA_PATH}")

# The DataFrame contains the interaction information.
_df: pd.DataFrame = pd.read_pickle(_DATA_PATH)

# Normalise drug names to a consistent case for look‑ups.
_df["Drug 1"] = _df["Drug 1"].str.strip().str.lower()
_df["Drug 2"] = _df["Drug 2"].str.strip().str.lower()

# Map severity strings to colour codes.
_SEVERITY_TO_COLOR = {
    "Major": "Red",
    "Moderate": "Yellow",
    "Minor": "Green",
}

# Build a fast lookup structure.
# We store both (drug_a, drug_b) and (drug_b, drug_a) because interactions are symmetric.
_interaction_lookup: Dict[Tuple[str, str], Dict[str, str]] = {}

for _, row in _df.iterrows():
    drug_a = row["Drug 1"]
    drug_b = row["Drug 2"]
    severity = row["Severity"]
    description = row["Interaction Description"]
    colour = _SEVERITY_TO_COLOR.get(severity, "gray")
    # Store lower‑case keys for UI compatibility
    entry = {
        "severity": severity.lower(),
        "description": description,
        "color": colour.lower(),
    }
    _interaction_lookup[(drug_a, drug_b)] = entry
    _interaction_lookup[(drug_b, drug_a)] = entry  # symmetric lookup

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _normalise_drug(name: str) -> str:
    """Return a lower‑cased, stripped version of a drug name.

    The source data stores drug names in a canonical lower‑case form, so we
    apply the same transformation to user‑supplied values.
    """
    return name.strip().lower()


def check_safety(
    new_drug: str,
    current_medications: List[str] | Tuple[str, ...],
    allergies: List[str] | Tuple[str, ...],
) -> List[Dict[str, str]]:
    """Check a prospective drug against allergies and existing meds.

    Parameters
    ----------
    new_drug: str
        The drug the prescriber wants to add.
    current_medications: list[str]
        List of drugs the patient is already taking.
    allergies: list[str]
        List of drugs the patient is allergic to.

    Returns
    -------
    list[dict]
        A list of conflict dictionaries. Each dictionary contains:
        ``"Drug"`` – the drug that caused the conflict (either the new drug
        or the interacting medication),
        ``"Severity"`` – ``"Major"``, ``"Moderate"``, ``"Minor"`` or
        ``"Unknown"`` when the interaction is not in the database,
        ``"Description"`` – the interaction description (or a short note for
        allergies/unknown), and ``"Color"`` – the colour code associated with
        the severity.
    """
    new_drug_norm = _normalise_drug(new_drug)
    conflicts: List[Dict[str, str]] = []

    # 1️⃣ Allergy check – highest priority (RED ALERT)
    if any(_normalise_drug(a) == new_drug_norm for a in allergies):
        conflicts.append(
            {
                "drug": new_drug,
                "severity": "major",
                "description": f"Allergy to {new_drug}",
                "color": "red",
            }
        )
        # We still continue to report drug‑drug interactions, but the allergy
        # entry will always be present and dominate any UI decision.

    # 2️⃣ Drug‑drug interaction checks
    for med in current_medications:
        med_norm = _normalise_drug(med)
        # Skip self‑interaction (should not happen but guard against it)
        if med_norm == new_drug_norm:
            continue
        key = (new_drug_norm, med_norm)
        interaction = _interaction_lookup.get(key)
        if interaction:
            conflicts.append(
                {
                    "drug": med,
                    "severity": interaction["severity"],
                    "description": interaction["description"],
                    "color": interaction["color"],
                }
            )
        else:
            # Unknown interaction – Gray status
            conflicts.append(
                {
                    "drug": med,
                    "severity": "unknown",
                    "description": "No known interaction",
                    "color": "gray",
                }
            )

    return conflicts


__all__ = ["check_safety"]
