import streamlit as st
import requests
import json
from datetime import date
from models import BikeInsurancePolicy
from vision_gemini_processor import process_insurance_document

st.set_page_config(
    page_title="InsuraWise API Documentation",
    page_icon="📋",
    layout="wide"
)

st.title("🔍 InsuraWise API Documentation & Testing")
st.markdown("---")

# Sidebar for navigation
page = st.sidebar.selectbox(
    "Choose a section:",
    ["API Overview", "PDF Processing", "Submit Policy", "View Database", "JSON Schema"]
)

if page == "API Overview":
    st.header("📚 API Overview")
    st.markdown("""
    ### InsuraWise Insurance Policy Management API
    
    This API allows you to submit and manage insurance policies for two-wheelers.
    
    **Base URL:** `http://localhost:8000`
    
    **Available Endpoints:**
    - `POST /submit-policy/` - Submit a new insurance policy
    - `GET /docs` - Interactive API documentation (Swagger UI)
    - `GET /redoc` - Alternative API documentation
    
    **Authentication:** Currently using simple authentication
    """)

elif page == "PDF Processing":
    st.header("📄 PDF Document Processing")
    st.markdown("Upload your insurance PDF and extract information using Google Cloud Vision API and Gemini AI")
    
    # Product type selection
    product_type = st.selectbox(
        "Select Product Type:",
        ["CAR", "BIKE", "HEALTH"],
        help="Select the type of insurance product"
    )
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload Insurance PDF Document", 
        type=["pdf"],
        help="Upload your insurance policy PDF for processing"
    )
    
    if uploaded_file and st.button("🔍 Process PDF with Vision API & Gemini AI"):
        with st.spinner("📖 Scanning PDF with Google Cloud Vision API..."):
            # Process the PDF
            result = process_insurance_document(uploaded_file, product_type)
        
        if isinstance(result, dict) and "Coverton imp_keys" in result:
            st.success("✅ PDF processed successfully!")
            
            # Display the extracted JSON
            st.subheader("📋 Extracted Information")
            st.json(result)
            
            # Show key information in a more readable format
            st.subheader("📊 Key Information Summary")
            data = result["Coverton imp_keys"]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Customer Information:**")
                st.write(f"**Name:** {data.get('firstName', '')} {data.get('lastName', '')}")
                st.write(f"**Email:** {data.get('emailId', 'N/A')}")
                st.write(f"**Phone:** {data.get('phoneNo', 'N/A')}")
                st.write(f"**DOB:** {data.get('dob', 'N/A')}")
                
                st.markdown("**Address:**")
                st.write(f"**Lane 1:** {data.get('lane1', 'N/A')}")
                st.write(f"**Lane 2:** {data.get('lane2', 'N/A')}")
                st.write(f"**Area:** {data.get('area', 'N/A')}")
                st.write(f"**State:** {data.get('state', 'N/A')}")
                st.write(f"**Pincode:** {data.get('pincode', 'N/A')}")
            
            with col2:
                st.markdown("**Policy Information:**")
                st.write(f"**Insurance Company:** {data.get('insuranceCompany', 'N/A')}")
                st.write(f"**Policy Number:** {data.get('policyno', 'N/A')}")
                st.write(f"**Category:** {data.get('category', 'N/A')}")
                st.write(f"**Sub Product:** {data.get('subProduct', 'N/A')}")
                st.write(f"**Product:** {data.get('product', 'N/A')}")
                
                st.markdown("**Policy Dates:**")
                st.write(f"**Commencement Date:** {data.get('commenceMentDate', 'N/A')}")
                st.write(f"**Policy End Date:** {data.get('policyEndDate', 'N/A')}")
                st.write(f"**Policy Issued Date:** {data.get('policyissuedDate', 'N/A')}")
                
                st.markdown("**Financial Information:**")
                st.write(f"**Sum Insured:** {data.get('sumInsuredIdv', 'N/A')}")
                st.write(f"**GST Percentage:** {data.get('gstPercentage', 'N/A')}")
                st.write(f"**Gross Premium:** {data.get('grossPremium', 'N/A')}")
            
            # Store in session state for potential submission
            st.session_state.extracted_data = result
            
        elif isinstance(result, str) and result.startswith("⚠️"):
            st.error(result)
        else:
            st.error("❌ Failed to process PDF. Please try again.")
            st.json(result)

