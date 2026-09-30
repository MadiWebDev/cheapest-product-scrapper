"""Supplier matching service using pgvector similarity search."""
import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.search import Search
from app.models.supplier import Supplier
from app.config import settings


def match_suppliers(search_id: str, filters: Dict[str, Any], db: Session) -> List[Supplier]:
    """
    Match suppliers using pgvector similarity search and re-ranking.
    
    Args:
        search_id: Search ID to get embedding from
        filters: Dictionary of filters (country, min_trust, max_price)
        db: Database session
        
    Returns:
        List of top suppliers sorted by composite score
    """
    # Get search record with embedding
    search = db.query(Search).filter(Search.id == uuid.UUID(search_id)).first()
    if not search or not search.detected_attributes:
        return []
    
    # Extract embedding from search (should be stored during analysis)
    # For now, we'll use a similarity-based approach without embedding
    # In production, this would use the actual pgvector similarity search
    
    # Build query with filters
    query = db.query(Supplier)
    
    # Apply country filter if provided
    if filters.get("country"):
        query = query.filter(Supplier.country_code == filters["country"])
    
    # Apply trust score filter if provided
    if filters.get("min_trust"):
        query = query.filter(Supplier.trust_score >= filters["min_trust"])
    
    # Apply price filter if provided
    if filters.get("max_price"):
        query = query.filter(Supplier.price_usd_per_unit <= filters["max_price"])
    
    # Get initial candidates (limit to 50)
    candidates = query.limit(settings.INITIAL_CANDIDATES_LIMIT).all()
    
    # Re-rank by composite score
    scored_suppliers = []
    for supplier in candidates:
        score = calculate_composite_score(supplier, filters, search)
        scored_suppliers.append((supplier, score))
    
    # Sort by score descending
    scored_suppliers.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N suppliers
    top_suppliers = [s[0] for s in scored_suppliers[:settings.TOP_SUPPLIERS_LIMIT]]
    
    return top_suppliers


def calculate_composite_score(supplier: Supplier, filters: Dict[str, Any], search: Search) -> float:
    """
    Calculate composite score for supplier ranking.
    
    Score formula:
    score = (similarity * 0.35) + (trust_score/10 * 0.40)
          + (price_fit * 0.15) + (moq_fit * 0.10)
    
    Args:
        supplier: Supplier object
        filters: Applied filters
        search: Search object for context
        
    Returns:
        Composite score (0-1)
    """
    # Similarity score (placeholder - in production use pgvector similarity)
    similarity = 0.7  # Default similarity
    
    # Trust score (normalized to 0-1)
    trust_score = supplier.trust_score / 10.0
    
    # Price fit score
    price_fit = 0.5
    if filters.get("max_price"):
        price_ratio = supplier.price_usd_per_unit / filters["max_price"]
        price_fit = max(0, 1 - min(price_ratio, 1))
    
    # MOQ fit score
    moq_fit = 0.5
    if filters.get("min_moq"):
        moq_fit = 1.0 if supplier.min_order_qty <= filters["min_moq"] else 0.3
    else:
        moq_fit = 1.0
    
    # Calculate composite score
    composite_score = (similarity * 0.35) + (trust_score * 0.40) + (price_fit * 0.15) + (moq_fit * 0.10)
    
    # Boost verified suppliers
    if supplier.verified:
        composite_score *= 1.1
    
    return min(composite_score, 1.0)
