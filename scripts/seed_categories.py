from app.core.database import SessionLocal
from app.modules.categories.models import Category


DEFAULT_CATEGORIES = [
    "Breakfast",
    "Lunch",
    "Dinner",
    "Dessert",
    "Snack",
    "Beverage",
    "Indonesian",
    "Asian",
    "Western",
    "Vegetarian",
    "Vegan",
    "Seafood",
    "Chicken",
    "Beef",
    "Soup",
    "Noodles",
    "Rice",
    "Cake"
]


def run():
    db = SessionLocal()

    try:
        existing_names = {
            c.name
            for c in db.query(Category).all()
        }

        new_categories = [
            Category(name=name)
            for name in DEFAULT_CATEGORIES
            if name not in existing_names
        ]

        if new_categories:
            db.add_all(new_categories)
            db.commit()
            print(f"Inserted {len(new_categories)} categories.")
        else:
            print("No new categories to insert.")

    finally:
        db.close()


if __name__ == "__main__":
    run()