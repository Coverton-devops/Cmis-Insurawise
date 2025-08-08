import google.generativeai as genai
from google.cloud import vision
import fitz  # PyMuPDF for PDF processing
import base64
import json
import io
from PIL import Image
import os
from google.cloud import vision_v1
from google.cloud.vision_v1 import ImageAnnotatorClient
from google.api_core import client_options
from dotenv import load_dotenv
from models import CovertonImpKeys, MedicalInsuranceResponse

# Load environment variables from .env file
load_dotenv()

# API Keys from environment variables (secure)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_CLOUD_VISION_API_KEY = os.getenv("GOOGLE_CLOUD_VISION_API_KEY")

# Validate API keys are loaded
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
if not GOOGLE_CLOUD_VISION_API_KEY:
    raise ValueError("GOOGLE_CLOUD_VISION_API_KEY not found in environment variables. Please check your .env file.")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-pro")

async def extract_text_from_pdf_with_vision(pdf_file, insurance_type, vehicle_type=None):
    """
    Extract text from PDF using Google Cloud Vision API
    """
    try:
        # Read PDF file content
        pdf_content = await pdf_file.read()
        
        # Open PDF with PyMuPDF
        pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
        
        # Initialize Vision API client with API key
        client_options_obj = client_options.ClientOptions(
            api_key=GOOGLE_CLOUD_VISION_API_KEY
        )
        client = ImageAnnotatorClient(client_options=client_options_obj)
        
        all_text = []
        
        # Process each page
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            
            # Convert PDF page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Higher resolution
            img_data = pix.tobytes("png")
            
            # Create image object for Vision API
            image = vision_v1.Image(content=img_data)
            
            # Perform text detection
            response = client.text_detection(image=image)
            texts = response.text_annotations
            
            if texts:
                # Extract text from the first annotation (contains all text)
                page_text = texts[0].description
                all_text.append(page_text)
            
            if response.error.message:
                raise Exception(f"Vision API Error: {response.error.message}")
        
        pdf_document.close()
        
        # Combine all text
        full_text = "\n".join(all_text)
        
        # Process with Gemini AI for field classification based on insurance type
        if insurance_type == "vehicle":
            return classify_vehicle_fields_with_gemini(full_text, vehicle_type)
        elif insurance_type == "medical":
            return classify_medical_fields_with_gemini(full_text)
        else:
            return f"⚠️ Error: Invalid insurance type: {insurance_type}"
        
    except Exception as e:
        return f"⚠️ Error processing PDF: {str(e)}"

