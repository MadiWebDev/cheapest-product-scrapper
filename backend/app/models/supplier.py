"""Supplier model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID, VECTOR
from app.database import Base


class Supplier(Base):
    """Supplier model for product sourcing."""
    
    __tablename__ = "suppliers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False, index=True)
    country_code = Column(String(2), nullable=False, index=True)  # ISO 3166-1 alpha-2
    categories = Column(ARRAY(String), nullable=False)
    min_order_qty = Column(Integer, nullable=False)
    price_usd_per_unit = Column(Float, nullable=False)
    trust_score = Column(Float, nullable=False)  # 0-10
    verified = Column(Boolean, default=False, nullable=False)
    website_url = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    embedding = Column(VECTOR(1536), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Supplier(id={self.id}, name={self.name}, country={self.country_code})>"