elif page == "Submit Policy":
    st.header("📝 Submit Insurance Policy")
    st.markdown("Test the API by submitting a policy")
    
    # Create form for policy submission
    with st.form("policy_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Policy Holder Name", value="John Doe")
            email = st.text_input("Email Address", value="john@example.com")
            insurer = st.text_input("Insurance Company", value="ABC Insurance")
            policy_number = st.text_input("Policy Number", value="POL123456")
            policy_start_date = st.date_input("Policy Start Date", value=date(2024, 1, 1))
            policy_end_date = st.date_input("Policy End Date", value=date(2024, 12, 31))
        
        with col2:
            date_of_policy = st.date_input("Date of Policy", value=date(2024, 1, 1))
            expiry_date = st.date_input("Expiry Date", value=date(2024, 12, 31))
            product_type = st.selectbox("Product Type", ["CAR", "BIKE", "HEALTH"])
        
        submitted = st.form_submit_button("Submit Policy")
        
        if submitted:
            # Create the JSON payload
            policy_data = {
                "name": name,
                "email": email,
                "insurer": insurer,
                "policy_number": policy_number,
                "policy_start_date": policy_start_date.isoformat(),
                "policy_end_date": policy_end_date.isoformat(),
                "date_of_policy": date_of_policy.isoformat(),
                "expiry_date": expiry_date.isoformat(),
                "product_type": product_type
            }
            
            st.subheader("📤 JSON Payload")
            st.json(policy_data)
            
            # Try to submit to API
            try:
                response = requests.post(
                    "http://localhost:8000/submit-policy/",
                    json=policy_data,
                    headers={"Content-Type": "application/json"}
                )
                
                st.subheader("📥 API Response")
                if response.status_code == 200:
                    st.success("✅ Policy submitted successfully!")
                    st.json(response.json())
                else:
                    st.error(f"❌ Error: {response.status_code}")
                    st.text(response.text)
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API server. Make sure the FastAPI server is running on localhost:8000")
                st.info("💡 Start the server with: `uvicorn main:app --reload`")

elif page == "View Database":
    st.header("🗄️ Database Contents")
    
    try:
        import sqlite3
        import pandas as pd
        
        conn = sqlite3.connect("insurance.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM policies")
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            columns = [
                "ID", "Name", "Email", "Insurer", "Policy Number", 
                "Policy Start Date", "Policy End Date", "Date of Policy",
                "Expiry Date", "Vehicle Type", "Submitted At"
            ]
            df = pd.DataFrame(rows, columns=columns)
            st.dataframe(df, use_container_width=True)
            
            # Download option
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download as CSV", 
                data=csv, 
                file_name="policies.csv", 
                mime="text/csv"
            )
        else:
            st.info("No policies in database yet.")
            
    except Exception as e:
        st.error(f"❌ Database error: {e}")

elif page == "JSON Schema":
    st.header("📋 JSON Schema Documentation")
    
    st.subheader("Policy Submission Schema")
    
    # Display the Pydantic model schema
    schema = BikeInsurancePolicy.model_json_schema()
    st.json(schema)
    
    st.markdown("---")
    
    st.subheader("📝 Example JSON Payload")
    example_payload = {
        "name": "John Doe",
        "email": "john@example.com",
        "insurer": "ABC Insurance Company",
        "policy_number": "POL123456789",
        "policy_start_date": "2024-01-01",
        "policy_end_date": "2024-12-31",
        "date_of_policy": "2024-01-01",
        "expiry_date": "2024-12-31",
        "vehicle_type": "Bike"
    }
    st.json(example_payload)
    
    st.markdown("---")
    
    st.subheader("🔧 API Response Schema")
    response_schema = {
        "message": "Policy stored successfully"
    }
    st.json(response_schema)
    
    st.markdown("---")
    
    st.subheader("📄 Vision API + Gemini AI Output Schema")
    vision_gemini_schema = {
        "Coverton imp_keys": {
            "insuranceCompany": "string",
            "category": "string (bike/car/scooter)",
            "product": "Motor",
            "policyno": "string",
            "lastName": "string",
            "firstName": "string",
            "dob": "date or null",
            "emailId": "string",
            "phoneNo": "string",
            "lane1": "string (house number/street)",
            "lane2": "string (full address)",
            "area": "string",
            "state": "Tamil Nadu",
            "pincode": "string",
            "adharNo": "string or null",
            "panNo": "string or null",
            "remarks": "string or null",
            "subProduct": "string (bike/car/scooter)",
            "policyissuedDate": "date or null",
            "commenceMentDate": "date",
            "policyEndDate": "date",
            "sumInsuredIdv": "string",
            "grossPremium": "number or null",
            "gstPercentage": "string"
        }
    }
    st.json(vision_gemini_schema)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>InsuraWise API Documentation | Built with FastAPI & Streamlit</p>
</div>
""", unsafe_allow_html=True) 