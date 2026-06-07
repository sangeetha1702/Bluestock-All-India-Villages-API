import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = ROOT / "data" / "raw" / "dataset"
OUTPUT_PATH = ROOT / "data" / "cleaned"

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

required_columns = [
    "MDDS STC",
    "STATE NAME",
    "MDDS DTC",
    "DISTRICT NAME",
    "MDDS Sub_DT",
    "SUB-DISTRICT NAME",
    "MDDS PLCN",
    "Area Name"
]

all_data = []


def clean_code(series, length):
    return (
        series.astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
        .str.zfill(length)
    )


for file in RAW_DATA_PATH.iterdir():

    if file.name.startswith(".") or file.name.startswith("._"):
        continue

    if file.suffix.lower() not in [".xls", ".xlsx", ".ods"]:
        continue

    print(f"Reading file: {file.name}")

    try:
        if file.suffix.lower() == ".ods":
            engine = "odf"
        elif file.suffix.lower() == ".xls":
            engine = "xlrd"
        else:
            engine = "openpyxl"

        try:
            df = pd.read_excel(
                file,
                sheet_name="Village Directory",
                dtype=str,
                keep_default_na=False,
                engine=engine
            )
        except Exception:
            df = pd.read_excel(
                file,
                dtype=str,
                keep_default_na=False,
                engine=engine
            )

        df.columns = df.columns.astype(str).str.strip()

        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            print(f"Skipped {file.name}. Missing columns: {missing_columns}")
            continue

        df = df[required_columns].copy()
        all_data.append(df)

    except Exception as e:
        print(f"Error reading {file.name}: {e}")


if not all_data:
    raise Exception("No valid Excel/ODS files found. Check data/raw/dataset folder.")

final_df = pd.concat(all_data, ignore_index=True)

final_df = final_df.rename(columns={
    "MDDS STC": "state_code",
    "STATE NAME": "state_name",
    "MDDS DTC": "district_code",
    "DISTRICT NAME": "district_name",
    "MDDS Sub_DT": "subdistrict_code",
    "SUB-DISTRICT NAME": "subdistrict_name",
    "MDDS PLCN": "village_code",
    "Area Name": "village_name"
})

text_columns = ["state_name", "district_name", "subdistrict_name", "village_name"]

for col in text_columns:
    final_df[col] = final_df[col].astype(str).str.strip()

final_df["state_code"] = clean_code(final_df["state_code"], 2)
final_df["district_code"] = clean_code(final_df["district_code"], 3)
final_df["subdistrict_code"] = clean_code(final_df["subdistrict_code"], 5)
final_df["village_code"] = clean_code(final_df["village_code"], 6)

final_df = final_df.drop_duplicates()

master_df = final_df.copy()

country_df = pd.DataFrame([{
    "country_code": "IN",
    "country_name": "India"
}])

states_df = final_df[["state_code", "state_name"]].drop_duplicates()
states_df = states_df[states_df["state_code"] != "00"]

districts_df = final_df[
    ["state_code", "district_code", "district_name"]
].drop_duplicates()
districts_df = districts_df[districts_df["district_code"] != "000"]

subdistricts_df = final_df[
    ["state_code", "district_code", "subdistrict_code", "subdistrict_name"]
].drop_duplicates()
subdistricts_df = subdistricts_df[subdistricts_df["subdistrict_code"] != "00000"]

villages_df = final_df[
    ["state_code", "district_code", "subdistrict_code", "village_code", "village_name"]
].drop_duplicates()
villages_df = villages_df[villages_df["village_code"] != "000000"]

country_df.to_csv(OUTPUT_PATH / "country.csv", index=False, encoding="utf-8-sig")
states_df.to_csv(OUTPUT_PATH / "states.csv", index=False, encoding="utf-8-sig")
districts_df.to_csv(OUTPUT_PATH / "districts.csv", index=False, encoding="utf-8-sig")
subdistricts_df.to_csv(OUTPUT_PATH / "subdistricts.csv", index=False, encoding="utf-8-sig")
villages_df.to_csv(OUTPUT_PATH / "villages.csv", index=False, encoding="utf-8-sig")
master_df.to_csv(OUTPUT_PATH / "village_master.csv", index=False, encoding="utf-8-sig")

print("\nData cleaning completed successfully!")
print("-----------------------------------")
print("Total master rows:", len(master_df))
print("Total states:", len(states_df))
print("Total districts:", len(districts_df))
print("Total sub-districts:", len(subdistricts_df))
print("Total villages:", len(villages_df))
print("\nCleaned files saved in: data/cleaned")