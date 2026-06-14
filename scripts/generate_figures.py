import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

METRICS_FILE = BASE_DIR / "data" / "processed_metrics" / "version_metrics_summary.csv"
QMOOD_FILE = BASE_DIR / "data" / "qmood_scores" / "qmood_scores.csv"
FIGURES_DIR = BASE_DIR / "figures"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def read_csv_safely(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    # PowerShell/Windows kültür ayarlarından gelebilecek virgüllü ondalıkları düzeltir.
    for col in df.columns:
        if col != "version":
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", ".", regex=False)
                .replace({"nan": None, "NaN": None, "": None})
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


metrics = read_csv_safely(METRICS_FILE)
qmood = read_csv_safely(QMOOD_FILE)

versions = qmood["version"].tolist()


def save_line_chart(df, y_columns, title, ylabel, filename):
    plt.figure(figsize=(11, 6))

    for col in y_columns:
        plt.plot(df["version"], df[col], marker="o", label=col)

    plt.title(title)
    plt.xlabel("Version")
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    output_path = FIGURES_DIR / filename
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved: {output_path}")


# 1. TQI trendi
save_line_chart(
    qmood,
    ["tqi"],
    "Picocli QMOOD Total Quality Index Trend",
    "TQI",
    "01_tqi_trend.png",
)

# 2. QMOOD kalite nitelikleri
save_line_chart(
    qmood,
    [
        "reusability",
        "flexibility",
        "understandability",
        "functionality",
        "extendibility",
        "effectiveness",
    ],
    "Picocli QMOOD Quality Attribute Trends",
    "Normalized QMOOD Score",
    "02_qmood_quality_attributes.png",
)

# 3. Sınıf sayısı trendi
save_line_chart(
    metrics,
    ["class_count"],
    "Picocli Class Count Trend",
    "Class Count",
    "03_class_count_trend.png",
)

# 4. Metot sayısı trendi
save_line_chart(
    metrics,
    ["method_count"],
    "Picocli Method Count Trend",
    "Method Count",
    "04_method_count_trend.png",
)

# 5. Karmaşıklık ve yanıt kümesi trendi
save_line_chart(
    metrics,
    ["avg_wmc", "avg_rfc"],
    "Picocli Complexity and Response Trend",
    "Average Metric Value",
    "05_complexity_rfc_trend.png",
)

# 6. Coupling trendi
save_line_chart(
    metrics,
    ["avg_cbo"],
    "Picocli Coupling Trend",
    "Average CBO",
    "06_coupling_trend.png",
)

# 7. LCOM trendi
save_line_chart(
    metrics,
    ["avg_lcom"],
    "Picocli LCOM Trend",
    "Average LCOM",
    "07_lcom_trend.png",
)

# 8. DIT trendi
save_line_chart(
    metrics,
    ["avg_dit"],
    "Picocli Inheritance Depth Trend",
    "Average DIT",
    "08_dit_trend.png",
)

# 9. QMOOD normalize tasarım özellikleri
design_columns = [
    "design_size_n",
    "coupling_n",
    "cohesion_n",
    "messaging_n",
    "complexity_n",
]

save_line_chart(
    qmood,
    design_columns,
    "Picocli Normalized QMOOD Design Property Trends",
    "Normalized Design Property Value",
    "09_qmood_design_properties.png",
)

# 10. TQI yüzde değişimi
qmood["tqi_percent_change_from_base"] = (
    (qmood["tqi"] - qmood["tqi"].iloc[0]) / qmood["tqi"].iloc[0]
) * 100

save_line_chart(
    qmood,
    ["tqi_percent_change_from_base"],
    "Picocli TQI Change Relative to v4.0.4",
    "TQI Change (%)",
    "10_tqi_percent_change.png",
)

print("\nAll figures were generated successfully.")
