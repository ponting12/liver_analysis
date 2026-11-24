import kagglehub
import shutil
from pathlib import Path
import os

def download_and_copy():
    # Download the ILPD dataset using kagglehub
    print("Downloading Indian Liver Patient Dataset via kagglehub...")
    dataset_path = kagglehub.dataset_download("uciml/indian-liver-patient-records")
    print(f"Dataset downloaded to: {dataset_path}")

    # Find the CSV file inside the downloaded folder
    csv_files = list(Path(dataset_path).rglob("*.csv"))
    if not csv_files:
        raise FileNotFoundError("CSV file not found in the downloaded Kaggle dataset.")
    source_csv = csv_files[0]
    print(f"Found CSV: {source_csv}")

    # Destination path within the project
    dest_dir = Path(__file__).parent / "data" / "raw"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_csv = dest_dir / "liver.csv"
    shutil.copy2(source_csv, dest_csv)
    print(f"Copied CSV to: {dest_csv}")

if __name__ == "__main__":
    download_and_copy()
