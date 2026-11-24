"""
download_dataset.py
-------------------
Run this script ONCE locally to download the ILPD dataset from Kaggle
and copy it into data/raw/liver.csv.

Usage:
    pip install kagglehub
    python download_dataset.py

NOTE: This script is NOT used by the Streamlit app (app.py).
      It is only needed if you need to re-download the raw dataset locally.
"""


def download_and_copy():
    try:
        import kagglehub          # only imported when this function is called
    except ImportError:
        print("kagglehub is not installed. Run: pip install kagglehub")
        return

    import shutil
    from pathlib import Path

    print("Downloading Indian Liver Patient Dataset via kagglehub...")
    dataset_path = kagglehub.dataset_download("uciml/indian-liver-patient-records")
    print(f"Dataset downloaded to: {dataset_path}")

    # Find the CSV inside the downloaded folder
    csv_files = list(Path(dataset_path).rglob("*.csv"))
    if not csv_files:
        raise FileNotFoundError("CSV file not found in downloaded Kaggle dataset.")

    source_csv = csv_files[0]
    dest_dir = Path(__file__).parent / "data" / "raw"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_csv = dest_dir / "liver.csv"
    shutil.copy2(source_csv, dest_csv)
    print(f"Copied CSV to: {dest_csv}")


if __name__ == "__main__":
    download_and_copy()
