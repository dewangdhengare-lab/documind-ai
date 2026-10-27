"""CSV parsing and analysis using pandas."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def parse_csv(file_path: Path) -> tuple[list[dict], dict[str, Any]]:
    """
    Parse a CSV file into sections and extract metadata.

    Returns:
        A tuple of (sections, csv_meta).
        sections: list of dicts with 'text', 'section_index'.
        csv_meta: dict with column info, shape, dtypes, etc.
    """
    df = pd.read_csv(str(file_path), encoding="utf-8", on_bad_lines="skip")

    csv_meta: dict[str, Any] = {
        "columns": list(df.columns),
        "shape": list(df.shape),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "numeric_columns": list(df.select_dtypes(include="number").columns),
    }

    # Add basic statistics for numeric columns
    numeric_df = df.select_dtypes(include="number")
    if not numeric_df.empty:
        csv_meta["statistics"] = {}
        for col in numeric_df.columns:
            csv_meta["statistics"][col] = {
                "mean": round(float(numeric_df[col].mean()), 4) if not numeric_df[col].isna().all() else None,
                "median": round(float(numeric_df[col].median()), 4) if not numeric_df[col].isna().all() else None,
                "min": round(float(numeric_df[col].min()), 4) if not numeric_df[col].isna().all() else None,
                "max": round(float(numeric_df[col].max()), 4) if not numeric_df[col].isna().all() else None,
                "sum": round(float(numeric_df[col].sum()), 4) if not numeric_df[col].isna().all() else None,
                "std": round(float(numeric_df[col].std()), 4) if not numeric_df[col].isna().all() else None,
                "count": int(numeric_df[col].count()),
                "null_count": int(numeric_df[col].isna().sum()),
            }

    # Convert rows to text sections (batch rows together)
    sections: list[dict] = []
    batch_size = 50  # rows per section
    for start in range(0, len(df), batch_size):
        end = min(start + batch_size, len(df))
        batch = df.iloc[start:end]
        text = f"Rows {start + 1} to {end}:\n{batch.to_string(index=False)}"
        sections.append({
            "section_index": start // batch_size,
            "heading": f"Rows {start + 1}-{end}",
            "text": text,
        })

    # Add a summary section at the beginning
    summary_parts = [
        f"CSV Summary: {df.shape[0]} rows × {df.shape[1]} columns",
        f"Columns: {', '.join(df.columns)}",
    ]
    if csv_meta.get("statistics"):
        summary_parts.append("\nNumeric Column Statistics:")
        for col, stats in csv_meta["statistics"].items():
            summary_parts.append(
                f"  {col}: mean={stats['mean']}, median={stats['median']}, "
                f"min={stats['min']}, max={stats['max']}, sum={stats['sum']}"
            )

    sections.insert(0, {
        "section_index": -1,
        "heading": "CSV Summary",
        "text": "\n".join(summary_parts),
    })

    return sections, csv_meta


def run_csv_query(file_path: Path, query: str) -> str:
    """
    Run a natural-language-style query on a CSV by computing common aggregations.

    Returns a text description of the result that can be included in LLM context.
    """
    try:
        df = pd.read_csv(str(file_path), encoding="utf-8", on_bad_lines="skip")
    except Exception as e:
        return f"Error reading CSV: {e}"

    results: list[str] = []
    results.append(f"Dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    results.append(f"Columns: {', '.join(df.columns)}")

    # Compute describe for numeric cols
    numeric_df = df.select_dtypes(include="number")
    if not numeric_df.empty:
        results.append("\nNumeric Summary:")
        results.append(numeric_df.describe().to_string())

    # Value counts for categorical columns (top 10 per col)
    cat_df = df.select_dtypes(include=["object", "category"])
    if not cat_df.empty:
        results.append("\nCategorical Columns (top values):")
        for col in cat_df.columns[:5]:  # limit to first 5 categorical cols
            vc = df[col].value_counts().head(10)
            results.append(f"\n  {col}:")
            for val, count in vc.items():
                results.append(f"    {val}: {count}")

    return "\n".join(results)
