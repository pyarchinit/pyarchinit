# -*- coding: utf-8 -*-
"""
UUID Manager for StratiGraph integration.

Provides persistent UUID generation, validation, and URI construction
for all PyArchInit entities. UUIDs remain stable across database exports,
imports, and synchronization cycles.
"""

import uuid
import re


# Default base URI for PyArchInit entities in the StratiGraph Knowledge Graph
DEFAULT_BASE_URI = "http://pyarchinit.org/ontology/"

# Mapping from table names to entity type slugs used in URI construction
TABLE_ENTITY_TYPE_MAP = {
    'site_table': 'site',
    'us_table': 'stratigraphic-unit',
    'inventario_materiali_table': 'find',
    'tomba_table': 'burial',
    'periodizzazione_table': 'period',
    'struttura_table': 'structure',
    'campioni_table': 'sample',
    'individui_table': 'individual',
    'pottery_table': 'pottery',
    'media_table': 'media',
    'media_thumb_table': 'media-thumbnail',
    'media_to_entity_table': 'media-link',
    'fauna_table': 'fauna',
    'ut_table': 'topographic-unit',
    'tma_table': 'archaeometric-analysis',
    'tma_materiali_table': 'archaeometric-material',
    'archeozoology_table': 'archeozoology',
    'documentazione_table': 'documentation',
    'inventario_lapidei_table': 'stone-artifact',
    'tafonomia_table': 'taphonomy',
}

# Regex for validating UUID v4 format
UUID_REGEX = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
    re.IGNORECASE
)


def generate_uuid():
    """Generate a new UUID v4 string.

    Returns:
        str: A new UUID v4 in lowercase hyphenated format.
    """
    return str(uuid.uuid4())


def validate_uuid(value):
    """Validate that a string is a properly formatted UUID v4.

    Args:
        value: The value to validate.

    Returns:
        bool: True if value is a valid UUID v4 string.
    """
    if not isinstance(value, str):
        return False
    return UUID_REGEX.match(value) is not None


def ensure_uuid(record):
    """Ensure a record has a valid entity_uuid, generating one if missing.

    Checks the record's entity_uuid attribute. If it is None, empty,
    or not a valid UUID v4, a new UUID is generated and assigned.

    Args:
        record: Any object with an entity_uuid attribute.

    Returns:
        str: The (possibly newly assigned) UUID.
    """
    current = getattr(record, 'entity_uuid', None)
    if not current or not validate_uuid(current):
        new_uuid = generate_uuid()
        record.entity_uuid = new_uuid
        return new_uuid
    return current


def build_uri(entity_type, entity_uuid, base_uri=None):
    """Construct a persistent URI for an entity.

    Args:
        entity_type: The entity type slug (e.g. 'stratigraphic-unit')
            or the table name (e.g. 'us_table').
        entity_uuid: The entity's UUID.
        base_uri: Optional base URI. Defaults to DEFAULT_BASE_URI.

    Returns:
        str: A URI in the format {base_uri}{type}/{uuid}
    """
    if base_uri is None:
        base_uri = DEFAULT_BASE_URI
    # Resolve table name to entity type slug if needed
    type_slug = TABLE_ENTITY_TYPE_MAP.get(entity_type, entity_type)
    # Ensure base URI ends with /
    if not base_uri.endswith('/'):
        base_uri += '/'
    return f"{base_uri}{type_slug}/{entity_uuid}"


def get_entity_type_for_table(table_name):
    """Get the entity type slug for a given table name.

    Args:
        table_name: The database table name.

    Returns:
        str: The entity type slug, or the table name itself if not mapped.
    """
    return TABLE_ENTITY_TYPE_MAP.get(table_name, table_name)
