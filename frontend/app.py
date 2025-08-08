import streamlit as st
from pdf_utils import extract_text_from_pdf
from gemini_ai import extract_fields_from_text, analyze_policy_with_gemini, compare_with_better_policies
import json
import requests
from datetime import date

# Ensure session key exists
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Log out option (always visible if logged in)
if st.session_state.authenticated:
    if st.sidebar.button("🔓 Log out"):
        st.session_state.clear()
        st.rerun()

if st.session_state.authenticated:

    if st.session_state.user_type == "user":
        st.subheader("📎 Upload your Insurance PDF")
        uploaded_file = st.file_uploader("Upload Insurance Document", type=["pdf"])

        if uploaded_file and st.button("Extract Info from PDF"):
            raw_text = extract_text_from_pdf(uploaded_file)
            with st.spinner("🔍 Reading document with Gemini AI..."):
                extracted_data_raw = extract_fields_from_text(raw_text)

            try:
                extracted_data_raw = extracted_data_raw.strip("` \n")
                if extracted_data_raw.lower().startswith("json"):
                    extracted_data_raw = extracted_data_raw[4:].strip()
                extracted_data = json.loads(extracted_data_raw)
            except Exception as e:
                st.error("❌ Failed to parse response from Gemini.")
                st.text("Raw Gemini response:")
                st.text(extracted_data_raw)
                st.stop()

            st.success("✅ Data extracted from insurance PDF!")
            st.json(extracted_data)
            # Analyze policy with Gemini AI
            st.subheader("🤖 AI Analysis of Your Policy")

            with st.spinner("Thinking with Gemini..."):
                analysis = analyze_policy_with_gemini(extracted_data)

            if analysis.startswith("⚠️"):
                st.error(analysis)
            else:
                st.markdown("### ✅ Pros and Cons of your Policy")
                st.markdown(analysis)
            
            # Step: Ask user if they want better options
            if st.button("🔍 Show Better Insurance Options"):
                st.subheader("🌐 Gemini's Better Policy Suggestions")

            with st.spinner("Searching web for better policies..."):
                comparison = compare_with_better_policies(extracted_data)

            if comparison.startswith("⚠️"):
                st.error(comparison)
            else:
                st.markdown(comparison)


            
            # Analyze policy with Gemini AI
            st.subheader("🤖 AI Analysis of Your Policy")
            with st.spinner("Thinking..."):
                analysis = analyze_policy_with_gemini(extracted_data)
            if analysis.startswith("⚠️"):
                st.error(analysis)
            else:
                st.markdown(analysis)



            # Pre-fill the form with Gemini output
            name = st.text_input("Name", value=extracted_data.get("name", ""))
            insurer = st.text_input("Insurance Company", value=extracted_data.get("insurer", ""))
            policy_number = st.text_input("Policy Number", value=extracted_data.get("policy_number", ""))
            start_date = st.date_input("Policy Start Date")
            end_date = st.date_input("Policy End Date")
            date_of_policy = st.date_input("Date of Policy")
            expiry_date = st.date_input("Expiry Date")
            vehicle_type = st.text_input("Vehicle Type", value=extracted_data.get("vehicle_type", ""))
            fuel_type = st.text_input("Fuel Type", value=extracted_data.get("fuel_type", ""))
            vehicle_number = st.text_input("Vehicle Number", value=extracted_data.get("vehicle_number", ""))

            if st.button("Submit Extracted Info"):
                st.success("🚀 You can now store this info to database or analyze it.")

    elif st.session_state.user_type == "manager":
        st.title("📂 Manager Dashboard")

        import sqlite3
        import pandas as pd

        try:
            conn = sqlite3.connect("../insurance.db")
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM policies")
            rows = cursor.fetchall()
            conn.close()

            if rows:
                columns = [
                    "Name", "Insurer", "Policy Number", "Policy Start Date", "Policy End Date",
                    "Date of Policy", "Expiry Date", "Vehicle Type", "Fuel Type", "Vehicle Number", "Submitted At"
                ]
                df = pd.DataFrame(rows, columns=columns)
                st.dataframe(df, use_container_width=True)

                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download as CSV", data=csv, file_name="policies.csv", mime="text/csv")
            else:
                st.info("No policies submitted yet.")
        except Exception as e:
            st.error(f"⚠️ Failed to load policies: {e}")

else:
    st.title("🔐 Login to InsuraWise")
    user_type = st.selectbox("Login as", ["User", "Manager"])
    username = st.text_input("Email / ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if user_type == "User" and username == "add@gmail.com":
            st.session_state.authenticated = True
            st.session_state.user_type = "user"
            st.rerun()
        elif user_type == "Manager" and username == "admin" and password == "admin123":
            st.session_state.authenticated = True
            st.session_state.user_type = "manager"
            st.rerun()
        else:
            st.error("❌ Invalid credentials. Try again.")
