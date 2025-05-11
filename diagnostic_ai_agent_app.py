import streamlit as st
import pandas as pd
from openai import OpenAI

# Load API key
api_key = st.secrets.get("OPENAI_API_KEY", None)
if not api_key:
    st.error("Missing OpenAI API key. Please set OPENAI_API_KEY in secrets.toml or Streamlit Cloud.")
    st.stop()

client = OpenAI(api_key=api_key)

def process_entry(complaint, issue_description):
    prompt = f"""
You are an automotive diagnostic engineer.

Given the complaint and issue description below, summarize the conversation in a professional tone (in 5 bullet points or ~50 words), identify the diagnostic category (from the options below), and if the category is "Other", explain why in 50 words.

Complaint: {complaint}
Issue Description: {issue_description}

Options: [Diagnostic method NOK / Part failure / ECU replacement / Wiring harness / Reprogramming / Other]

Return in this format:
Summary:
- ...
- ...
Category: ...
Reason (only if "Other"): ...
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

st.title("Automotive Diagnostic AI Agent")
st.write("Upload an Excel file with Complaint and Issue Description columns.")

uploaded_file = st.file_uploader("Upload Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("Detected columns:", df.columns.tolist())

    if "Complaint" not in df.columns or "Issue Description" not in df.columns:
        st.error("Excel must contain 'Complaint' and 'Issue Description' columns.")
        st.stop()

    st.write("Preview of uploaded data:")
    st.dataframe(df[["Complaint", "Issue Description"]].head())

    if st.button("Run AI Analysis"):
        st.info("Processing... please wait.")
        df["AI Output"] = df.apply(lambda row: process_entry(str(row["Complaint"]), str(row["Issue Description"])), axis=1)

        df[["Summary", "Category", "Reason (Other)"]] = df["AI Output"].str.extract(
            r"Summary:\\s*(.*?)\\s*Category:\\s*(.*?)\\s*Reason.*?:\\s*(.*)", expand=True
        )

        st.success("AI processing complete.")
        st.dataframe(df[["Summary", "Category", "Reason (Other)"]])

        output_file = "AI_Diagnostic_Output.xlsx"
        df.to_excel(output_file, index=False)
        with open(output_file, "rb") as f:
            st.download_button("Download Results", f, file_name="AI_Diagnostic_Output.xlsx")
