import uuid
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, JSON, Text, UniqueConstraint, Numeric
MONEY=Numeric(19,4)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
def uid(): return Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
class Product(Base):
    __tablename__="products"; id=uid(); title=Column(String, nullable=False); brand=Column(String, index=True)
    model=Column(String, index=True); gtin=Column(String, index=True); asin=Column(String, index=True); mpn=Column(String, index=True)
    category=Column(String, index=True); attributes=Column(JSON, default=dict); image=Column(String); created_at=Column(DateTime(timezone=True), server_default=func.now())
class Seller(Base):
    __tablename__="sellers"; id=uid(); connector=Column(String, index=True); name=Column(String); rating=Column(Float)
    feedback_count=Column(Integer, default=0); age_years=Column(Float, default=0); official_store=Column(Boolean, default=False); return_rate=Column(Float)
class Offer(Base):
    __tablename__="offers"; id=uid(); product_id=Column(UUID(as_uuid=True), ForeignKey("products.id"), index=True)
    seller_id=Column(UUID(as_uuid=True), ForeignKey("sellers.id")); connector=Column(String, index=True); title=Column(String)
    url=Column(Text); price=Column(MONEY); currency=Column(String, default="USD"); shipping_price=Column(MONEY)
    availability=Column(String, default="unknown"); stock_qty=Column(Integer); delivery_days=Column(Integer)
    rating=Column(Float); review_count=Column(Integer, default=0); condition=Column(String, default="new")
    quality_score=Column(Float); last_verified_at=Column(DateTime(timezone=True), server_default=func.now()); raw=Column(JSON, default=dict)
class PriceHistory(Base):
    __tablename__="price_history"; id=uid(); product_id=Column(UUID(as_uuid=True), ForeignKey("products.id"), index=True)
    connector=Column(String, index=True); country=Column(String, index=True); price=Column(MONEY); currency=Column(String)
    landed_total=Column(MONEY); recorded_at=Column(DateTime(timezone=True), server_default=func.now(), index=True)
class WatchlistItem(Base):
    __tablename__="watchlist_items"; id=uid(); user_id=Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    product_id=Column(UUID(as_uuid=True), ForeignKey("products.id")); target_price=Column(MONEY); currency=Column(String, default="USD"); created_at=Column(DateTime(timezone=True), server_default=func.now())
class Alert(Base):
    __tablename__="alerts"; id=uid(); user_id=Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    product_id=Column(UUID(as_uuid=True), ForeignKey("products.id")); kind=Column(String)  # price_drop|back_in_stock
    target_price=Column(MONEY); channel=Column(String, default="email")  # email|telegram|whatsapp|webpush
    destination=Column(String); active=Column(Boolean, default=True); last_fired_at=Column(DateTime(timezone=True))
class SavedSearch(Base):
    __tablename__="saved_searches"; id=uid(); user_id=Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    query=Column(String); filters=Column(JSON, default=dict); created_at=Column(DateTime(timezone=True), server_default=func.now())
class FxRate(Base):
    __tablename__="fx_rates"; id=uid(); base=Column(String, default="USD"); rates=Column(JSON); fetched_at=Column(DateTime(timezone=True), server_default=func.now()); stale=Column(Boolean, default=False)
class TaxRule(Base):
    __tablename__="tax_rules"; id=uid(); country=Column(String, index=True); kind=Column(String)  # vat|duty|de_minimis
    category=Column(String, default="default"); rate=Column(MONEY); version=Column(String); label=Column(String, default="estimate")
class ApiKey(Base):
    __tablename__="api_keys"; id=uid(); user_id=Column(UUID(as_uuid=True), ForeignKey("users.id"))
    key_hash=Column(String, unique=True, index=True); name=Column(String); active=Column(Boolean, default=True)
    usage_count=Column(Integer, default=0); created_at=Column(DateTime(timezone=True), server_default=func.now())
class ConnectorHealth(Base):
    __tablename__="connector_health"; id=uid(); connector=Column(String, unique=True, index=True); enabled=Column(Boolean, default=True)
    successes=Column(Integer, default=0); failures=Column(Integer, default=0); blocks=Column(Integer, default=0)
    avg_latency_ms=Column(Float, default=0); drift_suspected=Column(Boolean, default=False); last_error=Column(Text); updated_at=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
class MatchFeedback(Base):
    __tablename__="match_feedback"; id=uid(); product_title=Column(String); offer_url=Column(Text); reason=Column(Text); created_at=Column(DateTime(timezone=True), server_default=func.now())
