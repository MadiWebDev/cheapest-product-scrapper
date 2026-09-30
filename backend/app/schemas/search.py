"""Search-related schemas."""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SearchFilters(BaseModel):
    """Schema for search filters."""
    country: Optional[str] = Field(None, description="ISO 3166-1 alpha-2 country code")
    min_trust: Optional[float] = Field(None, ge=0, le=10, description="Minimum trust score")
    max_price: Optional[float] = Field(None, gt=0, description="Maximum price per unit")
    limit: int = Field(20, ge=1, le=100, description="Number of results to return")


class SearchResponse(BaseModel):
    """Schema for search results with suppliers."""
    id: uuid.UUID
    user_id: uuid.UUID
    detected_category: Optional[str]
    detected_attributes: Optional[Dict[str, Any]]
    confidence_score: Optional[float]
    filters_applied: Optional[Dict[str, Any]]
    status: str
    created_at: datetime
    suppliers: Optional[List[uuid.UUID]] = None
    
    class Config:
        from_attributes = True


class SearchStatusResponse(BaseModel):
    """Schema for search status polling."""
    search_id: uuid.UUID
    status: str  # processing, complete, failed, needs_clarification
    detected_category: Optional[str] = None
    confidence_score: Optional[float] = None
    error_message: Optional[str] = None


class SearchHistoryResponse(BaseModel):
    """Schema for user's search history."""
    searches: List[SearchResponse]
    total: int
