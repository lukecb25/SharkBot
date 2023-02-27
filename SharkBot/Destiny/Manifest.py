import sqlite3
import json

from SharkBot import Errors

_MANIFEST_FOLDER = "data/live/bungie/manifest"
_CONTENT_FILE = _MANIFEST_FOLDER + "/manifest.content"

con = sqlite3.connect(_CONTENT_FILE)

def _execute(statement: str, fetch_all: bool = True):
    cur = con.cursor()
    if fetch_all:
        res = cur.execute(statement).fetchall()
    else:
        res = cur.execute(statement).fetchone()
    cur.close()
    return res

DEFINITION_TYPES = [r[0] for r in _execute("SELECT name FROM sqlite_master WHERE type='table';")]

_HASH_THRESHOLD = 2**31 - 1
_HASH_MODIFIER = 2**32

def _hash_to_id(hash_in: str | int) -> int:
    """
    Converts a given hash to an id for lookup in the manifest.content table by converting it to a 32-bit unsigned integer.

    :param hash_in: The Hash to convert
    :return: The ID for lookup in manifest.content
    """
    hash_in = int(hash_in)
    if hash_in > _HASH_THRESHOLD:
        return hash_in - _HASH_MODIFIER
    else:
        return hash_in

def _id_to_hash(id_in: int) -> int:
    """
    Converts a given id from manifest.content to a hash table by converting it to a 32-bit signed integer.

    :param id_in: The ID to convert from manifest.content
    :return: The resulting Hash
    """
    if id_in > 0:
        return id_in
    else:
        return id_in + _HASH_MODIFIER

def get_definition(definition_type: str, definition_hash: str | int) -> dict:
    if definition_type not in DEFINITION_TYPES:
        raise Errors.Manifest.DefinitionTypeDoesNotExistError(definition_type)
    definition_id = _hash_to_id(definition_hash)
    result = _execute(f"SELECT * FROM {definition_type} WHERE id={definition_id}", fetch_all=False)
    if result is None:
        raise Errors.Manifest.HashNotFoundError(definition_type, definition_hash, definition_id)
    else:
        return json.loads(result[1])

def get_all_definitions(definition_type: str) -> dict[str, dict]:
    if definition_type not in DEFINITION_TYPES:
        raise Errors.Manifest.DefinitionTypeDoesNotExistError(definition_type)
    result = _execute(f"SELECT * FROM {definition_type}", fetch_all=True)
    return {str(_id_to_hash(definition_id)): json.loads(definition) for definition_id, definition in result}

def get_definitions(definition_type: str, definition_hashes: list[str | int]) -> dict[str, dict]:
    if definition_type not in DEFINITION_TYPES:
        raise Errors.Manifest.DefinitionTypeDoesNotExistError(definition_type)
    raw_result = _execute(f"SELECT * FROM {definition_type} WHERE id IN ({', '.join(str(_hash_to_id(h)) for h in definition_hashes)})", fetch_all=True)
    result = {str(_id_to_hash(definition_id)): json.loads(definition) for definition_id, definition in raw_result}
    if all([str(h) in result for h in definition_hashes]):
        return result
    else:
        missing_hashes = [h for h in definition_hashes if str(h) not in result]
        missing_ids = [_hash_to_id(h) for h in missing_hashes]
        raise Errors.Manifest.HashesNotFoundError(definition_type, missing_hashes, missing_ids)



