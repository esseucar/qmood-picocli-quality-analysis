import argparse
import os
import pandas as pd

def normalize(series):
    series = pd.to_numeric(series, errors="coerce").fillna(0)
    min_v = series.min()
    max_v = series.max()
    if max_v == min_v:
        return series * 0
    return (series - min_v) / (max_v - min_v)

def find_col(columns, candidates):
    lowered = {c.lower(): c for c in columns}
    for name in candidates:
        if name.lower() in lowered:
            return lowered[name.lower()]
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("class_csv")
    parser.add_argument("--out-dir", default="data/processed_metrics")
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()

    df = pd.read_csv(args.class_csv)

    class_col = find_col(df.columns, ["class", "Class", "classname", "className", "type"])
    wmc_col = find_col(df.columns, ["wmc", "WMC"])
    rfc_col = find_col(df.columns, ["rfc", "RFC"])
    lcom_col = find_col(df.columns, ["lcom", "LCOM"])
    cbo_col = find_col(df.columns, ["cbo", "CBO"])
    dit_col = find_col(df.columns, ["dit", "DIT"])

    required = {
        "class": class_col,
        "wmc": wmc_col,
        "rfc": rfc_col,
        "lcom": lcom_col,
        "cbo": cbo_col,
        "dit": dit_col,
    }

    missing = [k for k, v in required.items() if v is None]
    if missing:
        print("Eksik kolonlar:", missing)
        print("Bulunan kolonlar:", list(df.columns))
        raise SystemExit(1)

    result = df[[class_col, wmc_col, rfc_col, lcom_col, cbo_col, dit_col]].copy()
    result.columns = ["class", "wmc", "rfc", "lcom", "cbo", "dit"]

    for col in ["wmc", "rfc", "lcom", "cbo", "dit"]:
        result[col] = pd.to_numeric(result[col], errors="coerce").fillna(0)

    result["risk_score"] = (
        0.35 * normalize(result["lcom"]) +
        0.25 * normalize(result["wmc"]) +
        0.20 * normalize(result["rfc"]) +
        0.15 * normalize(result["cbo"]) +
        0.05 * normalize(result["dit"])
    )

    result = result.sort_values("risk_score", ascending=False).head(args.top)
    result.insert(0, "rank", range(1, len(result) + 1))

    os.makedirs(args.out_dir, exist_ok=True)

    csv_out = os.path.join(args.out_dir, "v4.7.7_risky_classes.csv")
    md_out = os.path.join(args.out_dir, "v4.7.7_risky_classes.md")

    result.to_csv(csv_out, index=False, encoding="utf-8-sig")

    with open(md_out, "w", encoding="utf-8") as f:
        f.write("| Sıra | Sınıf | WMC | RFC | LCOM | CBO | DIT | Risk Skoru |\n")
        f.write("|---:|---|---:|---:|---:|---:|---:|---:|\n")
        for _, row in result.iterrows():
            f.write(
                f"| {int(row['rank'])} | `{row['class']}` | "
                f"{row['wmc']:.0f} | {row['rfc']:.0f} | {row['lcom']:.0f} | "
                f"{row['cbo']:.0f} | {row['dit']:.0f} | {row['risk_score']:.3f} |\n"
            )

    print("Oluşturuldu:")
    print(csv_out)
    print(md_out)

if __name__ == "__main__":
    main()