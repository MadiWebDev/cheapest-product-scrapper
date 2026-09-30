"""Supplier-related schemas."""
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class SupplierResponse(BaseModel):
    """Schema for supplier response."""
    id: uuid.UUID
    name: str
    country_code: str
    categories: List[str]
    min_order_qty: int
    price_usd_per_unit: float
    trust_score: float
    verified: bool
    website_url: str
    contact_email: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SupplierListResponse(BaseModel):
    """Schema for paginated supplier list response."""
    suppliers: List[SupplierResponse]
    total: int
    page: int
    page_size: int
