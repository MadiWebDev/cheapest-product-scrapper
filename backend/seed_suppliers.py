"""Seed script to populate the database with sample suppliers."""
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Supplier

# Sample supplier data across 10 countries
SAMPLE_SUPPLIERS = [
    {
        "name": "Shenzhen Electronics Co.",
        "country_code": "CN",
        "categories": ["electronics", "consumer electronics", "components"],
        "min_order_qty": 100,
        "price_usd_per_unit": 2.50,
        "trust_score": 8.5,
        "verified": True,
        "website_url": "https://shenzhen-electronics.example.com",
        "contact_email": "sales@shenzhen-electronics.example.com",
        "description": "Leading manufacturer of consumer electronics and electronic components."
    },
    {
        "name": "Bangladesh Textiles Ltd.",
        "country_code": "BD",
        "categories": ["textiles", "garments", "apparel"],
        "min_order_qty": 500,
        "price_usd_per_unit": 1.20,
        "trust_score": 7.8,
        "verified": True,
        "website_url": "https://bd-textiles.example.com",
        "contact_email": "info@bd-textiles.example.com",
        "description": "Premium textile manufacturer specializing in garments and apparel."
    },
    {
        "name": "Vietnam Furniture Works",
        "country_code": "VN",
        "categories": ["furniture", "home goods", "woodwork"],
        "min_order_qty": 50,
        "price_usd_per_unit": 45.00,
        "trust_score": 8.2,
        "verified": True,
        "website_url": "https://vietnam-furniture.example.com",
        "contact_email": "export@vietnam-furniture.example.com",
        "description": "Handcrafted furniture manufacturer with modern designs."
    },
    {
        "name": "India Pharma Solutions",
        "country_code": "IN",
        "categories": ["pharmaceuticals", "healthcare", "supplements"],
        "min_order_qty": 1000,
        "price_usd_per_unit": 0.80,
        "trust_score": 9.0,
        "verified": True,
        "website_url": "https://india-pharma.example.com",
        "contact_email": "orders@india-pharma.example.com",
        "description": "WHO-GMP certified pharmaceutical manufacturer."
    },
    {
        "name": "Turkish Ceramics Export",
        "country_code": "TR",
        "categories": ["ceramics", "home decor", "tiles"],
        "min_order_qty": 200,
        "price_usd_per_unit": 8.50,
        "trust_score": 7.5,
        "verified": False,
        "website_url": "https://turkish-ceramics.example.com",
        "contact_email": "sales@turkish-ceramics.example.com",
        "description": "Traditional and modern ceramic tiles and home decor."
    },
    {
        "name": "Brazil Agri Products",
        "country_code": "BR",
        "categories": ["agriculture", "food", "coffee"],
        "min_order_qty": 1000,
        "price_usd_per_unit": 3.20,
        "trust_score": 8.8,
        "verified": True,
        "website_url": "https://brazil-agri.example.com",
        "contact_email": "export@brazil-agri.example.com",
        "description": "Premium coffee and agricultural products exporter."
    },
    {
        "name": "Mexico Auto Parts Inc.",
        "country_code": "MX",
        "categories": ["automotive", "parts", "manufacturing"],
        "min_order_qty": 500,
        "price_usd_per_unit": 15.00,
        "trust_score": 7.2,
        "verified": True,
        "website_url": "https://mexico-autoparts.example.com",
        "contact_email": "orders@mexico-autoparts.example.com",
        "description": "Automotive parts manufacturer serving North America."
    },
    {
        "name": "Germany Precision Tools",
        "country_code": "DE",
        "categories": ["tools", "industrial", "machinery"],
        "min_order_qty": 100,
        "price_usd_per_unit": 85.00,
        "trust_score": 9.5,
        "verified": True,
        "website_url": "https://germany-tools.example.com",
        "contact_email": "sales@germany-tools.example.com",
        "description": "High-precision industrial tools and machinery."
    },
    {
        "name": "Indonesia Handicrafts Co.",
        "country_code": "ID",
        "categories": ["handicrafts", "arts", "decor"],
        "min_order_qty": 50,
        "price_usd_per_unit": 12.00,
        "trust_score": 7.0,
        "verified": False,
        "website_url": "https://indonesia-handicrafts.example.com",
        "contact_email": "info@indonesia-handicrafts.example.com",
        "description": "Traditional handicrafts and artisanal products."
    },
    {
        "name": "Pakistan Sports Goods",
        "country_code": "PK",
        "categories": ["sports", "equipment", "leather"],
        "min_order_qty": 200,
        "price_usd_per_unit": 5.50,
        "trust_score": 8.0,
        "verified": True,
        "website_url": "https://pakistan-sports.example.com",
        "contact_email": "export@pakistan-sports.example.com",
        "description": "Manufacturer of sports equipment and leather goods."
    },
    {
        "name": "Thailand Plastics Ltd.",
        "country_code": "TH",
        "categories": ["plastics", "packaging", "manufacturing"],
        "min_order_qty": 1000,
        "price_usd_per_unit": 0.50,
        "trust_score": 7.6,
        "verified": True,
        "website_url": "https://thailand-plastics.example.com",
        "contact_email": "sales@thailand-plastics.example.com",
        "description": "Plastic packaging and manufacturing solutions."
    },
    {
        "name": "Poland Furniture Export",
        "country_code": "PL",
        "categories": ["furniture", "wood", "office"],
        "min_order_qty": 30,
        "price_usd_per_unit": 55.00,
        "trust_score": 8.3,
        "verified": True,
        "website_url": "https://poland-furniture.example.com",
        "contact_email": "orders@poland-furniture.example.com",
        "description": "European-style office and home furniture."
    },
    {
        "name": "South Korea Electronics",
        "country_code": "KR",
        "categories": ["electronics", "semiconductors", "components"],
        "min_order_qty": 500,
        "price_usd_per_unit": 12.00,
        "trust_score": 9.2,
        "verified": True,
        "website_url": "https://korea-electronics.example.com",
        "contact_email": "global@korea-electronics.example.com",
        "description": "Advanced electronics and semiconductor components."
    },
    {
        "name": "Italy Leather Works",
        "country_code": "IT",
        "categories": ["leather", "fashion", "accessories"],
        "min_order_qty": 100,
        "price_usd_per_unit": 35.00,
        "trust_score": 9.0,
        "verified": True,
        "website_url": "https://italy-leather.example.com",
        "contact_email": "export@italy-leather.example.com",
        "description": "Premium leather goods and fashion accessories."
    },
    {
        "name": "Kenya Coffee Exporters",
        "country_code": "KE",
        "categories": ["coffee", "agriculture", "food"],
        "min_order_qty": 500,
        "price_usd_per_unit": 4.50,
        "trust_score": 7.4,
        "verified": False,
        "website_url": "https://kenya-coffee.example.com",
        "contact_email": "sales@kenya-coffee.example.com",
        "description": "Premium Arabica coffee beans from East Africa."
    },
    {
        "name": "Egypt Textile Mills",
        "country_code": "EG",
        "categories": ["textiles", "cotton", "fabrics"],
        "min_order_qty": 1000,
        "price_usd_per_unit": 2.00,
        "trust_score": 7.1,
        "verified": True,
        "website_url": "https://egypt-textiles.example.com",
        "contact_email": "export@egypt-textiles.example.com",
        "description": "Egyptian cotton textile manufacturer."
    },
    {
        "name": "Philippines Electronics Mfg",
        "country_code": "PH",
        "categories": ["electronics", "assembly", "components"],
        "min_order_qty": 200,
        "price_usd_per_unit": 3.50,
        "trust_score": 7.9,
        "verified": True,
        "website_url": "https://ph-electronics.example.com",
        "contact_email": "ordelectronics.example.com",
        "description": "Electronics manufacturing and assembly services."
    },
    {
        "name": "Argentina Beef Export",
        "country_code": "AR",
        "categories": ["food", "meat", "agriculture"],
        "min_order_qty": 1000,
        "price_usd_per_unit": 8.00,
        "trust_score": 8.1,
        "verified": True,
        "website_url": "https://argentina-beef.example.com",
        "contact_email": "export@argentina-beef.example.com",
        "description": "Premium beef and meat products exporter."
    },
    {
        "name": "Nigeria Oil & Gas Supplies",
        "country_code": "NG",
        "categories": ["oil", "gas", "industrial"],
        "min_order_qty": 500,
        "price_usd_per_unit": 25.00,
        "trust_score": 6.8,
        "verified": False,
        "website_url": "https://nigeria-oil.example.com",
        "contact_email": "sales@nigeria-oil.example.com",
        "description": "Oil and gas industrial supplies and equipment."
    },
    {
        "name": "Malaysia Electronics Hub",
        "country_code": "MY",
        "categories": ["electronics", "semiconductors", "assembly"],
        "min_order_qty": 300,
        "price_usd_per_unit": 5.00,
        "trust_score": 8.4,
        "verified": True,
        "website_url": "https://malaysia-electronics.example.com",
        "contact_email": "global@malaysia-electronics.example.com",
        "description": "Electronics manufacturing and semiconductor assembly."
    },
    {
        "name": "Colombia Coffee Beans",
        "country_code": "CO",
        "categories": ["coffee", "agriculture", "food"],
        "min_order_qty": 500,
        "price_usd_per_unit": 4.00,
        "trust_score": 7.7,
        "verified": True,
        "website_url": "https://colombia-coffee.example.com",
        "contact_email": "export@colombia-coffee.example.com",
        "description": "Premium Colombian coffee beans exporter."
    },
    {
        "name": "Ukraine Steel Works",
        "country_code": "UA",
        "categories": ["steel", "metal", "industrial"],
        "min_order_qty": 1000,
        "price_usd_per_unit": 18.00,
        "trust_score": 7.3,
        "verified": True,
        "website_url": "https://ukraine-steel.example.com",
        "contact_email": "sales@ukraine-steel.example.com",
        "description": "Steel and metal products manufacturer."
    },
    {
        "name": "South Africa Mining Supplies",
        "country_code": "ZA",
        "categories": ["mining", "industrial", "equipment"],
        "min_order_qty": 100,
        "price_usd_per_unit": 30.00,
        "trust_score": 7.5,
        "verified": True,
        "website_url": "https://sa-mining.example.com",
        "contact_email": "export@sa-mining.example.com",
        "description": "Mining equipment and industrial supplies."
    },
    {
        "name": "Singapore Electronics Trading",
        "country_code": "SG",
        "categories": ["electronics", "trading", "components"],
        "min_order_qty": 50,
        "price_usd_per_unit": 8.00,
        "trust_score": 9.1,
        "verified": True,
        "website_url": "https://singapore-electronics.example.com",
        "contact_email": "sales@singapore-electronics.example.com",
        "description": "Electronics components trading and distribution."
    },
    {
        "name": "Netherlands AgriTech",
        "country_code": "NL",
        "categories": ["agriculture", "technology", "equipment"],
        "min_order_qty": 20,
        "price_usd_per_unit": 150.00,
        "trust_score": 9.3,
        "verified": True,
        "website_url": "https://netherlands-agritech.example.com",
        "contact_email": "info@netherlands-agritech.example.com",
        "description": "Agricultural technology and equipment."
    },
    {
        "name": "Vietnam Garment Factory",
        "country_code": "VN",
        "categories": ["garments", "textiles", "apparel"],
        "min_order_qty": 300,
        "price_usd_per_unit": 3.00,
        "trust_score": 7.9,
        "verified": True,
        "website_url": "https://vietnam-garments.example.com",
        "contact_email": "orders@vietnam-garments.example.com",
        "description": "Garment manufacturing and textile production."
    },
    {
        "name": "China Machinery Corp",
        "country_code": "CN",
        "categories": ["machinery", "industrial", "manufacturing"],
        "min_order_qty": 10,
        "price_usd_per_unit": 500.00,
        "trust_score": 8.0,
        "verified": True,
        "website_url": "https://china-machinery.example.com",
        "contact_email": "export@china-machinery.example.com",
        "description": "Industrial machinery and equipment manufacturer."
    },
    {
        "name": "Bangladesh Jute Products",
        "country_code": "BD",
        "categories": ["jute", "textiles", "eco-friendly"],
        "min_order_qty": 500,
        "price_usd_per_unit": 1.50,
        "trust_score": 7.2,
        "verified": True,
        "website_url": "https://bd-jute.example.com",
        "contact_email": "sales@bd-jute.example.com",
        "description": "Eco-friendly jute products and textiles."
    },
    {
        "name": "India Software Solutions",
        "country_code": "IN",
        "categories": ["software", "technology", "services"],
        "min_order_qty": 1,
        "price_usd_per_unit": 25.00,
        "trust_score": 8.7,
        "verified": True,
        "website_url": "https://india-software.example.com",
        "contact_email": "contact@india-software.example.com",
        "description": "Software development and IT services."
    },
    {
        "name": "Turkey Marble Export",
        "country_code": "TR",
        "categories": ["marble", "stone", "construction"],
        "min_order_qty": 100,
        "price_usd_per_unit": 45.00,
        "trust_score": 7.6,
        "verified": True,
        "website_url": "https://turkey-marble.example.com",
        "contact_email": "export@turkey-marble.example.com",
        "description": "Natural marble and stone products."
    },
    {
        "name": "Brazil Sugar Export",
        "country_code": "BR",
        "categories": ["sugar", "agriculture", "food"],
        "min_order_qty": 2000,
        "price_usd_per_unit": 0.40,
        "trust_score": 8.2,
        "verified": True,
        "website_url": "https://brazil-sugar.example.com",
        "contact_email": "sales@brazil-sugar.example.com",
        "description": "Sugar and agricultural products exporter."
    },
    {
        "name": "Mexico Avocado Export",
        "country_code": "MX",
        "categories": ["avocado", "agriculture", "food"],
        "min_order_qty": 500,
        "price_usd_per_unit": 2.50,
        "trust_score": 8.5,
        "verified": True,
        "website_url": "https://mexico-avocado.example.com",
        "contact_email": "export@mexico-avocado.example.com",
        "description": "Premium avocado exporter."
    },
    {
        "name": "Germany Chemical Works",
        "country_code": "DE",
        "categories": ["chemicals", "industrial", "manufacturing"],
        "min_order_qty": 500,
        "price_usd_per_unit": 15.00,
        "trust_score": 9.4,
        "verified": True,
        "website_url": "https://germany-chemicals.example.com",
        "contact_email": "sales@germany-chemicals.example.com",
        "description": "Industrial chemicals and specialty products."
    },
    {
        "name": "Indonesia Palm Oil",
        "country_code": "ID",
        "categories": ["palm oil", "agriculture", "food"],
        "min_order_qty": 1000,
        "price_usd_per_unit": 0.80,
        "trust_score": 7.3,
        "verified": True,
        "website_url": "https://indonesia-palmoil.example.com",
        "contact_email": "export@indonesia-palmoil.example.com",
        "description": "Palm oil and agricultural products."
    },
    {
        "name": "Pakistan Textile Mills",
        "country_code": "PK",
        "categories": ["textiles", "cotton", "fabrics"],
        "min_order_qty": 1000,
        "price_usd_per_unit": 1.80,
        "trust_score": 7.8,
        "verified": True,
        "website_url": "https://pakistan-textiles.example.com",
        "contact_email": "sales@pakistan-textiles.example.com",
        "description": "Cotton textile and fabric manufacturer."
    },
    {
        "name": "Thailand Rubber Products",
        "country_code": "TH",
        "categories": ["rubber", "industrial", "automotive"],
        "min_order_qty": 500,
        "price_usd_per_unit": 4.00,
        "trust_score": 7.7,
        "verified": True,
        "website_url": "https://thailand-rubber.example.com",
        "contact_email": "export@thailand-rubber.example.com",
        "description": "Rubber products and automotive components."
    },
    {
        "name": "Poland Food Processing",
        "country_code": "PL",
        "categories": ["food", "processing", "manufacturing"],
        "min_order_qty": 200,
        "price_usd_per_unit": 6.00,
        "trust_score": 8.1,
        "verified": True,
        "website_url": "https://poland-food.example.com",
        "contact_email": "orders@poland-food.example.com",
        "description": "Food processing and manufacturing equipment."
    },
    {
        "name": "South Korea Shipbuilding",
        "country_code": "KR",
        "categories": ["shipbuilding", "marine", "industrial"],
        "min_order_qty": 1,
        "price_usd_per_unit": 50000.00,
        "trust_score": 9.3,
        "verified": True,
        "website_url": "https://korea-shipbuilding.example.com",
        "contact_email": "sales@korea-shipbuilding.example.com",
        "description": "Shipbuilding and marine engineering."
    },
    {
        "name": "Italy Food Export",
        "country_code": "IT",
        "categories": ["food", "gourmet", "olive oil"],
        "min_order_qty": 100,
        "price_usd_per_unit": 12.00,
        "trust_score": 9.1,
        "verified": True,
        "website_url": "https://italy-food.example.com",
        "contact_email": "export@italy-food.example.com",
        "description": "Italian gourmet food and olive oil exporter."
    },
    {
        "name": "Kenya Tea Exporters",
        "country_code": "KE",
        "categories": ["tea", "agriculture", "food"],
        "min_order_qty": 500,
        "price_usd_per_unit": 3.00,
        "trust_score": 7.5,
        "verified": True,
        "website_url": "https://kenya-tea.example.com",
        "contact_email": "sales@kenya-tea.example.com",
        "description": "Premium tea leaves and agricultural products."
    },
    {
        "name": "Egypt Marble & Stone",
        "country_code": "EG",
        "categories": ["marble", "stone", "construction"],
        "min_order_qty": 200,
        "price_usd_per_unit": 35.00,
        "trust_score": 7.0,
        "verified": False,
        "website_url": "https://egypt-marble.example.com",
        "contact_email": "export@egypt-marble.example.com",
        "description": "Egyptian marble and natural stone products."
    },
    {
        "name": "Philippines Coconut Products",
        "country_code": "PH",
        "categories": ["coconut", "agriculture", "food"],
        "min_order_qty": 300,
        "price_usd_per_unit": 2.00,
        "trust_score": 7.6,
        "verified": True,
        "website_url": "https://ph-coconut.example.com",
        "contact_email": "export@ph-coconut.example.com",
        "description": "Coconut products and agricultural goods."
    },
    {
        "name": "Argentina Wine Export",
        "country_code": "AR",
        "categories": ["wine", "beverages", "agriculture"],
        "min_order_qty": 100,
        "price_usd_per_unit": 10.00,
        "trust_score": 8.6,
        "verified": True,
        "website_url": "https://argentina-wine.example.com",
        "contact_email": "expentina-wine.example.com",
        "description": "Argentine wine and beverages exporter."
    },
    {
        "name": "Nigeria Cocoa Export",
        "country_code": "NG",
        "categories": ["cocoa", "agriculture", "food"],
        "min_order_qty": 500,
        "price_usd_per_unit": 2.50,
        "trust_score": 7.0,
        "verified": False,
        "website_url": "https://nigeria-cocoa.example.com",
        "contact_email": "sales@nigeria-cocoa.example.com",
        "description": "Cocoa beans and agricultural products."
    },
    {
        "name": "Malaysia Palm Products",
        "country_code": "MY",
        "categories": ["palm", "agriculture", "food"],
        "min_order_qty": 800,
        "price_usd_per_unit": 1.20,
        "trust_score": 8.0,
        "verified": True,
        "website_url": "https://malaysia-palm.example.com",
        "contact_email": "export@malaysia-palm.example.com",
        "description": "Palm oil and agricultural products."
    },
    {
        "name": "Colombia Flowers Export",
        "country_code": "CO",
        "categories": ["flowers", "agriculture", "decor"],
        "min_order_qty": 200,
        "price_usd_per_unit": 5.00,
        "trust_score": 7.8,
        "verified": True,
        "website_url": "https://colombia-flowers.example.com",
        "contact_email": "export@colombia-flowers.example.com",
        "description": "Fresh flowers and agricultural products."
    },
    {
        "name": "Ukraine Grain Export",
        "country_code": "UA",
        "categories": ["grain", "agriculture", "food"],
        "min_order_qty": 1000,
        "price_usd_per_unit": 0.30,
        "trust_score": 7.4,
        "verified": True,
        "website_url": "https://ukraine-grain.example.com",
        "contact_email": "export@ukraine-grain.example.com",
        "description": "Grain and agricultural products exporter."
    },
    {
        "name": "South Africa Wine Export",
        "country_code": "ZA",
        "categories": ["wine", "beverages", "agriculture"],
        "min_order_qty": 150,
        "price_usd_per_unit": 8.00,
        "trust_score": 8.3,
        "verified": True,
        "website_url": "https://sa-wine.example.com",
        "contact_email": "export@sa-wine.example.com",
        "description": "South African wine and beverages exporter."
    },
    {
        "name": "Singapore Trading Co.",
        "country_code": "SG",
        "categories": ["trading", "commodities", "general"],
        "min_order_qty": 50,
        "price_usd_per_unit": 20.00,
        "trust_score": 9.0,
        "verified": True,
        "website_url": "https://singapore-trading.example.com",
        "contact_email": "sales@singapore-trading.example.com",
        "description": "General trading and commodities distributor."
    },
]


def seed_suppliers():
    """Seed the database with sample suppliers."""
    db: Session = SessionLocal()
    
    try:
        # Clear existing suppliers
        db.query(Supplier).delete()
        db.commit()
        
        # Add sample suppliers
        for supplier_data in SAMPLE_SUPPLIERS:
            supplier = Supplier(**supplier_data)
            db.add(supplier)
        
        db.commit()
        print(f"Successfully seeded {len(SAMPLE_SUPPLIERS)} suppliers")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding suppliers: {str(e)}")
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    seed_suppliers()
