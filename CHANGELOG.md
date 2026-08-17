# Changelog

## Unreleased

## v0.2.1

- GitHub Pages user guide with MkDocs Material and custom styling.
- Project URLs point at the live docs, not the git clone.
- README expanded with feature overview.

## v0.2.0

- Export `PdSchemaError`, `SchemaValidationError`, `TypeCheckError`, and `FunctionSchemaError`.
- `@pdfunction` validates positional and keyword arguments. Declared outputs must be returned as a dict. `bool` is not accepted as `int`.
- Column type checks do not coerce strings like `"1"` into integers. Python `int` and `float` accept matching numeric widths.
- Declarative schemas inherit columns from parent classes in Python's usual class order. `Schema([])` is empty. `strict=True` rejects extra columns.
- Client guide: [docs/user/quickstart.md](docs/user/quickstart.md).
