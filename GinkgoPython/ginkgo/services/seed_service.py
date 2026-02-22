import json

from ginkgo.core.config import settings
from ginkgo.models.base import InputLanguage, InputSource
from ginkgo.services.database_service import db_service
from ginkgo.utils.logger import get_logger

logger = get_logger(__name__)


def sync_seeds():
    """Syncs the seed.json file with the database.

    Removes database entries with source='seed' that are not in the JSON file.
    Adds entries from the JSON file that are not in the database.
    Does not update modified entries (as per user choice/constraints).
    """
    seed_file = settings.data_dir / "seed.json"
    if not seed_file.exists():
        logger.warning(f"Seed file not found at {seed_file}")
        return

    try:
        with open(seed_file, "r", encoding="utf-8") as f:
            seeds_data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding seed file: {e}")
        return

    # Get all existing seeds from all tables
    existing_thoughts = db_service.get_thoughts_by_source(InputSource.SEED)
    existing_prompts = db_service.get_prompts_by_source(InputSource.SEED)
    existing_decrees = db_service.get_decrees_by_source(InputSource.SEED)

    # Build a mapping of (text, lang, type) -> id for all existing seeds
    db_seed_keys = {}
    for s in existing_thoughts:
        key = (s.text, s.lang, "thought")
        db_seed_keys[key] = ("thought", s.id)
    for s in existing_prompts:
        key = (s.text, s.lang, "prompt")
        db_seed_keys[key] = ("prompt", s.id)
    for s in existing_decrees:
        key = (s.text, s.lang, "decree")
        db_seed_keys[key] = ("decree", s.id)

    # Build a set of all JSON seed keys
    json_seed_keys = set()
    to_add = []
    for s in seeds_data:
        key = (s["text"], s["lang"], s["type"])
        json_seed_keys.add(key)
        if key not in db_seed_keys:
            to_add.append(s)

    # Find IDs to remove (in database but not in JSON)
    to_remove = []
    for key, (record_type, record_id) in db_seed_keys.items():
        if key not in json_seed_keys:
            to_remove.append((record_type, record_id))

    logger.info(f"Syncing seeds: +{len(to_add)} / -{len(to_remove)}")

    # Add new seeds to appropriate tables
    for s in to_add:
        seed_type = s["type"]
        lang = InputLanguage(s["lang"])

        if seed_type == "thought":
            db_service.add_thought(
                text=s["text"],
                lang=lang,
                source=InputSource.SEED,
            )
        elif seed_type == "prompt":
            db_service.add_prompt(
                text=s["text"],
                lang=lang,
                source=InputSource.SEED,
            )
        elif seed_type == "decree":
            db_service.add_decree(
                text=s["text"],
                lang=lang,
                source=InputSource.SEED,
            )

    # Remove old seeds from appropriate tables
    for record_type, record_id in to_remove:
        if record_type == "thought":
            db_service.delete_thought(record_id)
        elif record_type == "prompt":
            db_service.delete_prompt(record_id)
        elif record_type == "decree":
            db_service.delete_decree(record_id)
