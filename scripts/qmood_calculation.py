#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QMOOD hesaplama scripti - pandas/numpy gerektirmez.

Kullanım:
  python scripts\qmood_calculation.py

Bu script doğrudan CK Tool ham çıktılarından okur:
  data/raw_metrics/<version>/class.csv
  data/raw_metrics/<version>/method.csv

Çıktılar:
  data/processed_metrics/version_metrics_summary.csv
  data/processed_metrics/picocli_qmood_scores.csv
  data/qmood_scores/qmood_design_properties.csv
  data/qmood_scores/qmood_scores.csv
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List, Optional


DEFAULT_VERSIONS = [
    "v4.0.4",
    "v4.1.0",
    "v4.1.4",
    "v4.2.0",
    "v4.3.0",
    "v4.3.2",
    "v4.4.0",
    "v4.5.2",
    "v4.6.3",
    "v4.7.7",
]


def norm_name(name: str) -> str:
    return name.lower().replace("_", "").replace("-", "").strip()


def find_col(fieldnames: List[str], candidates: List[str]) -> Optional[str]:
    lookup = {norm_name(c): c for c in fieldnames}
    for cand in candidates:
        key = norm_name(cand)
        if key in lookup:
            return lookup[key]
    return None


def to_float(value) -> float:
    try:
        if value is None or value == "":
            return 0.0
        return float(str(value).replace(",", "."))
    except Exception:
        return 0.0


