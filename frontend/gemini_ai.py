import google.generativeai as genai

# ✅ Put your actual Gemini API key here
GEMINI_API_KEY = "AIzaSyBHl3haIlj3rVLIRtfQnPuaMH0raqU6p5Y"

genai.configure(api_key=GEMINI_API_KEY)

# Set model
model = genai.GenerativeModel("models/gemini-1.5-pro")

# 🔹 1. Extract fields from raw text (PDF)
def extract_fields_from_text(pdf_text):
    prompt = f"""
    From the following insurance policy document text, extract and return only these fields in JSON format:

    {{
        "name": "",
        "insurer": "",
        "policy_number": "",
        "vehicle_type": "",
        "policy_start_date": "",
        "policy_end_date": "",
        "date_of_policy": "",
        "expiry_date": "",
        "fuel_type": "",
        "vehicle_number": ""
    }}

    --- Insurance Text Starts Below ---

    {pdf_text}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Gemini Error: {str(e)}"


# 🔹 2. Analyze a completed policy to get pros & cons
def analyze_policy_with_gemini(policy_data):
    prompt = f"""
    Analyze the following bike insurance policy and provide pros and cons.

    Policy Details:
    Name: {policy_data['name']}
    Insurer: {policy_data['insurer']}
    Policy Number: {policy_data['policy_number']}
    Start Date: {policy_data['policy_start_date']}
    End Date: {policy_data['policy_end_date']}
    Date of Policy: {policy_data['date_of_policy']}
    Expiry Date: {policy_data['expiry_date']}
    Vehicle Type: {policy_data['vehicle_type']}

    Give bullet-pointed output in this format:

    **Pros**
    - ...

    **Cons**
    - ...
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Gemini Error: {str(e)}"
def compare_with_better_policies(policy_data):
    prompt = f"""
    Compare the following bike insurance policy to better options available online.

    Policy Details:
    Name: {policy_data['name']}
    Insurer: {policy_data['insurer']}
    Policy Number: {policy_data['policy_number']}
    Start Date: {policy_data['policy_start_date']}
    End Date: {policy_data['policy_end_date']}
    Date of Policy: {policy_data['date_of_policy']}
    Expiry Date: {policy_data['expiry_date']}
    Vehicle Type: {policy_data['vehicle_type']}

    Now, do the following:
    1. Briefly summarize this policy.
    2. List 2-3 better insurance options available in India right now (real-world if possible).
    3. Explain how they are better than the current policy.
    4. Use bullet points and simple language.

    Format:
    - **Current Policy Summary**
    - **Better Option 1**: Name, Insurer, Benefits
    - **Better Option 2**: Name, Insurer, Benefits
    - **Why they are better**
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Gemini Error: {str(e)}"
