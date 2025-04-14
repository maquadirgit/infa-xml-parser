# 🛠️ Informatica XML Mapping Logic Parser

This Streamlit web app parses Informatica PowerCenter XML exports and extracts transformation logic across all commonly used transformation types. The extracted logic is cleaned, formatted, and made available for download in Excel format.
---

## ✅ Supported Features

- Extracts logic from all major transformation types:
  - `Expression`, `Filter`, `Router`, `Lookup Procedure`, `Aggregator`, `Joiner`, `Source Qualifier`, `SQL Transformation`, `Update Strategy`, `Normalizer`, `Sorter`, `Sequence Generator`, `Union`, `Rank`, and `Target`-level configurations.
- Beautifies SQL/Expression logic using `sqlparse`.
- Splits SQL logic into logical clauses: `SELECT`, `FROM`, `WHERE`, `JOIN`, and `OTHER`.
- Marks reusable transformations and identifies mapplets.
- Supports uploading **multiple XML files** at once.
- Combines logic from all files into a unified view.
- Exports logic to **Excel with a separate sheet per mapping**.

---

## ❌ Logic Exclusion Rules

The app will automatically skip:
- Records where the **logic is null or empty**.
- Records where the **field name is exactly the same as the logic string**.

---

## 📦 Output

- An Excel file (`Informatica_Logic_Parsed_Extended.xlsx`) with:
  - One sheet per mapping name (max 31 characters due to Excel limits).
  - Beautified and clause-split logic.
  - Metadata such as transformation type, reusable status, and whether it belongs to a mapplet.

---

## 📦 How to Use

1. Launch the Streamlit app.
2. Upload one or more Informatica XML mapping files.
3. Review the parsed logic in the app UI.
4. Click the **Download as Excel** button to save the results.

---

## 🚀 Live App

👉 Hosted on Streamlit Cloud: [https://infa-xml-parser-sduqwfhu2o6mez8qdcn9jj.streamlit.app/]

---

## 🧱 Built With

- `Streamlit` – for the web UI.
- `pandas` – for data processing.
- `xml.etree.ElementTree` – for parsing Informatica XML.
- `sqlparse` – for beautifying and splitting SQL.
- `openpyxl` – for writing Excel files.

---

## 🗂 Example Use Cases

- Reverse-engineer Informatica mappings.
- Document transformation logic in Excel format.
- Validate SQL logic inside Source Qualifier or Lookup overrides.

---

## 📌 Limitations

- Only XML files exported from Informatica PowerCenter are supported.
- Sheet names in the Excel output are truncated to 31 characters due to Excel constraints.

---

## 🧑‍💻 Author

Abdul Quadir
