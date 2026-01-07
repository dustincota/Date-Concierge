"""
Seed data for venues (NYC restaurants).
"""

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.venue import Venue

NYC_VENUES = [
    {
        "name": "Celestine",
        "address": "1 John St, Brooklyn, NY 11201",
        "neighborhood": "DUMBO",
        "city": "New York",
        "latitude": 40.7033,
        "longitude": -73.9893,
        "category": "restaurant",
        "cuisines": ["Mediterranean", "Seafood"],
        "price_level": 3,
        "rating": 4.6,
        "phone": "(718) 596-0505",
        "website": "https://celestinebk.com",
    },
    {
        "name": "Lilia",
        "address": "567 Union Ave, Brooklyn, NY 11211",
        "neighborhood": "Williamsburg",
        "city": "New York",
        "latitude": 40.7089,
        "longitude": -73.9502,
        "category": "restaurant",
        "cuisines": ["Italian"],
        "price_level": 3,
        "rating": 4.7,
        "resy_slug": "lilia",
        "phone": "(718) 576-3095",
    },
    {
        "name": "Carbone",
        "address": "181 Thompson St, New York, NY 10012",
        "neighborhood": "Greenwich Village",
        "city": "New York",
        "latitude": 40.7279,
        "longitude": -74.0018,
        "category": "restaurant",
        "cuisines": ["Italian"],
        "price_level": 4,
        "rating": 4.5,
        "resy_slug": "carbone-new-york",
        "phone": "(212) 254-3000",
    },
    {
        "name": "Di Fara Pizza",
        "address": "1424 Avenue J, Brooklyn, NY 11230",
        "neighborhood": "Midwood",
        "city": "New York",
        "latitude": 40.6253,
        "longitude": -73.9612,
        "category": "restaurant",
        "cuisines": ["Pizza", "Italian"],
        "price_level": 2,
        "rating": 4.4,
        "phone": "(718) 258-1367",
    },
    {
        "name": "Peter Luger Steak House",
        "address": "178 Broadway, Brooklyn, NY 11211",
        "neighborhood": "Williamsburg",
        "city": "New York",
        "latitude": 40.7096,
        "longitude": -73.9626,
        "category": "restaurant",
        "cuisines": ["Steakhouse", "American"],
        "price_level": 4,
        "rating": 4.3,
        "phone": "(718) 387-7400",
        "website": "https://peterluger.com",
    },
    {
        "name": "Lucali",
        "address": "575 Henry St, Brooklyn, NY 11231",
        "neighborhood": "Carroll Gardens",
        "city": "New York",
        "latitude": 40.6769,
        "longitude": -74.0018,
        "category": "restaurant",
        "cuisines": ["Pizza", "Italian"],
        "price_level": 2,
        "rating": 4.6,
        "phone": "(718) 858-4086",
    },
    {
        "name": "Marea",
        "address": "240 Central Park S, New York, NY 10019",
        "neighborhood": "Midtown",
        "city": "New York",
        "latitude": 40.7672,
        "longitude": -73.9807,
        "category": "restaurant",
        "cuisines": ["Italian", "Seafood"],
        "price_level": 4,
        "rating": 4.5,
        "resy_slug": "marea-new-york",
        "phone": "(212) 582-5100",
    },
    {
        "name": "The River Café",
        "address": "1 Water St, Brooklyn, NY 11201",
        "neighborhood": "DUMBO",
        "city": "New York",
        "latitude": 40.7037,
        "longitude": -73.9937,
        "category": "restaurant",
        "cuisines": ["American", "Fine Dining"],
        "price_level": 4,
        "rating": 4.4,
        "opentable_id": "the-river-cafe",
        "phone": "(718) 522-5200",
        "website": "https://therivercafe.com",
    },
    {
        "name": "Roberta's Pizza",
        "address": "261 Moore St, Brooklyn, NY 11206",
        "neighborhood": "Bushwick",
        "city": "New York",
        "latitude": 40.7058,
        "longitude": -73.9334,
        "category": "restaurant",
        "cuisines": ["Pizza", "Italian"],
        "price_level": 2,
        "rating": 4.3,
        "phone": "(718) 417-1118",
        "website": "https://robertaspizza.com",
    },
    {
        "name": "Olmsted",
        "address": "659 Vanderbilt Ave, Brooklyn, NY 11238",
        "neighborhood": "Prospect Heights",
        "city": "New York",
        "latitude": 40.6821,
        "longitude": -73.9686,
        "category": "restaurant",
        "cuisines": ["American", "Contemporary"],
        "price_level": 3,
        "rating": 4.5,
        "resy_slug": "olmsted",
        "phone": "(718) 552-2610",
    },
    {
        "name": "Okonomi",
        "address": "150 Ainslie St, Brooklyn, NY 11211",
        "neighborhood": "Williamsburg",
        "city": "New York",
        "latitude": 40.7177,
        "longitude": -73.9525,
        "category": "restaurant",
        "cuisines": ["Japanese"],
        "price_level": 2,
        "rating": 4.6,
        "phone": "(718) 302-2228",
    },
    {
        "name": "Kissaki",
        "address": "122 Smith St, Brooklyn, NY 11201",
        "neighborhood": "Cobble Hill",
        "city": "New York",
        "latitude": 40.6885,
        "longitude": -73.9905,
        "category": "restaurant",
        "cuisines": ["Japanese", "Sushi"],
        "price_level": 3,
        "rating": 4.5,
        "resy_slug": "kissaki-brooklyn",
        "phone": "(347) 689-4609",
    },
    {
        "name": "Llama Inn",
        "address": "50 Withers St, Brooklyn, NY 11211",
        "neighborhood": "Williamsburg",
        "city": "New York",
        "latitude": 40.7156,
        "longitude": -73.9502,
        "category": "restaurant",
        "cuisines": ["Peruvian", "Latin American"],
        "price_level": 3,
        "rating": 4.4,
        "resy_slug": "llama-inn",
        "phone": "(718) 387-3434",
    },
    {
        "name": "Hometown Bar-B-Que",
        "address": "454 Van Brunt St, Brooklyn, NY 11231",
        "neighborhood": "Red Hook",
        "city": "New York",
        "latitude": 40.6762,
        "longitude": -74.0106,
        "category": "restaurant",
        "cuisines": ["BBQ", "American"],
        "price_level": 2,
        "rating": 4.5,
        "phone": "(347) 294-4644",
        "website": "https://hometownbarbque.com",
    },
    {
        "name": "Frankie's 457 Spuntino",
        "address": "457 Court St, Brooklyn, NY 11231",
        "neighborhood": "Carroll Gardens",
        "city": "New York",
        "latitude": 40.6769,
        "longitude": -74.0006,
        "category": "restaurant",
        "cuisines": ["Italian"],
        "price_level": 2,
        "rating": 4.3,
        "phone": "(718) 403-0033",
    },
]


def seed_venues(db: Session):
    """Seed the database with NYC venue data."""
    print("Seeding venues...")

    for venue_data in NYC_VENUES:
        # Check if venue already exists
        existing = db.query(Venue).filter(
            Venue.name == venue_data["name"],
            Venue.neighborhood == venue_data["neighborhood"]
        ).first()

        if existing:
            print(f"  - {venue_data['name']} already exists, skipping")
            continue

        venue = Venue(**venue_data)
        db.add(venue)
        print(f"  + Added {venue_data['name']}")

    db.commit()
    print(f"Seeded {len(NYC_VENUES)} venues!")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_venues(db)
    finally:
        db.close()
