"""Search model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.database import Base


class Search(Base):
    """Search model for product image analysis and supplier matching."""
    
    __tablename__ = "searches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    image_s3_key = Column(String, nullable=False)
    image_expires_at = Column(DateTime, nullable=False)
    detected_category = Column(String, nullable=True)
    detected_attributes = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    filters_applied = Column(JSON, nullable=True)
    result_supplier_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    status = Column(String, default="processing", nullable=False)  # processing, complete, failed, needs_clarification
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Search(id={self.id}, user_id={self.user_id}, status={self.status})>"
