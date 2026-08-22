"""Currency utilities — paise ↔ rupees conversion."""


def paise_to_rupees(paise: int) -> float:
    """Convert paise to rupees."""
    return paise / 100


def rupees_to_paise(rupees: float) -> int:
    """Convert rupees to paise."""
    return int(round(rupees * 100))


def format_inr(paise: int) -> str:
    """Format paise as Indian Rupee string with comma separation."""
    rupees = paise / 100
    if rupees >= 10_000_000:
        return f"₹{rupees / 10_000_000:.2f}Cr"
    elif rupees >= 100_000:
        return f"₹{rupees / 100_000:.2f}L"
    elif rupees >= 1_000:
        return f"₹{rupees:,.0f}"
    else:
        return f"₹{rupees:.2f}"
