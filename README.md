# 🛠️ Informatica XML Mapping Logic Parser

This Streamlit web tool parses Informatica PowerCenter mapping `.xml` exports and extracts implemented logic (e.g., expressions, filters, SQL overrides) in a **readable Excel format**.

---

## 🔍 Features

- Supports multiple transformation types:
  - Expression, Filter, Router, Lookup, Aggregator, Joiner, Source Qualifier, SQL Transformation, Update Strategy, etc.
- Extracts:
  - SQL overrides (with clause breakdown)
  - Source Qualifier queries & filters
  - Target instance logic
- Outputs:
  - Multi-sheet Excel (one per mapping)
  - Clause-wise SQL formatting
  - Flags for reusable/mapplet logic
- Skips logic-less or repetitive rows

---

## 📦 How to Use

1. Export mapping `.xml` files from Informatica Designer
2. Upload them to this tool
3. Download clean Excel logic documentation in one click

---

## 🚀 Live App

👉 Hosted on Streamlit Cloud: [Insert your app URL here]

---

## 🧱 Built With

- Python
- Streamlit
- Pandas
- SQLParse
- OpenPyXL

---

## 🧑‍💻 Author

Abdul Quadir
