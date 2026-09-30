"""Upload router for image upload and status polling."""
import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
from app.database import get_db
from app.models.user import User
from app.models.search import Search
from app.schemas.common import SuccessResponse, ErrorResponse
from app.schemas.search import SearchStatusResponse
from app.auth import get_current_user
from app.config import settings, PlanEnum
from app.workers.celery_app import analyze_image_task

router = APIRouter(prefix="/api/upload", tags=["Upload"])

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)


def check_rate_limit(user: User) -> None:
    """
    Check if user has exceeded their monthly search limit.
    
    Args:
        user: Current user
        
    Raises:
        HTTPException: If user has exceeded their limit
    """
    if user.plan == PlanEnum.FREE and user.searches_this_month >= settings.FREE_PLAN_SEARCHES_PER_MONTH:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Free plan limit of {settings.FREE_PLAN_SEARCHES_PER_MONTH} searches per month reached"
        )


def validate_image(file: UploadFile) -> None:
    """
    Validate uploaded image file.
    
    Args:
        file: Uploaded file
        
    Raises:
        HTTPException: If file is invalid
    """
    # Check file type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
        )
    
    # Check file size (10MB max)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Seek back to beginning
    
    max_size_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds {settings.MAX_IMAGE_SIZE_MB}MB limit"
        )


def upload_to_cloudinary(file: UploadFile, user_id: uuid.UUID) -> str:
    """
    Upload image file to Cloudinary.
    
    Args:
        file: Uploaded file
        user_id: User ID for the upload folder
        
    Returns:
        Cloudinary public ID for the uploaded file
        
    Raises:
        HTTPException: If upload fails
    """
    try:
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file.file,
            folder=f"sourcelens/{user_id}",
            resource_type="image",
            allowed_formats=["jpg", "png", "webp"],
            max_file_size=10 * 1024 * 1024  # 10MB
        )
        return result["public_id"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image to Cloudinary: {str(e)}"
        )


@router.post("/image", response_model=SuccessResponse)
async def upload_image(
    image: UploadFile = File(...),
    country: Optional[str] = Query(None, description="Filter by country code"),
    max_price: Optional[float] = Query(None, description="Maximum price per unit"),
    min_moq: Optional[int] = Query(None, description="Minimum order quantity"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a product image for analysis.
    
    Args:
        image: Product image file (jpeg/png/webp, max 10MB)
        country: Optional filter by country code
        max_price: Optional maximum price filter
        min_moq: Optional minimum order quantity filter
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Search ID and processing status
        
    Raises:
        HTTPException: If validation fails or upload fails
    """
    # Check rate limit
    check_rate_limit(current_user)
    
    # Validate image
    validate_image(image)
    
    # Upload to Cloudinary
    cloudinary_public_id = upload_to_cloudinary(image, current_user.id)
    
    # Create search record
    image_expires_at = datetime.utcnow() + timedelta(days=settings.IMAGE_EXPIRY_DAYS)
    filters_applied = {}
    if country:
        filters_applied["country"] = country
    if max_price:
        filters_applied["max_price"] = max_price
    if min_moq:
        filters_applied["min_moq"] = min_moq
    
    search = Search(
        user_id=current_user.id,
        image_s3_key=cloudinary_public_id,
        image_expires_at=image_expires_at,
        filters_applied=filters_applied,
        status="processing"
    )
    
    db.add(search)
    db.commit()
    db.refresh(search)
    
    # Increment user's search count
    current_user.searches_this_month += 1
    db.commit()
    
    # Trigger Celery task for image analysis
    analyze_image_task.delay(str(search.id), cloudinary_public_id)
    
    return SuccessResponse(
        data={"search_id": str(search.id), "status": "processing"},
        message="Image uploaded successfully. Analysis in progress."
    )


@router.get("/status/{search_id}", response_model=SuccessResponse)
def get_search_status(
    search_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the status of an image analysis search.
    
    Args:
        search_id: Search ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Search status and results if complete
        
    Raises:
        HTTPException: If search not found
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
    
    status_data = SearchStatusResponse(
        search_id=search.id,
        status=search.status,
        detected_category=search.detected_category,
        confidence_score=search.confidence_score,
        error_message=search.error_message
    )
    
    return SuccessResponse(data=status_data.model_dump())
