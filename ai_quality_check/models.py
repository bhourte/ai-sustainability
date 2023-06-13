from dataclasses import dataclass


@dataclass(kw_only=True)
class Check:
    """Dataclass corresponding to check proposition in the file"""

    number: int
    text: str
    help_text: str = ""
    cluster: str = ""
