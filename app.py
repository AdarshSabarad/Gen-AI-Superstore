# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI

# OpenAI setup
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Load data
df = pd.read_csv("Superstore.csv", encoding="latin-1")

# Extract schema
def get_schema_string(df):
    return "\n".join(
        f"- {col}: {df[col].dtype}, e.g., {df[col].dropna().iloc[0]}"
        for col in df.columns
    )

# Clean code blocks
def extract_code(gpt_response):
    lines = gpt_response.strip().splitlines()
    clean_lines = [line for line in lines if not line.strip().startswith("```")]
    return "\n".join(clean_lines)

# App UI
st.title("📊 Superstore Data Assistant")

question = st.text_input("Ask your data question (e.g., 'Show sales by region')")

if question:
    schema_summary = get_schema_string(df)

    prompt = f"""
You are an AI assistant that writes correct, working Pandas + Matplotlib code for a DataFrame named `df`.

Instructions:
- 'Order Date' is a string like '11/8/2016'.
- Always convert 'Order Date' to datetime using pd.to_datetime.
- Use .dt.year or .dt.month when needed.
- Never assume 'Year' or 'Month' columns exist.
- Only return code. Do NOT include comments or explanations.
- If the question involves trends, create a chart using df.plot() or plt.plot()
- Always end with plt.show()

Schema:
{schema_summary}

User question: {question}
"""

    with st.spinner("Generating answer..."):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        raw_response = response.choices[0].message.content
        cleaned_code = extract_code(raw_response)

        st.code(cleaned_code, language="python")

        # Execute code safely
        try:
            exec(cleaned_code, {"df": df, "pd": pd, "plt": plt})
            st.pyplot(plt)
        except Exception as e:
            st.error(f"Error: {e}")
