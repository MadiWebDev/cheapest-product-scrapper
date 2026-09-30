"""Search router for supplier results, history, and saved suppliers."""
import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.database import get_db
from app.models.user import User
from app.models.search import Search
from app.models.supplier import Supplier
from app.models.saved_supplier import SavedSupplier
from app.schemas.common import SuccessResponse
from app.schemas.supplier import SupplierResponse, SupplierListResponse
from app.schemas.search import SearchHistoryResponse, SearchFilters
from app.schemas.saved_supplier import SavedSupplierCreate, SavedSupplierResponse, SavedSupplierListResponse
from app.auth import get_current_user
from app.services.matching import match_suppliers

router = APIRouter(prefix="/api/search", tags=["Search"])


@router.get("/results/{search_id}", response_model=SuccessResponse)
def get_search_results(
    search_id: uuid.UUID,
    country: Optional[str] = Query(None, description="Filter by country code"),
    min_trust: Optional[float] = Query(None, ge=0, le=10, description="Minimum trust score"),
    max_price: Optional[float] = Query(None, gt=0, description="Maximum price per unit"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get supplier results for a search with optional filters.
    
    Args:
        search_id: Search ID
        country: Optional filter by country code
        min_trust: Optional minimum trust score
        max_price: Optional maximum price filter
        limit: Number of results to return
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Paginated list of suppliers sorted by composite score
        
    Raises:
        HTTPException: If search not found or not complete
    """
    search = db.query(Search).filter(
        Search.id == search_id,
        Search.user_id == current_user.id
    ).first()
    
    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found"
        )
    
    if search.status != "complete":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Search is not complete. Current status: {search.status}"
        )
    
    # Build filters
    filters = {}
    if country:
        filters["country"] = country
    if min_trust:
        filters["min_trust"] = min_trust
    if max_price:
        filters["max_price"] = max_price
    
    # Get matched suppliers
    suppliers = match_suppliers(str(search.id), filters, db)
    
    # Apply limit
    suppliers = suppliers[:limit]
    
    supplier_responses = [SupplierResponse.model_validate(s) for s in suppliers]
    
    return SuccessResponse(
        data={
            "suppliers": [s.model_dump() for s in supplier_responses],
            "total": len(supplier_responses),
            "search_id": str(search.id),
            "detected_category": search.detected_category,
            "confidence_score": search.confidence_score
        }
    )


@router.get("/history", response_model=SuccessResponse)
def get_search_history(
    limit: int = Query(50, ge=1, le=100, description="Number of searches to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's search history.
    
    Args:
        limit: Number of searches to return
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of past searches
    """
    searches = db.query(Search).filter(
        Search.user_id == current_user.id
    ).order_by(Search.created_at.desc()).limit(limit).all()
    
    search_data = []
    for search in searches:
        search_data.append({
            "id": str(search.id),
            "detected_category": search.detected_category,
            "confidence_score": search.confidence_score,
            "status": search.status,
            "created_at": search.created_at.isoformat(),
            "filters_applied": search.filters_applied
        })
    
    return SuccessResponse(
        data={"searches": search_data, "total": len(search_data)}
    )


@router.get("/suppliers/{supplier_id}", response_model=SuccessResponse)
def get_supplier_detail(
    supplier_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get full supplier detail.
    
    Args:
        supplier_id: Supplier ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Full supplier information
        
    Raises:
        HTTPException: If supplier not found
    """
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    supplier_response = SupplierResponse.model_validate(supplier)
    
    return SuccessResponse(data=supplier_response.model_dump())


@router.post("/save/{supplier_id}", response_model=SuccessResponse)
def save_supplier(
    supplier_id: uuid.UUID,
    notes_data: SavedSupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Save a supplier to user's watchlist.
    
    Args:
        supplier_id: Supplier ID to save
        notes_data: Optional notes for the supplier
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Confirmation of saved supplier
        
    Raises:
        HTTPException: If supplier not found or already saved
    """
    # Check if supplier exists
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    # Check if already saved
    existing = db.query(SavedSupplier).filter(
        SavedSupplier.user_id == current_user.id,
        SavedSupplier.supplier_id == supplier_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supplier already saved"
        )
    
    # Create saved supplier
    saved_supplier = SavedSupplier(
        user_id=current_user.id,
        supplier_id=supplier_id,
        notes=notes_data.notes
    )
    
    db.add(saved_supplier)
    db.commit()
    db.refresh(saved_supplier)
    
    return SuccessResponse(
        data={"saved_supplier_id": str(saved_supplier.id)},
        message="Supplier saved successfully"
    )


@router.get("/saved", response_model=SuccessResponse)
def get_saved_suppliers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's saved suppliers.
    
    Args:
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of saved suppliers with full details
    """
    saved_suppliers = db.query(SavedSupplier).filter(
        SavedSupplier.user_id == current_user.id
    ).order_by(SavedSupplier.created_at.desc()).all()
    
    result = []
    for saved in saved_suppliers:
        supplier = db.query(Supplier).filter(Supplier.id == saved.supplier_id).first()
        supplier_data = SupplierResponse.model_validate(supplier).model_dump() if supplier else None
        result.append({
            "id": str(saved.id),
            "supplier_id": str(saved.supplier_id),
            "notes": saved.notes,
            "created_at": saved.created_at.isoformat(),
            "supplier": supplier_data
        })
    
    return SuccessResponse(
        data={"saved_suppliers": result, "total": len(result)}
    )
