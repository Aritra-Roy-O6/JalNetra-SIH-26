"""Insert development data into the JalNetra database."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Alert, engine, initialize_database


MOCK_ALERT = {
    "type": "cyclone",
    "zone_geom": {
        "type": "Polygon",
        "coordinates": [
            [[88.0, 21.0], [89.0, 21.0], [88.5, 22.0], [88.0, 21.0]]
        ],
    },
}


def seed_mock_data() -> None:
    """Initialize the schema and add the mock cyclone alert once."""
    initialize_database()
    with Session(engine) as session:
        existing_alert = session.scalar(
            select(Alert).where(Alert.type == MOCK_ALERT["type"])
        )
        if existing_alert is None:
            session.add(Alert(**MOCK_ALERT))
            session.commit()

    print("Mock database data seeded successfully.")


if __name__ == "__main__":
    seed_mock_data()