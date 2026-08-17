class PdSchemaError(Exception):
    """Base error for pdschema failures."""


class SchemaValidationError(PdSchemaError, ValueError):
    """A DataFrame did not match a Schema."""


class TypeCheckError(PdSchemaError, TypeError):
    """A column or value had the wrong type."""


class FunctionSchemaError(PdSchemaError, TypeError):
    """A @pdfunction argument or output contract failed."""
