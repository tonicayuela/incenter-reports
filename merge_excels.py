# merge_excels.py
import pandas as pd
import pathlib

DOWNLOADS_DIR = "downloads"

def merge_excels(start_date, end_date):

    files = list(pathlib.Path(DOWNLOADS_DIR).glob("*.xlsx"))

    if not files:
        print("No se encontraron archivos Excel en /downloads")
        return

    dfs = []

    for file in files:
        print("Leyendo:", file.name)

        df = pd.read_excel(file)

        dfs.append(df)

    merged = pd.concat(dfs, ignore_index=True)

    output_file = f"merged_reports_{start_date[:10]}_{end_date[:10]}.xlsx"

    merged.to_excel(output_file, index=False)

    print("\nArchivo generado:", output_file)
    print("Total filas:", len(merged))


if __name__ == "__main__":
    merge_excels()