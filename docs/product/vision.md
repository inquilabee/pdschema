# Vision — pdschema

## Who

Data engineers and Python developers validating pandas DataFrames in data pipelines: ETL jobs, data preparation, quality gates.

## What

A lightweight schema validation library for pandas. Define column contracts (types, nullability, custom validators), validate DataFrames at runtime, and decorate functions to validate inputs and outputs. Support for PyArrow type inference and declarative schema syntax.

## Not this

- Data cleaning or transformation (we validate; you clean)
- Orchestration or workflow management
- SQL/database schema syncing
- Streaming data validation

## Success

Developers can:

- Write clear, reusable schemas with minimal boilerplate
- Get precise, actionable error messages when data doesn't match
- Validate function I/O with a decorator
- Build confidence in data quality without slowing pipelines
