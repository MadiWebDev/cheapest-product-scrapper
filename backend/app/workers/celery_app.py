"""Celery application and image analysis task."""
import uuid
import json
import cloudinary
import cloudinary.api
from celery import Celery
from openai import OpenAI
from sqlalchemy.orm import Session
from app.config import settings
from app.database import SessionLocal
from app.models.search import Search
from app.models.supplier import Supplier
from app.services.matching import match_suppliers

# Initialize Celery
celery_app = Celery(
    "sourcelens",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour timeout
)

# Initialize OpenAI client
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)


def get_cloudinary_url(public_id: str) -> str:
    """
    Generate a URL for Cloudinary image.
    
    Args:
        public_id: Cloudinary public ID
        
    Returns:
        Image URL string
        
    Raises:
        Exception: If URL generation fails
    """
    try:
        url = cloudinary.CloudinaryImage(public_id).build_url()
        return url
    except Exception as e:
        raise Exception(f"Failed to generate Cloudinary URL: {str(e)}")


def analyze_image_with_gpt4o(image_url: str) -> dict:
    """
    Analyze product image using GPT-4o Vision.
    
    Args:
        image_url: Presigned URL to the image
        
    Returns:
        Dictionary with analysis results
        
    Raises:
        Exception: If analysis fails
    """
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Analyze this product image and return ONLY valid JSON with these fields: "
                                "category (string), subcategory (string), material (string), "
                                "color (string), estimated_size (string), style (string), "
                                "keywords (array of 5-8 strings), confidence (float 0-1). "
                                "No explanation, only JSON."
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        # Parse JSON from response
        analysis = json.loads(content)
        return analysis
    
    except Exception as e:
        raise Exception(f"Image analysis failed: {str(e)}")


def generate_embedding(text: str) -> list:
    """
    Generate text embedding using OpenAI text-embedding-3-small.
    
    Args:
        text: Text to embed
        
    Returns:
        List of 1536 floats representing the embedding
        
    Raises:
        Exception: If embedding generation fails
    """
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        raise Exception(f"Embedding generation failed: {str(e)}")


@celery_app.task(name="app.workers.celery_app.analyze_image_task")
def analyze_image_task(search_id: str, cloudinary_public_id: str):
    """
    Celery task to analyze uploaded product image and match suppliers.
    
    Steps:
    1. Get Cloudinary image URL
    2. Call GPT-4o Vision for analysis
    3. Check confidence threshold
    4. Generate text embedding
    5. Run supplier matching
    6. Update search record with results
    
    Args:
        search_id: Search ID
        cloudinary_public_id: Cloudinary public ID for the uploaded image
    """
    db: Session = SessionLocal()
    
    try:
        # Get search record
        search = db.query(Search).filter(Search.id == uuid.UUID(search_id)).first()
        if not search:
            raise Exception(f"Search {search_id} not found")
        
        # Step 1: Get Cloudinary image URL
        image_url = get_cloudinary_url(cloudinary_public_id)
        
        # Step 2: Call GPT-4o Vision
        analysis = analyze_image_with_gpt4o(image_url)
        
        # Step 3: Check confidence threshold
        confidence = analysis.get("confidence", 0)
        if confidence < settings.MIN_CONFIDENCE_THRESHOLD:
            search.status = "needs_clarification"
            search.confidence_score = confidence
            search.detected_category = analysis.get("category")
            search.detected_attributes = analysis
            db.commit()
            return
        
        # Step 4: Generate text embedding
        # Combine category and keywords for embedding
        category = analysis.get("category", "")
        keywords = " ".join(analysis.get("keywords", []))
        embedding_text = f"{category} {keywords}"
        embedding = generate_embedding(embedding_text)
        
        # Step 5: Run supplier matching
        filters = search.filters_applied or {}
        matched_suppliers = match_suppliers(search_id, filters, db)
        
        # Step 6: Update search record
        search.detected_category = analysis.get("category")
        search.detected_attributes = analysis
        search.confidence_score = confidence
        search.result_supplier_ids = [s.id for s in matched_suppliers]
        search.status = "complete"
        
        db.commit()
        
    except Exception as e:
        # Update search with error status
        search = db.query(Search).filter(Search.id == uuid.UUID(search_id)).first()
        if search:
            search.status = "failed"
            search.error_message = str(e)
            db.commit()
        raise
    
    finally:
        db.close()


@celery_app.task(name="app.workers.celery_app.reset_monthly_searches")
def reset_monthly_searches():
    """
    Celery beat task to reset monthly search counters on the 1st of each month.
    """
    db: Session = SessionLocal()
    
    try:
        from app.models.user import User
        from sqlalchemy import update
        
        # Reset all users' search counts
        db.execute(update(User).values(searches_this_month=0))
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise
    
    finally:
        db.close()