def classify_vehicle_fields_with_gemini(extracted_text, vehicle_type):
    """
    Use Gemini AI to classify vehicle insurance fields and return JSON in specified format
    """
    prompt = f"""
    You are an expert vehicle insurance document analyzer. Extract information from the following insurance document text and return it in the exact JSON format specified below.

    Vehicle Type Selected: {vehicle_type}

    IMPORTANT: Return ONLY the JSON object, no additional text or explanations.

    CRITICAL DATE FORMAT RULE: All dates MUST be in "dd-mm-yyyy" format (e.g., "15-03-2024", "01-12-2023")

    JSON Format:
    {{
        "Coverton imp_keys": {{
            "insuranceCompany": "",
            "category": "{vehicle_type}",
            "product": "Motor",
            "policyno": "",
            "lastName": "",
            "firstName": "",
            "dob": "",
            "emailId": "",
            "phoneNo": "",
            "lane1": "",
            "lane2": "",
            "area": "",
            "state": "Tamil Nadu",
            "pincode": "",
            "adharNo": null,
            "panNo": null,
            "remarks": null,
            "subProduct": "{vehicle_type}",
            "policyissuedDate": "",
            "commenceMentDate": "",
            "policyEndDate": "",
            "sumInsuredIdv": "",
            "grossPremium": null,
            "gstPercentage": "",
            "plan": ""
        }}
    }}

    Instructions:
    1. Extract customer information for: lastName, firstName, dob, emailId, phoneNo, lane1, lane2, area, pincode, adharNo, panNo
    2. Extract policy information for: insuranceCompany, policyno, policyissuedDate, commenceMentDate, policyEndDate, sumInsuredIdv, grossPremium, gstPercentage
    3. Set category and subProduct to the selected vehicle type
    4. Split address into lane1 and lane2 (lane1 for house number/street, lane2 for full address)
    5. Extract area and pincode from the address
    6. Set state to "Tamil Nadu" as default
    7. Set product to "Motor"
    8. Leave fields as empty string if not found in document
    9. ALL DATES MUST BE IN "dd-mm-yyyy" FORMAT (e.g., "15-03-2024", "01-12-2023")
    10. Extract plan information: Look for text containing "policy", "schedule", or "policy schedule" - usually found in headers or top sections of the document

    CRITICAL PHONE NUMBER EXTRACTION RULES:
    - Look for phone numbers in formats: 10-digit, 11-digit, or 12-digit numbers
    - Search for keywords: "phone", "mobile", "cell", "cellno", "contact", "tel", "telephone"
    - Extract any number that appears to be a contact number
    - If multiple numbers found, use the most likely customer contact number
    - Phone number should NOT be null - if not found, use empty string ""
    - Common patterns: 9XXXXXXXXX, 8XXXXXXXXX, 7XXXXXXXXX, 6XXXXXXXXX
    - Remove any spaces, dashes, or special characters from phone numbers

    CRITICAL NAME EXTRACTION RULES:
    - Extract ANY name found in the document - customer name, insured name, policy holder name, etc.
    - Look for keywords: "name", "insured", "customer", "policy holder", "applicant"
    - If multiple names found, use the most relevant customer name
    - Name fields should NEVER be null - if not found, use empty string ""
    - Extract full names as they appear in the document
    - Handle various formats: "Insured Name", "Customer Name", "Policy Holder", etc.

    Document Text:
    {extracted_text}
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up the response to ensure it's valid JSON
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse JSON to validate
        parsed_json = json.loads(response_text)
        
        # Ensure phoneNo is not null - if it is, set to empty string
        if parsed_json.get("Coverton imp_keys", {}).get("phoneNo") is None:
            parsed_json["Coverton imp_keys"]["phoneNo"] = ""
        
        # Ensure name fields are not null
        if parsed_json.get("Coverton imp_keys", {}).get("firstName") is None:
            parsed_json["Coverton imp_keys"]["firstName"] = ""
        if parsed_json.get("Coverton imp_keys", {}).get("lastName") is None:
            parsed_json["Coverton imp_keys"]["lastName"] = ""
        
        # Format all dates to dd-mm-yyyy format
        parsed_json = format_dates_in_vehicle_json(parsed_json)
        
        # Validate with Pydantic model (without affecting existing logic)
        try:
            validated_data = CovertonImpKeys(**parsed_json)
            return validated_data.model_dump()
        except Exception as validation_error:
            # If validation fails, return original data (maintain existing behavior)
            print(f"Validation warning: {validation_error}")
            return parsed_json
        
    except json.JSONDecodeError as e:
        return f"⚠️ JSON parsing error: {str(e)}"
    except Exception as e:
        return f"⚠️ Gemini AI error: {str(e)}"

def classify_medical_fields_with_gemini(extracted_text):
    """
    Use Gemini AI to classify medical insurance fields and return JSON in specified format
    """
    prompt = f"""
    You are an expert medical insurance document analyzer. Extract information from the following insurance document text and return it in the exact JSON format specified below.

    IMPORTANT: Return ONLY the JSON object, no additional text or explanations.

    CRITICAL DATE FORMAT RULE: All dates MUST be in "dd-mm-yyyy" format (e.g., "15-03-2024", "01-12-2023")

         CRITICAL EXTRACTION RULES:
     1. Extract ALL possible information from the document - leave NO field empty unless absolutely not found
     2. For tables, extract each column as a separate field with its corresponding values
     3. Look for information in ALL sections of the document - headers, footers, sidebars, etc.
     4. Extract amounts, percentages, dates, names, addresses, contact information wherever found
     5. For amounts, include currency symbols and commas as they appear
     6. For dates, use "dd-mm-yyyy" format (e.g., "15-03-2024", "01-12-2023")
     7. For addresses, extract complete address including street, city, state, pincode, and area/locality
     8. For contact information, extract phone numbers, emails, fax numbers
     9. For policy numbers and IDs, extract exact alphanumeric values
     10. For names, extract full names as they appear
     11. For tables, extract each row's data into separate field entries
           12. For addresses, ALWAYS extract the area/locality part (e.g., "MYLAPORE" from "ROYAPETTAH HIGH ROAD, MYLAPORE, CHENNAI")
      13. For plan information: Look for text containing "policy", "schedule", or "policy schedule" - usually found in headers or top sections of the document

    CRITICAL NAME EXTRACTION RULES:
    - Extract ANY name found in the document - insured name, member name, nominee name, etc.
    - Look for keywords: "name", "insured", "member", "nominee", "policy holder", "applicant"
    - Name fields should NEVER be null - if not found, use empty string ""
    - Extract full names as they appear in the document
    - Handle various formats: "Insured Name", "Member Name", "Nominee Name", etc.
    - For multiple names, use the most relevant one for each field

    JSON Format:
    {{
        "medical_insurance": {{
            "gross_premium_and_stamp_duty": {{
                "gross_premium": "",
                "stamp_duty": ""
            }},
            "risk_details": {{
                "emp_dependant_name": "",
                "si_no": "",
                "no_of_dependants": ""
            }},
            "installment_details": {{
                "inst_no": "",
                "installment_percentage": "",
                "amount": "",
                "tax": "",
                "total": "",
                "remarks": ""
            }},
            "endorsement_schedule_details": {{
                "endorsement_no": "",
                "endorsement_date": ""
            }},
            "agent_broker_details": {{
                "agent_broker": "",
                "address": ""
            }},
            "sales_channel_details": {{
                "sales_channel_code": "",
                "name": ""
            }},
            "generic_information": {{
                "company_name": "",
                "insured_name": "",
                "insured_address": "",
                "plan_type": "",
                "endorsement_schedule": ""
            }},
                         "individual_member_details": {{
                 "member_1": {{
                     "sl_no": "",
                     "name": "",
                     "dob_and_age": "",
                     "relation": "",
                     "occupation": "",
                     "gender": "",
                     "basic_cover_sum_insured": "",
                     "cumulative_bonus": ""
                 }},
                 "member_2": {{
                     "sl_no": "",
                     "name": "",
                     "dob_and_age": "",
                     "relation": "",
                     "occupation": "",
                     "gender": "",
                     "basic_cover_sum_insured": "",
                     "cumulative_bonus": ""
                 }},
                 "member_3": {{
                     "sl_no": "",
                     "name": "",
                     "dob_and_age": "",
                     "relation": "",
                     "occupation": "",
                     "gender": "",
                     "basic_cover_sum_insured": "",
                     "cumulative_bonus": ""
                 }}
             }},
            "nominee_details": {{
                "name": "",
                "relationship_with_insured": ""
            }},
            "optional_copayment_details": {{
                "co_payment_percentage": ""
            }},
            "amount_details": {{
                "premium": "",
                "total_premium": "",
                "cgst": "",
                "sgst_utgst": "",
                "igst": "",
                "gst_tds": "",
                "recoverable_stamp_duty": "",
                "total_amount": ""
            }},
            "insurer_details": {{
                "insured": "",
                "issue_office_name": "",
                "address": "",
                "tel_fax_email": "",
                "gstin": "",
                "agent_no": ""
            }},
            "policy_details": {{
                "policy_name_schedule": "",
                "policy_no": "",
                "previous_policy_no": "",
                "period_of_insurance": "",
                "date_of_insurance": "",
                "start_date": "",
                "end_date": "",
                "unique_invoice_no": ""
            }},
            "member_details": {{
                "total_members_covered": "",
                "total_self_covered": "",
                "total_dependent_covered": ""
            }},
            "co_insurance_details": {{
                "insurance_company": "",
                "share_percentage": ""
            }},
            "premium_details": {{
                "net_premium": "",
                "gross_premium": ""
            }},
            "gst_details": {{
                "cgst": "",
                "sgst": "",
                "ugst": "",
                "igst": ""
            }},
            "tpa_details": {{
                "tpa_id": "",
                "tpa_name": "",
                "tpa_address": "",
                "telephone_no": "",
                "entity": "",
                "email": ""
            }},
            "policy_conditions_extensions_endorsements": {{
                "condition_name": "",
                "description": "",
                "coverage_amount": "",
                "terms": ""
            }},
            "third_party_details": {{
                "third_party_administrator": ""
            }},
            "intermediary_agent_details": {{
                "name": "",
                "contact_no": "",
                "email": "",
                "health_id_cards": "",
                "industry_type": ""
            }},
            "intermediary_details": {{
                "intermediary_name": "",
                "code": "",
                "contact_number": ""
            }},
            "other_insured_person_details": {{
                "name": "",
                "dob": "",
                "base_sum_insured": "",
                "aggregate_deductible": "",
                "unlimited_restored_addon": ""
            }},
            "premium_details_all": {{
                "member_name": "",
                "relation": "",
                "age": "",
                "sum_insured": "",
                "premium_amount": "",
                "gst_amount": "",
                "total_amount": ""
            }},
            "insured_person_premium_details": {{
                "name": "",
                "relation": "",
                "gender": "",
                "dob": "",
                "premium": "",
                "gst": "",
                "total_with_gst": "",
                "abha_id": ""
            }},
            "schedule_of_benefits": {{
                "benefit_name": "",
                "description": "",
                "coverage_amount": "",
                "terms_conditions": "",
                "exclusions": ""
            }},
            "policy_holder_policy_details": {{
                "policy_holder_name": "",
                "policy_number": "",
                "start_date": "",
                "end_date": "",
                "premium_amount": "",
                "coverage_details": ""
            }}
        }}
    }}

    SPECIFIC EXTRACTION INSTRUCTIONS:
    1. Look for "Gross Premium" and "Stamp Duty" amounts in premium sections
    2. Find "Risk Details" or "Employee/Dependant" information
    3. Extract "Installment Details" with installment numbers, percentages, amounts, taxes
    4. Look for "Endorsement Schedule" with endorsement numbers and dates
    5. Find "Agent/Broker" information with names and addresses
    6. Extract "Sales Channel" details with codes and names
         7. Get "Generic Information" including company name, insured name, address, plan type - for plan_type, look for text containing "policy", "schedule", or "policy schedule" in headers or top sections
         8. Look for "Individual Member Details" with names, DOB, relations, occupations - populate member_1, member_2, member_3 based on the order found in document
    9. Find "Nominee Details" with names and relationships
    10. Extract "Optional Copayment" percentages
    11. Get "Amount Details" including premium, total premium, CGST, SGST, IGST, GST TDS
    12. Find "Insurer Details" with insured name, office name, address, contact info, GSTIN
    13. Extract "Policy Details" with policy name, number, dates, invoice number
    14. Get "Member Details" with total members, self covered, dependent covered
    15. Find "Co-Insurance Details" with company names and share percentages
    16. Extract "Premium Details" with net and gross premium
    17. Get "GST Details" with CGST, SGST, UGST, IGST amounts
    18. Find "TPA Details" with TPA ID, name, address, contact info
    19. For "Policy Conditions/Extensions/Endorsements" - extract each condition as separate fields
    20. Find "Third Party Details" with administrator information
    21. Extract "Intermediary/Agent Details" with names, contacts, health ID cards
    22. Get "Intermediary Details" with names, codes, contact numbers
    23. Find "Other Insured Person Details" with names, DOB, sum insured, deductibles
    24. For "Premium Details (All)" - extract each member's details as separate fields
    25. Get "Insured Person Premium Details" with names, relations, gender, DOB, premium, GST
    26. For "SCHEDULE OF BENEFITS" - extract each benefit as separate fields
    27. For "Policy Holder Policy Details" - extract each policy detail as separate fields

         TABLE EXTRACTION RULES:
     - For any table in the document, extract each column as a separate field
     - Map table headers to corresponding JSON field names
     - Extract data from each row and populate the appropriate fields
     - For multiple rows, use the most relevant or first row data
     - Include all table data by mapping columns to fields
     - For complex tables, extract the most important information into the specified fields
     
     INDIVIDUAL MEMBER DETAILS STRUCTURE:
     - Extract member details from tables or lists in the document
     - Populate member_1, member_2, member_3 based on the order found
     - If only one member found, populate member_1 only
     - If two members found, populate member_1 and member_2
     - If three or more members found, populate all three slots
     - Each member should have complete details: sl_no, name, dob_and_age, relation, occupation, gender, basic_cover_sum_insured, cumulative_bonus
     - Keep the structured format for better readability

    Document Text:
    {extracted_text}
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up the response to ensure it's valid JSON
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse JSON to validate
        parsed_json = json.loads(response_text)
        
        # Ensure name fields are not null in medical insurance
        medical_data = parsed_json.get("medical_insurance", {})
        
        # Check and fix name fields in various sections
        name_fields_to_check = [
            "emp_dependant_name", "agent_broker", "name", "insured_name", 
            "name", "nominee_details.name", "insured", "tpa_name", 
            "condition_name", "third_party_administrator", "name", 
            "intermediary_name", "name", "member_name", "name", 
            "benefit_name", "policy_holder_name"
        ]
        
        # Helper function to safely set nested field
        def set_nested_field(data, field_path, default_value=""):
            if field_path in data:
                if data[field_path] is None:
                    data[field_path] = default_value
            elif "." in field_path:
                parts = field_path.split(".")
                if parts[0] in data and isinstance(data[parts[0]], dict):
                    if data[parts[0]].get(parts[1]) is None:
                        data[parts[0]][parts[1]] = default_value
        
        # Fix name fields in medical insurance
        for field in name_fields_to_check:
            set_nested_field(medical_data, field, "")
        
        # Format all dates to dd-mm-yyyy format
        parsed_json = format_dates_in_medical_json(parsed_json)
        
        # Add extra Coverton imp_keys section for health insurance
        extra_coverton_section = extract_coverton_fields_from_medical(parsed_json)
        if extra_coverton_section:
            parsed_json["Coverton imp_keys"] = extra_coverton_section
        
        # Validate with Pydantic model (without affecting existing logic)
        try:
            validated_data = MedicalInsuranceResponse(**parsed_json)
            return validated_data.model_dump()
        except Exception as validation_error:
            # If validation fails, return original data (maintain existing behavior)
            print(f"Validation warning: {validation_error}")
            return parsed_json
        
    except json.JSONDecodeError as e:
        return f"⚠️ JSON parsing error: {str(e)}"
    except Exception as e:
        return f"⚠️ Gemini AI error: {str(e)}"

