"""Сущность «Член семьи»."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class FamilyMember:
    member_id: Optional[int]
    full_name: str
    role: str
