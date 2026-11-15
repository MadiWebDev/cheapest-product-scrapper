from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Optional

class Availability(str, Enum):
    IN_STOCK="in_stock"; LOW_STOCK="low_stock"; PREORDER="preorder"; BACKORDER="backorder"; OUT_OF_STOCK="out_of_stock"; UNKNOWN="unknown"
class Condition(str, Enum):
    NEW="new"; USED="used"; REFURBISHED="refurbished"; OPEN_BOX="open-box"

@dataclass
class RawOffer:
    connector: str; title: str; url: str; price: Optional[float]; currency: str="USD"
    image: Optional[str]=None; gtin: Optional[str]=None; asin: Optional[str]=None; mpn: Optional[str]=None
    brand: Optional[str]=None; model: Optional[str]=None; seller_name: Optional[str]=None
    seller_rating: Optional[float]=None; seller_feedback_count: int=0; seller_age_years: float=0.0
    rating: Optional[float]=None; review_count: int=0; shipping_price: Optional[float]=None
    ships_to: list[str]=field(default_factory=list); availability: str="unknown"; stock_qty: Optional[int]=None
    delivery_days: Optional[int]=None; condition: str="new"; warranty: bool=False; returns_days: int=0
    buyer_protection: bool=False; official_store: bool=False; was_price: Optional[float]=None
    attributes: dict[str,Any]=field(default_factory=dict); demo: bool=False
    def to_dict(self): return asdict(self)

@dataclass
class LandedBreakdown:
    item: float; shipping: float; duty: float; tax: float; handling: float; fx_margin: float; total: float; currency: str
    provenance: dict[str,str]=field(default_factory=dict)  # component -> exact|estimated
    def to_dict(self): return asdict(self)

@dataclass
class ScoredOffer:
    offer: RawOffer; landed: Optional[LandedBreakdown]=None; quality_score: float=0.0
    quality_explanation: dict[str,Any]=field(default_factory=dict); value_score: float=0.0
    availability: str="unknown"; badges: list[str]=field(default_factory=list)
    def to_dict(self):
        d=asdict(self); return d
