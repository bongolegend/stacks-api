from sqlalchemy import Table, Column, Row

def prefix(table: Table, prefix: str) -> list[Column]:
    """Add a prefix to the name of each column in a table"""
    return [col.label(f"{prefix}{col.name}") for col in table.columns]

def filter_by_prefix(row: Row, prefix: str) -> dict:
        """Filter key-value pairs into their respective tables based on the column name prefix"""
        return {k[len(prefix):]: v for k, v in row._mapping.items() if k.startswith(prefix)}