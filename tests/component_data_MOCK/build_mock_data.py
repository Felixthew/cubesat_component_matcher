"""
Generates mock-data xlsx workbooks for the api_test.py integration tests.

The real test_requests/*.json fixtures point at schemas suffixed with `_TEST`
(power_TEST, platforms_TEST, avionics_TEST) which do not exist in the
production-like data under tests/component_data_TEST/. This script writes a
parallel directory tree of small, hand-crafted workbooks whose rows we know
exactly, so api_test.py can run against a deterministic test DB.

Run from anywhere:
    py -3.12 tests/component_data_MOCK/build_mock_data.py

Then upload to the test DB by editing src/upload_data/upload_table.py to call
    upload_all("../../tests/component_data_MOCK", has_schema=True, verbose=True)
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))


def _write_workbook(rel_path: str, sheets: dict[str, tuple[dict[str, str], list[dict]]]) -> None:
    """
    rel_path: subdirectory + filename relative to this script's directory.
    sheets: {sheet_name: ({col: dtype}, [row_dict, ...])}

    Each sheet is written so that:
      row 1 (xlsx) = header row of column names
      row 2 (xlsx) = dtype metadata row (consumed by upload_table._upload_data)
      row 3+       = real data rows
    """
    out_path = os.path.join(HERE, rel_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with pd.ExcelWriter(out_path, engine="openpyxl") as xw:
        for sheet_name, (dtypes, rows) in sheets.items():
            cols = list(dtypes.keys())
            # First row of the dataframe is the dtype metadata row;
            # subsequent rows are the real data.
            df = pd.DataFrame([dtypes, *rows], columns=cols)
            df.to_sheet = None  # silence linters; not used
            df.to_excel(xw, sheet_name=sheet_name, index=False)


# ---- power_TEST / solar_arrays ---------------------------------------------
# Used by test_request.json (specs: Company, Specific Power (W/kg))
# and test_retrieve.json (filters on Specific Power, Peak BOL Solar Array Power).
power_solar_arrays_dtypes = {
    "Company": "string",
    "Product": "string",
    "Panel Mount": "string",
    "Panel Material": "string",
    "Panel Deployment": "string",
    "Panel Deployability": "string",
    "Specific Power (W/kg)": "number",
    "Peak BOL Solar Array Power (W)": "number",
}
power_solar_arrays_rows = [
    {"Company": "DHV Technologies", "Product": "MockArray-Alpha",
     "Panel Mount": "Body", "Panel Material": "GaAs",
     "Panel Deployment": "Rigid", "Panel Deployability": "Fixed",
     "Specific Power (W/kg)": 68, "Peak BOL Solar Array Power (W)": 50},
    {"Company": "DHV Technologies", "Product": "MockArray-Beta",
     "Panel Mount": "Deployable", "Panel Material": "GaAs",
     "Panel Deployment": "Folding", "Panel Deployability": "Single-axis",
     "Specific Power (W/kg)": 75, "Peak BOL Solar Array Power (W)": 100},
    {"Company": "MMA Design", "Product": "HaWK-Mock",
     "Panel Mount": "Body", "Panel Material": "Si",
     "Panel Deployment": "Rigid", "Panel Deployability": "Fixed",
     "Specific Power (W/kg)": 45, "Peak BOL Solar Array Power (W)": 8},
    {"Company": "AAC Clyde Space", "Product": "Photon-Mock",
     "Panel Mount": "Body", "Panel Material": "GaAs",
     "Panel Deployment": "Rigid", "Panel Deployability": "Fixed",
     "Specific Power (W/kg)": 55, "Peak BOL Solar Array Power (W)": 9.25},
    {"Company": "Pumpkin Space Systems", "Product": "MockArray-Gamma",
     "Panel Mount": "Deployable", "Panel Material": "GaAs",
     "Panel Deployment": "Folding", "Panel Deployability": "Two-axis",
     "Specific Power (W/kg)": 90, "Peak BOL Solar Array Power (W)": 200},
    {"Company": "Spectrolab", "Product": "UltraTriple-Mock",
     "Panel Mount": "Deployable", "Panel Material": "GaAs",
     "Panel Deployment": "Folding", "Panel Deployability": "Single-axis",
     "Specific Power (W/kg)": 65, "Peak BOL Solar Array Power (W)": 120},
    # Below filter min on Specific Power: should be excluded by retrieve filter
    {"Company": "Generic Co", "Product": "Mock-Mini",
     "Panel Mount": "Body", "Panel Material": "Si",
     "Panel Deployment": "Rigid", "Panel Deployability": "Fixed",
     "Specific Power (W/kg)": 30, "Peak BOL Solar Array Power (W)": 4.0},
    # Above filter max on Specific Power: should be excluded by retrieve filter
    {"Company": "Generic Co", "Product": "Mock-Max",
     "Panel Mount": "Deployable", "Panel Material": "GaAs",
     "Panel Deployment": "Folding", "Panel Deployability": "Two-axis",
     "Specific Power (W/kg)": 110, "Peak BOL Solar Array Power (W)": 250},
    # Below filter min on Peak BOL Solar Array Power: excluded by retrieve filter
    {"Company": "TinyCells", "Product": "Mock-Tiny",
     "Panel Mount": "Body", "Panel Material": "Si",
     "Panel Deployment": "Rigid", "Panel Deployability": "Fixed",
     "Specific Power (W/kg)": 60, "Peak BOL Solar Array Power (W)": 2.0},
]

# ---- platforms_TEST / hosted_payloads --------------------------------------
# Used by test_req2.json (specs: Organization, Intended Destination, US Office)
# and test_req_kwargs.json (specs: Headquarters, Intended Destination, Organization).
platforms_hosted_payloads_dtypes = {
    "Organization": "string",
    "Headquarters": "string",
    "Max Volume (m3)": "number",
    "Max Mass (kg)": "number",
    "Peak Power (W)": "number",
    "3-σ Pointing Control (deg)": "number",
    "3-σ Pointing Knowledge (deg)": "number",
    "Intended Destination": "list",
    "US Office": "boolean",
}
platforms_hosted_payloads_rows = [
    {"Organization": "Creotech", "Headquarters": "Poland",
     "Max Volume (m3)": 0.10, "Max Mass (kg)": 30, "Peak Power (W)": 200,
     "3-σ Pointing Control (deg)": 0.01, "3-σ Pointing Knowledge (deg)": 0.005,
     "Intended Destination": "LEO, MEO", "US Office": 0},
    {"Organization": "Aerospacelab", "Headquarters": "Belgium",
     "Max Volume (m3)": 0.125, "Max Mass (kg)": 50, "Peak Power (W)": 300,
     "3-σ Pointing Control (deg)": 0.005, "3-σ Pointing Knowledge (deg)": 0.005,
     "Intended Destination": "LEO, GEO", "US Office": 1},
    {"Organization": "Xplore", "Headquarters": "USA",
     "Max Volume (m3)": 0.20, "Max Mass (kg)": 80, "Peak Power (W)": 500,
     "3-σ Pointing Control (deg)": 0.001, "3-σ Pointing Knowledge (deg)": 0.001,
     "Intended Destination": "LEO, GEO, MEO, GTO", "US Office": 1},
    {"Organization": "Mock Space Inc", "Headquarters": "USA",
     "Max Volume (m3)": 0.05, "Max Mass (kg)": 20, "Peak Power (W)": 100,
     "3-σ Pointing Control (deg)": 0.05, "3-σ Pointing Knowledge (deg)": 0.05,
     "Intended Destination": "LEO", "US Office": 1},
    {"Organization": "Mock GmbH", "Headquarters": "Germany",
     "Max Volume (m3)": 0.15, "Max Mass (kg)": 60, "Peak Power (W)": 250,
     "3-σ Pointing Control (deg)": 0.02, "3-σ Pointing Knowledge (deg)": 0.01,
     "Intended Destination": "LEO, GEO", "US Office": 0},
    {"Organization": "Test Aero", "Headquarters": "UK",
     "Max Volume (m3)": 0.08, "Max Mass (kg)": 40, "Peak Power (W)": 180,
     "3-σ Pointing Control (deg)": 0.03, "3-σ Pointing Knowledge (deg)": 0.02,
     "Intended Destination": "LEO, MEO, GEO", "US Office": 0},
    {"Organization": "Constellation Co", "Headquarters": "Japan",
     "Max Volume (m3)": 0.18, "Max Mass (kg)": 70, "Peak Power (W)": 400,
     "3-σ Pointing Control (deg)": 0.008, "3-σ Pointing Knowledge (deg)": 0.004,
     "Intended Destination": "GEO", "US Office": 1},
    {"Organization": "MockSpace", "Headquarters": "USA",
     "Max Volume (m3)": 0.02, "Max Mass (kg)": 10, "Peak Power (W)": 50,
     "3-σ Pointing Control (deg)": 0.10, "3-σ Pointing Knowledge (deg)": 0.08,
     "Intended Destination": "LEO", "US Office": 1},
]

# ---- avionics_TEST / boards ------------------------------------------------
# Used by test_req3.json (specs: Dimensions tuple, TRL number).
avionics_boards_dtypes = {
    "Manufacturer": "string",
    "Headquarters": "string",
    "Product": "string",
    "Dimensions": "tuple",
    "TRL": "number",
    "Power Consumption (W)": "number",
    "Orbits Flown": "string",
}
avionics_boards_rows = [
    {"Manufacturer": "Mock Avionics", "Headquarters": "USA",
     "Product": "TestBoard-1", "Dimensions": "9.5, 9, 0.5",
     "TRL": 8, "Power Consumption (W)": 0.4, "Orbits Flown": "LEO"},
    {"Manufacturer": "AAC Clyde Space", "Headquarters": "Sweden",
     "Product": "Kryten-Mock", "Dimensions": "9.6, 9.0, 0.55",
     "TRL": 9, "Power Consumption (W)": 0.4, "Orbits Flown": "LEO"},
    {"Manufacturer": "Test Boards Inc", "Headquarters": "UK",
     "Product": "NanoBoard", "Dimensions": "5, 5, 1",
     "TRL": 6, "Power Consumption (W)": 0.2, "Orbits Flown": "LEO"},
    {"Manufacturer": "MockTech", "Headquarters": "Germany",
     "Product": "RadHard-Pro", "Dimensions": "10, 10, 1",
     "TRL": 9, "Power Consumption (W)": 1.5, "Orbits Flown": "GEO"},
    {"Manufacturer": "Demo Co", "Headquarters": "Japan",
     "Product": "EduBoard", "Dimensions": "8, 6, 0.5",
     "TRL": 4, "Power Consumption (W)": 0.3, "Orbits Flown": "None"},
    {"Manufacturer": "Stellar Sys", "Headquarters": "USA",
     "Product": "DeepSpaceBoard", "Dimensions": "12, 8, 1.5",
     "TRL": 7, "Power Consumption (W)": 2.0, "Orbits Flown": "Lunar"},
    {"Manufacturer": "ProtoLab", "Headquarters": "Italy",
     "Product": "ResearchBoard", "Dimensions": "7, 7, 0.8",
     "TRL": 5, "Power Consumption (W)": 0.5, "Orbits Flown": "LEO"},
    {"Manufacturer": "MicroSat Inc", "Headquarters": "Canada",
     "Product": "MicroBoard", "Dimensions": "10, 2, 5",
     "TRL": 5, "Power Consumption (W)": 0.6, "Orbits Flown": "LEO"},
]

# ---- avionics_TEST / sat_computer ------------------------------------------
# Used by test_req4.json (specs: Voltage number).
avionics_sat_computer_dtypes = {
    "Manufacturer": "string",
    "Model": "string",
    "Voltage": "number",
    "Power Consumption (W)": "number",
    "Mass (kg)": "number",
}
avionics_sat_computer_rows = [
    {"Manufacturer": "Mock Avionics", "Model": "SatCPU-1",
     "Voltage": 28, "Power Consumption (W)": 5, "Mass (kg)": 0.30},
    {"Manufacturer": "Test Comp Co", "Model": "OBC-Mini",
     "Voltage": 12, "Power Consumption (W)": 2, "Mass (kg)": 0.10},
    {"Manufacturer": "MockTech", "Model": "OBC-Pro",
     "Voltage": 48, "Power Consumption (W)": 8, "Mass (kg)": 0.50},
    {"Manufacturer": "Stellar Sys", "Model": "DeepCPU",
     "Voltage": 50, "Power Consumption (W)": 10, "Mass (kg)": 0.70},
    {"Manufacturer": "Demo Co", "Model": "EduOBC",
     "Voltage": 5, "Power Consumption (W)": 1, "Mass (kg)": 0.05},
    {"Manufacturer": "ProtoLab", "Model": "ResearchOBC",
     "Voltage": 24, "Power Consumption (W)": 4, "Mass (kg)": 0.25},
    {"Manufacturer": "OrbitalCorp", "Model": "FlightCPU",
     "Voltage": 42, "Power Consumption (W)": 6, "Mass (kg)": 0.40},
]


def main() -> None:
    _write_workbook(
        "power_TEST/power.xlsx",
        {"solar_arrays": (power_solar_arrays_dtypes, power_solar_arrays_rows)},
    )
    _write_workbook(
        "platforms_TEST/platforms.xlsx",
        {"hosted_payloads": (platforms_hosted_payloads_dtypes,
                             platforms_hosted_payloads_rows)},
    )
    _write_workbook(
        "avionics_TEST/avionics.xlsx",
        {
            "boards": (avionics_boards_dtypes, avionics_boards_rows),
            "sat_computer": (avionics_sat_computer_dtypes,
                             avionics_sat_computer_rows),
        },
    )
    print(f"Wrote mock workbooks under {HERE}")


if __name__ == "__main__":
    main()