async def process_insurance_document(pdf_file, product_type, vehicle_type=None):
    """
    Main function to process insurance document
    """
    # Convert product type to insurance type and vehicle type
    if product_type in ["CAR", "BIKE"]:
        insurance_type = "vehicle"
        vehicle_type = product_type.lower()
    elif product_type == "HEALTH":
        insurance_type = "medical"
        vehicle_type = None
    else:
        return {"error": "Invalid product type. Must be CAR, BIKE, or HEALTH."}
    
    if insurance_type == "vehicle":
        if vehicle_type not in ["bike", "car"]:
            return {"error": "Invalid vehicle type. Must be bike or car."}
        return await extract_text_from_pdf_with_vision(pdf_file, insurance_type, vehicle_type)
    elif insurance_type == "medical":
        return await extract_text_from_pdf_with_vision(pdf_file, insurance_type)
    else:
        return {"error": "Invalid insurance type. Must be vehicle or medical."}

def format_dates_in_vehicle_json(data):
    """
    Format all dates in vehicle insurance JSON to dd-mm-yyyy format
    """
    import re
    from datetime import datetime
    
    def format_date(date_str):
        if not date_str or date_str == "":
            return ""
        
        # Try to parse various date formats and convert to dd-mm-yyyy
        date_formats = [
            "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", 
            "%Y/%m/%d", "%d.%m.%Y", "%m.%d.%Y", "%d %m %Y",
            "%d-%m-%y", "%d/%m/%y", "%Y-%m-%d %H:%M:%S"
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(str(date_str).strip(), fmt)
                return parsed_date.strftime("%d-%m-%Y")
            except ValueError:
                continue
        
        # If no format matches, return original
        return str(date_str)
    
    if "Coverton imp_keys" in data:
        vehicle_data = data["Coverton imp_keys"]
        
        # Format all date fields
        date_fields = ["dob", "policyissuedDate", "commenceMentDate", "policyEndDate"]
        
        for field in date_fields:
            if field in vehicle_data and vehicle_data[field]:
                vehicle_data[field] = format_date(vehicle_data[field])
    
        return data 

def extract_coverton_fields_from_medical(medical_data):
    """
    Extract Coverton imp_keys fields from medical insurance data
    """
    try:
        medical_insurance = medical_data.get("medical_insurance", {})
        
        # Extract relevant fields from medical insurance data
        coverton_fields = {
            "insuranceCompany": medical_insurance.get("generic_information", {}).get("company_name", ""),
            "category": "Health",
            "product": "Health",
            "policyno": medical_insurance.get("policy_details", {}).get("policy_no", ""),
            "lastName": "",
            "firstName": medical_insurance.get("generic_information", {}).get("insured_name", ""),
            "dob": "",
            "emailId": "",
            "phoneNo": "",
            "lane1": "",
            "lane2": medical_insurance.get("generic_information", {}).get("insured_address", ""),
            "area": "",
            "state": "Tamil Nadu",
            "pincode": "",
            "adharNo": None,
            "panNo": None,
            "remarks": None,
            "subProduct": "Health",
            "policyissuedDate": medical_insurance.get("policy_details", {}).get("date_of_insurance", ""),
            "commenceMentDate": medical_insurance.get("policy_details", {}).get("start_date", ""),
            "policyEndDate": medical_insurance.get("policy_details", {}).get("end_date", ""),
            "sumInsuredIdv": "",
            "grossPremium": medical_insurance.get("amount_details", {}).get("total_premium", ""),
            "gstPercentage": "",
            "plan": medical_insurance.get("generic_information", {}).get("plan_type", "")
        }
        
        # Extract name from insured_name if available
        insured_name = medical_insurance.get("generic_information", {}).get("insured_name", "")
        if insured_name:
            name_parts = insured_name.split()
            if len(name_parts) >= 2:
                coverton_fields["lastName"] = name_parts[-1]
                coverton_fields["firstName"] = " ".join(name_parts[:-1])
            else:
                coverton_fields["firstName"] = insured_name
        
        # Extract phone number from various sections
        phone_sources = [
            medical_insurance.get("insurer_details", {}).get("tel_fax_email", ""),
            medical_insurance.get("tpa_details", {}).get("telephone_no", ""),
            medical_insurance.get("intermediary_details", {}).get("contact_number", "")
        ]
        
        for phone_source in phone_sources:
            if phone_source and any(char.isdigit() for char in phone_source):
                # Extract digits only
                digits = ''.join(filter(str.isdigit, phone_source))
                if len(digits) >= 10:
                    coverton_fields["phoneNo"] = digits[:10]
                    break
        
        # Extract email from various sections
        email_sources = [
            medical_insurance.get("insurer_details", {}).get("tel_fax_email", ""),
            medical_insurance.get("tpa_details", {}).get("email", ""),
            medical_insurance.get("intermediary_agent_details", {}).get("email", "")
        ]
        
        for email_source in email_sources:
            if email_source and "@" in email_source:
                coverton_fields["emailId"] = email_source
                break
        
        # Extract address components
        address = medical_insurance.get("generic_information", {}).get("insured_address", "")
        if address:
            # Try to extract pincode (6 digits)
            import re
            pincode_match = re.search(r'\b\d{6}\b', address)
            if pincode_match:
                coverton_fields["pincode"] = pincode_match.group()
            
            # Split address into lane1 and lane2
            address_lines = address.split(',')
            if len(address_lines) >= 2:
                coverton_fields["lane1"] = address_lines[0].strip()
                coverton_fields["lane2"] = address
            else:
                coverton_fields["lane2"] = address
            
            # Extract area from address (usually the second-to-last part before city)
            address_parts = [part.strip() for part in address.split(',')]
            if len(address_parts) >= 3:
                # Look for area in the middle parts of the address
                for i in range(1, len(address_parts) - 1):
                    part = address_parts[i]
                    # Skip if it's a road name or contains numbers
                    if not any(char.isdigit() for char in part) and not any(road_word in part.upper() for road_word in ['ROAD', 'STREET', 'AVENUE', 'LANE', 'DRIVE']):
                        coverton_fields["area"] = part
                        break
                # If no area found in middle parts, try the second part
                if not coverton_fields["area"] and len(address_parts) >= 2:
                    coverton_fields["area"] = address_parts[1]
            elif len(address_parts) >= 2:
                coverton_fields["area"] = address_parts[1]
        
        # Extract sum insured from various sources
        sum_insured_sources = [
            medical_insurance.get("individual_member_details", {}).get("basic_cover_sum_insured", ""),
            medical_insurance.get("other_insured_person_details", {}).get("base_sum_insured", ""),
            medical_insurance.get("premium_details_all", {}).get("sum_insured", "")
        ]
        
        for sum_source in sum_insured_sources:
            if sum_source:
                coverton_fields["sumInsuredIdv"] = sum_source
                break
        
        # Extract GST percentage
        gst_sources = [
            medical_insurance.get("gst_details", {}).get("cgst", ""),
            medical_insurance.get("gst_details", {}).get("sgst", ""),
            medical_insurance.get("gst_details", {}).get("igst", "")
        ]
        
        for gst_source in gst_sources:
            if gst_source and gst_source.replace('.', '').isdigit():
                # Calculate GST percentage (assuming 18% total GST)
                try:
                    gst_amount = float(gst_source)
                    premium_amount = float(coverton_fields["grossPremium"]) if coverton_fields["grossPremium"] else 0
                    if premium_amount > 0:
                        gst_percentage = (gst_amount / premium_amount) * 100
                        coverton_fields["gstPercentage"] = str(int(gst_percentage))
                    else:
                        coverton_fields["gstPercentage"] = "18"
                except:
                    coverton_fields["gstPercentage"] = "18"
                break
        
        return coverton_fields
        
    except Exception as e:
        print(f"Error extracting Coverton fields: {e}")
        return None
def format_dates_in_medical_json(data):
    """
    Format all dates in medical insurance JSON to dd-mm-yyyy format
    """
    import re
    from datetime import datetime
    
    def format_date(date_str):
        if not date_str or date_str == "":
            return ""
        
        # Try to parse various date formats and convert to dd-mm-yyyy
        date_formats = [
            "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", 
            "%Y/%m/%d", "%d.%m.%Y", "%m.%d.%Y", "%d %m %Y",
            "%d-%m-%y", "%d/%m/%y", "%Y-%m-%d %H:%M:%S"
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(str(date_str).strip(), fmt)
                return parsed_date.strftime("%d-%m-%Y")
            except ValueError:
                continue
        
        # If no format matches, return original
        return str(date_str)
    
    if "medical_insurance" in data:
        medical_data = data["medical_insurance"]
        
        # Format dates in all nested objects
        sections_to_format = [
            "endorsement_schedule_details",
            "policy_details",
            "individual_member_details",
            "other_insured_person_details",
            "insured_person_premium_details",
            "policy_holder_policy_details"
        ]
        
        for section in sections_to_format:
            if section in medical_data and isinstance(medical_data[section], dict):
                section_data = medical_data[section]
                
                # Define date fields for each section
                date_fields_map = {
                    "endorsement_schedule_details": ["endorsement_date"],
                    "policy_details": ["date_of_insurance", "start_date", "end_date"],
                    "individual_member_details": ["dob_and_age"],
                    "other_insured_person_details": ["dob"],
                    "insured_person_premium_details": ["dob"],
                    "policy_holder_policy_details": ["start_date", "end_date"]
                }
                
                date_fields = date_fields_map.get(section, [])
                for field in date_fields:
                    if field in section_data and section_data[field]:
                        section_data[field] = format_date(section_data[field])
                
                # Special handling for individual_member_details structured format
                if section == "individual_member_details":
                    for member_key in ["member_1", "member_2", "member_3"]:
                        if member_key in section_data and isinstance(section_data[member_key], dict):
                            member_data = section_data[member_key]
                            if "dob_and_age" in member_data and member_data["dob_and_age"]:
                                member_data["dob_and_age"] = format_date(member_data["dob_and_age"])
    
    return data 