def read_csv_rows(path: Path) -> tuple[List[str], List[Dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    return fieldnames, rows


def col_values(rows: List[Dict[str, str]], col: Optional[str]) -> List[float]:
    if col is None:
        return []
    return [to_float(row.get(col, 0)) for row in rows]


def mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def summarize_version(raw_dir: Path, version: str) -> Dict[str, float | str]:
    version_dir = raw_dir / version
    class_csv = version_dir / "class.csv"
    method_csv = version_dir / "method.csv"

    if not class_csv.exists():
        raise FileNotFoundError(f"Bulunamadı: {class_csv}")

    fields, rows = read_csv_rows(class_csv)

    cbo_col = find_col(fields, ["cbo", "CBO"])
    wmc_col = find_col(fields, ["wmc", "WMC"])
    dit_col = find_col(fields, ["dit", "DIT"])
    noc_col = find_col(fields, ["noc", "NOC"])
    rfc_col = find_col(fields, ["rfc", "RFC"])
    lcom_col = find_col(fields, ["lcom", "LCOM"])
    tcc_col = find_col(fields, ["tcc", "TCC"])

    public_methods_col = find_col(fields, ["publicMethodsQty", "public_methods_qty"])
    total_fields_col = find_col(fields, ["totalFieldsQty", "total_fields_qty"])
    private_fields_col = find_col(fields, ["privateFieldsQty", "private_fields_qty"])
    protected_fields_col = find_col(fields, ["protectedFieldsQty", "protected_fields_qty"])

    class_count = len(rows)

    if method_csv.exists():
        _, method_rows = read_csv_rows(method_csv)
        method_count = len(method_rows)
    else:
        total_methods_col = find_col(fields, ["totalMethodsQty", "total_methods_qty"])
        method_count = int(sum(col_values(rows, total_methods_col)))

    noc_values = col_values(rows, noc_col)
    classes_with_children = sum(1 for v in noc_values if v > 0)

    public_methods_qty = sum(col_values(rows, public_methods_col))
    total_fields_qty = sum(col_values(rows, total_fields_col))
    private_fields_qty = sum(col_values(rows, private_fields_col))
    protected_fields_qty = sum(col_values(rows, protected_fields_col))

    dam = 0.0
    if total_fields_qty > 0:
        dam = (private_fields_qty + protected_fields_qty) / total_fields_qty

    tcc_values = col_values(rows, tcc_col)
    nonzero_tcc = [v for v in tcc_values if v > 0]
    avg_tcc = mean(nonzero_tcc) if nonzero_tcc else ""

    return {
        "version": version,
        "class_count": class_count,
        "method_count": method_count,
        "avg_cbo": mean(col_values(rows, cbo_col)),
        "avg_wmc": mean(col_values(rows, wmc_col)),
        "avg_dit": mean(col_values(rows, dit_col)),
        "avg_rfc": mean(col_values(rows, rfc_col)),
        "avg_lcom": mean(col_values(rows, lcom_col)),
        "avg_tcc": avg_tcc,
        "dam": dam,
        "classes_with_children": classes_with_children,
        "public_methods_qty": public_methods_qty,
        "total_fields_qty": total_fields_qty,
    }


def ratio(value: float, base: float) -> float:
    if base == 0:
        return 1.0 if value == 0 else value
    return value / base


def calculate_design_properties(summary: List[Dict[str, float | str]]) -> List[Dict[str, float | str]]:
    design = []
    for row in summary:
        avg_tcc = row.get("avg_tcc", "")
        avg_lcom = float(row["avg_lcom"])

        if avg_tcc != "" and to_float(avg_tcc) > 0:
            cohesion = to_float(avg_tcc)
        else:
            cohesion = 1.0 / (1.0 + avg_lcom)

        design.append(
            {
                "version": row["version"],
                "design_size": float(row["class_count"]),
                "hierarchies": float(row["classes_with_children"]),
                "abstraction": float(row["avg_dit"]),
                "encapsulation": float(row["dam"]),
                "coupling": float(row["avg_cbo"]),
                "cohesion": cohesion,
                "composition": float(row["total_fields_qty"]),
                "inheritance": float(row["avg_dit"]),
                "polymorphism": float(row["classes_with_children"]),
                "messaging": float(row["public_methods_qty"]),
                "complexity": float(row["avg_wmc"]),
            }
        )
    return design


def calculate_scores(design: List[Dict[str, float | str]]) -> List[Dict[str, float | str]]:
    prop_cols = [
        "design_size",
        "hierarchies",
        "abstraction",
        "encapsulation",
        "coupling",
        "cohesion",
        "composition",
        "inheritance",
        "polymorphism",
        "messaging",
        "complexity",
    ]

    base = design[0]
    scores = []

    for row in design:
        n = {col: ratio(float(row[col]), float(base[col])) for col in prop_cols}

        reusability = (
            0.5 * n["design_size"]
            - 0.25 * n["coupling"]
            + 0.25 * n["cohesion"]
            + 0.5 * n["messaging"]
        )

        flexibility = (
            0.25 * n["encapsulation"]
            - 0.25 * n["coupling"]
            + 0.5 * n["composition"]
            + 0.5 * n["polymorphism"]
        )

        understandability = (
            -0.33 * n["design_size"]
            -0.33 * n["abstraction"]
            +0.33 * n["encapsulation"]
            -0.33 * n["coupling"]
            +0.33 * n["cohesion"]
            -0.33 * n["polymorphism"]
            -0.33 * n["complexity"]
        )

        functionality = (
            0.22 * n["design_size"]
            +0.22 * n["hierarchies"]
            +0.12 * n["cohesion"]
            +0.22 * n["polymorphism"]
            +0.22 * n["messaging"]
        )

        extendibility = (
            0.5 * n["abstraction"]
            -0.5 * n["coupling"]
            +0.5 * n["inheritance"]
            +0.5 * n["polymorphism"]
        )

        effectiveness = (
            0.2 * n["abstraction"]
            +0.2 * n["encapsulation"]
            +0.2 * n["composition"]
            +0.2 * n["inheritance"]
            +0.2 * n["polymorphism"]
        )

        tqi = reusability + flexibility + understandability + functionality + extendibility + effectiveness

        scores.append(
            {
                "version": row["version"],
                "reusability": reusability,
                "flexibility": flexibility,
                "understandability": understandability,
                "functionality": functionality,
                "extendibility": extendibility,
                "effectiveness": effectiveness,
                "tqi": tqi,
            }
        )

    return scores


def write_csv(path: Path, rows: List[Dict[str, float | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("Yazılacak satır yok.")
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            clean = {}
            for k, v in row.items():
                if isinstance(v, float):
                    clean[k] = f"{v:.10f}"
                else:
                    clean[k] = v
            writer.writerow(clean)


def main() -> None:
    parser = argparse.ArgumentParser(description="CK Tool ham metriklerinden QMOOD skorlarını hesaplar.")
    parser.add_argument("--raw-dir", default="data/raw_metrics")
    parser.add_argument("--processed-dir", default="data/processed_metrics")
    parser.add_argument("--out-dir", default="data/qmood_scores")
    parser.add_argument("--versions", nargs="*", default=DEFAULT_VERSIONS)
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    processed_dir = Path(args.processed_dir)
    out_dir = Path(args.out_dir)

    print(f"Ham CK Tool çıktıları okunuyor: {raw_dir}")

    summary = [summarize_version(raw_dir, version) for version in args.versions]
    design = calculate_design_properties(summary)
    scores = calculate_scores(design)

    write_csv(processed_dir / "version_metrics_summary.csv", summary)
    write_csv(out_dir / "qmood_design_properties.csv", design)
    write_csv(out_dir / "qmood_scores.csv", scores)
    write_csv(processed_dir / "picocli_qmood_scores.csv", scores)

    last = scores[-1]
    print("QMOOD hesaplama tamamlandı.")
    print(f"- Sürüm özeti: {processed_dir / 'version_metrics_summary.csv'}")
    print(f"- Tasarım özellikleri: {out_dir / 'qmood_design_properties.csv'}")
    print(f"- QMOOD skorları: {out_dir / 'qmood_scores.csv'}")
    print(f"- Uyumlu eski çıktı: {processed_dir / 'picocli_qmood_scores.csv'}")
    print()
    print("Son sürüm özeti:")
    print(
        f"{last['version']}: "
        f"Reusability={last['reusability']:.4f}, "
        f"Flexibility={last['flexibility']:.4f}, "
        f"Understandability={last['understandability']:.4f}, "
        f"Functionality={last['functionality']:.4f}, "
        f"Extendibility={last['extendibility']:.4f}, "
        f"Effectiveness={last['effectiveness']:.4f}, "
        f"TQI={last['tqi']:.4f}"
    )


if __name__ == "__main__":
    main()
