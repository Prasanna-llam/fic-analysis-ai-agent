
import streamlit as st
import pandas as pd
import openai

# Set your OpenAI API key here or use Streamlit secrets
openai.api_key = st.secrets.get("OPENAI_API_KEY", "your-api-key-here")
st.write("API key loaded:", st.secrets["OPENAI_API_KEY"][:8] + "****")

# Function to process each entry with OpenAI
def process_entry(conversation, issue_description):
    prompt = f"""
You are an automotive diagnostic engineer.

Given the complaint and issue description below, summarize the conversation in a professional tone (in 5 bullet points or ~50 words), identify the diagnostic category (from the options below), and if the category is "Other", explain why in 50 words.

Complaint: {conversation}
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
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        reply = response['choices'][0]['message']['content']
        return reply
    except Exception as e:
        return f"Error: {e}"

# Streamlit UI
st.title("Automotive Diagnostic AI Agent")
st.write("Upload an Excel file with complaint (Column B) and issue description (Column C). The AI will summarize and classify each entry.")

uploaded_file = st.file_uploader("Upload Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("File uploaded successfully!")

    # Display preview
    st.write("Preview of Uploaded Data:")
    st.dataframe(df.head())

    if st.button("Run AI Analysis"):
        st.info("Processing... Please wait.")

        results = df.apply(lambda row: process_entry(str(row["Complaint"]), str(row["Issue Description"])), axis=1)
        df["AI Output"] = results

        # Extract fields if possible
        df[["Summary", "Category", "Reason (Other)"]] = df["AI Output"].str.extract(
            r"Summary:\s*(.*?)\s*Category:\s*(.*?)\s*Reason.*?:\s*(.*)", expand=True
        )

        st.write("Processed Data:")
        st.dataframe(df[["Summary", "Category", "Reason (Other)"]].fillna(""))

        # Save and offer download
        output_file = "AI_Processed_Output.xlsx"
        df.to_excel(output_file, index=False)
        with open(output_file, "rb") as f:
            st.download_button("Download Results", f, file_name="AI_Output.xlsx")
