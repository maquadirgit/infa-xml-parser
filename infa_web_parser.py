import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import sqlparse
import io

def beautify_sql(sql):
    return sqlparse.format(sql, reindent=True, keyword_case='upper') if sql else ""

def extract_sql_clauses(sql):
    if not sql:
        return {}
    parsed = sqlparse.parse(sql)[0]
    clauses = {'SELECT': '', 'FROM': '', 'WHERE': '', 'JOIN': '', 'OTHER': ''}
    current_clause = 'OTHER'
    for token in parsed.tokens:
        if token.ttype is sqlparse.tokens.DML and token.value.upper() in clauses:
            current_clause = token.value.upper()
        elif token.is_keyword and token.value.upper() in clauses:
            current_clause = token.value.upper()
        elif current_clause in clauses:
            clauses[current_clause] += str(token)
    return {k: v.strip() for k, v in clauses.items() if v.strip()}

def parse_xml(upload):
    tree = ET.parse(upload)
    root = tree.getroot()
    mapping_name = root.attrib.get("NAME", "Unknown_Mapping")
    is_mapplet = root.tag == "MAPPLET"
    data = []
    reusable_lookup = {inst.attrib.get("TRANSFORMATION_NAME") for inst in root.findall(".//INSTANCE") if inst.attrib.get("REUSABLE") == "YES"}

    def add_logic(trans_type, trans_name, field, logic, is_reusable="NO"):
        if field != logic and logic and logic.strip():
            row = {
                "Mapping Name": mapping_name,
                "Type": trans_type,
                "Name": trans_name,
                "Reusable": is_reusable,
                "Is_Mapplet": "YES" if is_mapplet else "NO",
                "Field": field,
                "Logic": beautify_sql(logic),
                **extract_sql_clauses(logic)
            }
            data.append(row)

    for transformation in root.findall(".//TRANSFORMATION"):
        trans_type = transformation.attrib.get("TYPE")
        trans_name = transformation.attrib.get("NAME")
        is_reusable = "YES" if trans_name in reusable_lookup else "NO"

        if trans_type == "Expression":
            for f in transformation.findall(".//TRANSFORMFIELD"):
                add_logic(trans_type, trans_name, f.attrib.get("NAME"), f.attrib.get("EXPRESSION"), is_reusable)

        elif trans_type == "Filter":
            for inst in root.findall(f".//INSTANCE[@TRANSFORMATION_NAME='{trans_name}']"):
                add_logic(trans_type, trans_name, "FILTERCONDITION", inst.attrib.get("FILTERCONDITION"), is_reusable)

        elif trans_type == "Router":
            for g in transformation.findall(".//GROUP"):
                add_logic(trans_type, trans_name, g.attrib.get("NAME"), g.attrib.get("CONDITION"), is_reusable)

        elif trans_type == "Lookup Procedure":
            for t in transformation.findall(".//TABLEATTRIBUTE"):
                if t.attrib.get("NAME", "").upper() == "LOOKUP_SQL_OVERRIDE":
                    add_logic(trans_type, trans_name, "SQL Override", t.attrib.get("VALUE"), is_reusable)

        elif trans_type == "Aggregator":
            for f in transformation.findall(".//AGGREGATORFIELD"):
                add_logic(trans_type, trans_name, f.attrib.get("NAME"), f.attrib.get("EXPRESSION"), is_reusable)

        elif trans_type == "Joiner":
            for inst in root.findall(f".//INSTANCE[@TRANSFORMATION_NAME='{trans_name}']"):
                add_logic(trans_type, trans_name, "Join Condition", inst.attrib.get("JOINCONDITION"), is_reusable)

        elif trans_type == "Source Qualifier":
            for inst in root.findall(f".//INSTANCE[@TRANSFORMATION_NAME='{trans_name}']"):
                for key in ["SQLQUERY", "USERDEFINEDSQL", "SOURCEFILTER", "SELECTDISTINCT"]:
                    if key in inst.attrib:
                        add_logic(trans_type, trans_name, key, inst.attrib.get(key), is_reusable)

        elif trans_type == "SQL Transformation":
            for t in transformation.findall(".//TABLEATTRIBUTE"):
                if t.attrib.get("NAME") == "Sql Query":
                    add_logic(trans_type, trans_name, "SQL Query", t.attrib.get("VALUE"), is_reusable)

        elif trans_type == "Update Strategy":
            for f in transformation.findall(".//TRANSFORMFIELD"):
                add_logic(trans_type, trans_name, f.attrib.get("NAME"), f.attrib.get("EXPRESSION"), is_reusable)

        elif trans_type == "Normalizer":
            for nf in transformation.findall(".//NORMALIZABLEFIELD"):
                logic = f"NORMALIZED: {nf.attrib.get('NAME')}({nf.attrib.get('OCCURS')})"
                add_logic(trans_type, trans_name, nf.attrib.get("NAME"), logic, is_reusable)

        elif trans_type == "Sorter":
            for f in transformation.findall(".//FIELD"):
                if f.attrib.get("KEYTYPE"):
                    logic = f"SORTKEY ({f.attrib.get('KEYTYPE')})"
                    add_logic(trans_type, trans_name, f.attrib.get("NAME"), logic, is_reusable)

        elif trans_type == "Sequence Generator":
            for attr in transformation.findall(".//TABLEATTRIBUTE"):
                name = attr.attrib.get("NAME", "")
                if name in ["STARTVALUE", "INCREMENTBY"]:
                    add_logic(trans_type, trans_name, name, attr.attrib.get("VALUE", ""), is_reusable)

        elif trans_type == "Union":
            for g in transformation.findall(".//GROUP"):
                logic = f"Group {g.attrib.get('NAME')}"
                add_logic(trans_type, trans_name, g.attrib.get("NAME"), logic, is_reusable)

        elif trans_type == "Rank":
            for f in transformation.findall(".//FIELD"):
                if f.attrib.get("RANK") == "YES":
                    logic = f"RANK FIELD (TOPN: {f.attrib.get('TOPN')})"
                    add_logic(trans_type, trans_name, f.attrib.get("NAME"), logic, is_reusable)

    # Additional check: Target instance logic
    for instance in root.findall(".//INSTANCE[@TYPE='TARGET']"):
        target_name = instance.attrib.get("TRANSFORMATION_NAME", "")
        for key in ["UPDATE_STRATEGY", "INSERT", "DELETE", "TRUNCATE_TARGET"]:
            logic = instance.attrib.get(key)
            if logic:
                add_logic("Target", target_name, key, logic)

    df = pd.DataFrame(data)
    df = df[df["Logic"].notnull()]
    df = df[df["Logic"].str.strip() != ""]
    return mapping_name, df

# Streamlit UI
st.set_page_config(page_title="Informatica XML Parser", layout="wide")
st.title("🔍 Informatica Mapping Logic Extractor (Extended + Target & Source Qualifier Logic)")

uploaded_files = st.file_uploader("Upload one or more Informatica Mapping XML files", type="xml", accept_multiple_files=True)

if uploaded_files:
    combined_df = pd.DataFrame()
    all_sheets = {}
    for file in uploaded_files:
        mapping_name, df = parse_xml(file)
        all_sheets[mapping_name[:31]] = df
        combined_df = pd.concat([combined_df, df], ignore_index=True)

    st.success("✅ Logic extracted from all supported transformations including Source Qualifier & Target logic.")
    st.dataframe(combined_df)

    towrite = io.BytesIO()
    with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
        for name, df in all_sheets.items():
            df.to_excel(writer, index=False, sheet_name=name[:31])
    st.download_button("📥 Download as Excel", towrite.getvalue(), file_name="Informatica_Logic_Parsed_Extended.xlsx")
