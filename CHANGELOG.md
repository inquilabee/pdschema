# Changelog

## Unreleased

## v0.2.0

- Export `PdSchemaError`, `SchemaValidationError`, `TypeCheckError`, and `FunctionSchemaError`.
- `@pdfunction` validates positional and keyword arguments. Declared outputs must be returned as a dict. `bool` is not accepted as `int`.
- Column type checks do not coerce strings like `"1"` into integers. Python `int` and `float` accept matching numeric widths.
- Declarative schemas inherit columns in MRO order. `Schema([])` is empty. `strict=True` rejects extra columns.
- Client guide: [docs/user/quickstart.md](docs/user/quickstart.md).
