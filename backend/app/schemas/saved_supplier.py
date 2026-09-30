"""Saved supplier schemas."""
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class SavedSupplierCreate(BaseModel):
    """Schema for saving a supplier."""
    supplier_id: uuid.UUID
    notes: Optional[str] = Field(None, max_length=1000)


class SavedSupplierResponse(BaseModel):
    """Schema for saved supplier response."""
    id: uuid.UUID
    user_id: uuid.UUID
    supplier_id: uuid.UUID
    notes: Optional[str]
    created_at: datetime
    supplier: Optional[dict] = None  # Populated when needed
    
    class Config:
        from_attributes = True


class SavedSupplierListResponse(BaseModel):
    """Schema for list of saved suppliers."""
    saved_suppliers: List[SavedSupplierResponse]
    total: int
