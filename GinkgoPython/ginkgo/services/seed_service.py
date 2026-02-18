import json

from ginkgo.core.config import settings
from ginkgo.schemas.frontend import InputSource
from ginkgo.services.database_service import db_service


def sync_seeds():
    """Syncs the seed.json file with the database.

    Removes database entries with source='seed' that are not in the JSON file.
    Adds entries from the JSON file that are not in the database.
    Does not update modified entries (as per user choice/constraints).
    """
    seed_file = settings.data_dir / "seed.json"
    if not seed_file.exists():
        print(f"Seed file not found at {seed_file}")
        return

    try:
        with open(seed_file, "r", encoding="utf-8") as f:
            seeds_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding seed file: {e}")
        return

    existing_seeds = db_service.get_by_source(InputSource.SEED)

    json_seed_keys = {(s["text"], s["lang"], s["type"]) for s in seeds_data}

    db_seed_keys = {(s.text, s.lang, s.type): s.id for s in existing_seeds}

    to_add = []
    for s in seeds_data:
        key = (s["text"], s["lang"], s["type"])
        if key not in db_seed_keys:
            to_add.append(s)

    to_remove_ids = []
    for key, record_id in db_seed_keys.items():
        if key not in json_seed_keys:
            to_remove_ids.append(record_id)

    print(f"Syncing seeds: +{len(to_add)} / -{len(to_remove_ids)}")

    for s in to_add:
        db_service.add_input(
            text=s["text"],
            input_type=s["type"],
            lang=s["lang"],
            source=InputSource.SEED,
        )

    for record_id in to_remove_ids:
        db_service.delete(record_id)
