#!/usr/bin/env python3
"""ColdDirect's permanent ten-family money-keyword and London-intent mapping.

Nine canonical landing hubs serve ten keyword families: cellar repair and cellar
cooler repair share one hub. Query classification is specific-first so generic
fridge/freezer and catering rows do not also count their commercial variants.
"""
from __future__ import annotations

import re

TARGETS = [
    {"id": "cold-room", "label": "Cold room repair London", "labelFa": "تعمیر سردخانه لندن", "slug": "cold-room-repair-london"},
    {"id": "commercial-fridge", "label": "Commercial fridge repair London", "labelFa": "تعمیر یخچال تجاری لندن", "slug": "commercial-fridge-repair-london"},
    {"id": "commercial-freezer", "label": "Commercial freezer repair London", "labelFa": "تعمیر فریزر تجاری لندن", "slug": "commercial-freezer-repair-london"},
    {"id": "fridge", "label": "Fridge repair London", "labelFa": "تعمیر یخچال لندن", "slug": "fridge-repair-london"},
    {"id": "freezer", "label": "Freezer repair London", "labelFa": "تعمیر فریزر لندن", "slug": "freezer-repair-london"},
    {"id": "cellar", "label": "Cellar repair London", "labelFa": "تعمیر سردخانه آبجو لندن", "slug": "cellar-cooler-repair-london"},
    {"id": "cellar-cooler", "label": "Cellar cooler repair London", "labelFa": "تعمیر کولر سردخانه آبجو لندن", "slug": "cellar-cooler-repair-london"},
    {"id": "air-conditioning", "label": "Air conditioning repair London", "labelFa": "تعمیر تهویه مطبوع لندن", "slug": "air-conditioning-repair-london"},
    {"id": "catering", "label": "Catering repair London", "labelFa": "تعمیر تجهیزات پذیرایی لندن", "slug": "catering-repair-london"},
    {"id": "commercial-appliances", "label": "Commercial appliances repair London", "labelFa": "تعمیر تجهیزات تجاری لندن", "slug": "commercial-appliances-repair-london"},
]

INTENT_MODIFIERS = (
    "repair", "repairs", "service", "services", "maintenance", "installation",
    "breakdown", "fix", "diagnostics", "call out", "emergency", "24/7",
    "same day", "urgent", "fast response", "near me", "local", "engineer",
    "engineers", "technician", "specialist", "company", "commercial", "industrial",
)


def normalize_query(query: str) -> str:
    return re.sub(r"\s+", " ", str(query).lower().replace("-", " ")).strip()


def has_london_or_local_intent(query: str) -> bool:
    q = normalize_query(query)
    return "london" in q or "near me" in q or bool(re.search(r"\blocal\b", q))


def family_for_query(query: str) -> str | None:
    """Return one specific target ID, or None for unrelated/non-local queries."""
    q = normalize_query(query)
    if not has_london_or_local_intent(q):
        return None
    if re.search(r"\bcold\s+rooms?\b", q):
        return "cold-room"
    if "cellar" in q:
        if "cooler" in q or "cooling" in q or "beer" in q:
            return "cellar-cooler"
        return "cellar"
    if "air conditioning" in q or "air con" in q or re.search(r"\bac\b", q):
        return "air-conditioning"
    if "appliance" in q or ("commercial" in q and "catering" in q):
        return "commercial-appliances"
    if "catering" in q:
        return "catering"
    if "commercial" in q and "fridge" in q:
        return "commercial-fridge"
    if "commercial" in q and "freezer" in q:
        return "commercial-freezer"
    if "fridge" in q:
        return "fridge"
    if "freezer" in q:
        return "freezer"
    return None


def selftest() -> None:
    assert len(TARGETS) == 10 and len({t["id"] for t in TARGETS}) == 10
    examples = {
        "same day cold room repairs london": "cold-room",
        "london commercial fridge service": "commercial-fridge",
        "emergency commercial freezer repair london": "commercial-freezer",
        "london fridge repair": "fridge",
        "london fridge service": "fridge",
        "emergency freezer repair london": "freezer",
        "cellar repair london": "cellar",
        "beer cellar cooler service london": "cellar-cooler",
        "commercial air conditioning maintenance london": "air-conditioning",
        "same day catering repair london": "catering",
        "commercial catering equipment repair london": "commercial-appliances",
        "commercial appliance engineers london": "commercial-appliances",
        "local commercial fridge technician": "commercial-fridge",
    }
    for query, expected in examples.items():
        assert family_for_query(query) == expected, (query, family_for_query(query), expected)
    assert family_for_query("cellar cooler repair") is None, "non-local query must not enter London report"
    assert family_for_query("ice machine repair london") is None
    assert family_for_query("commercial fridge repair london") != family_for_query("fridge repair london")
    print("money_target_matrix selftest OK: 10 families, local intent, specific-first classification")


if __name__ == "__main__":
    selftest()
