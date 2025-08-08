from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from models import BikeInsurancePolicy
import sqlite3
from datetime import datetime
from vision_gemini_processor import process_insurance_document
import json
from enum import Enum

app = FastAPI(
    title="InsuraWise Insurance API",
    description="Insurance policy management with PDF processing using Google Cloud Vision API and Gemini AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Product type enum for dropdown
class ProductType(str, Enum):
    car = "CAR"
    bike = "BIKE"
    health = "HEALTH"

# Initialize DB on first run
def init_db():
    conn = sqlite3.connect("insurance.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            insurer TEXT,
            policy_number TEXT,
            policy_start_date TEXT,
            policy_end_date TEXT,
            date_of_policy TEXT,
            expiry_date TEXT,
            vehicle_type TEXT,
            submitted_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.post("/submit-policy/")
def submit_policy(policy: BikeInsurancePolicy):
    conn = sqlite3.connect("insurance.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO policies (
            name, email, insurer, policy_number, policy_start_date,
            policy_end_date, date_of_policy, expiry_date,
            vehicle_type, submitted_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        policy.name,
        policy.email,
        policy.insurer,
        policy.policy_number,
        policy.policy_start_date,
        policy.policy_end_date,
        policy.date_of_policy,
        policy.expiry_date,
        policy.vehicle_type,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return {"message": "Policy stored successfully"}

@app.post("/process-pdf/")
async def process_pdf(
    pdf_file: UploadFile = File(..., description="Upload insurance PDF document"),
    product_type: ProductType = Form(..., description="Select product type")
):
    """
    Process insurance PDF with Google Cloud Vision API and Gemini AI
    
    - **pdf_file**: Upload your insurance policy PDF
    - **product_type**: Select product type (CAR, BIKE, or HEALTH)
    
    Returns JSON in specified format based on product type
    """
    try:
        # Validate file type
        if not pdf_file.filename.lower().endswith('.pdf'):
            return JSONResponse(
                status_code=400,
                content={"error": "File must be a PDF"}
            )
        
        # Convert product type to insurance type and vehicle type for processing logic
        if product_type.value in ["CAR", "BIKE"]:
            insurance_type_lower = "vehicle"
            vehicle_type_lower = product_type.value.lower()
        elif product_type.value == "HEALTH":
            insurance_type_lower = "medical"
            vehicle_type_lower = None
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid product type"}
            )
        
        # Process the PDF
        result = await process_insurance_document(pdf_file, product_type.value, vehicle_type_lower)
        
        if isinstance(result, dict) and ("Coverton imp_keys" in result or "medical_insurance" in result):
            return JSONResponse(
                status_code=200,
                content={
                    "message": "PDF processed successfully",
                    "data": result,
                    "product_type": product_type.value,
                    "insurance_type": insurance_type_lower,
                    "vehicle_type": vehicle_type_lower
                }
            )
        elif isinstance(result, str) and result.startswith("⚠️"):
            return JSONResponse(
                status_code=500,
                content={"error": result}
            )
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to process PDF", "details": result}
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )

@app.get("/")
def read_root():
    return {
        "message": "InsuraWise Insurance API",
        "endpoints": {
            "submit_policy": "/submit-policy/",
            "process_pdf": "/process-pdf/",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "features": [
            "PDF processing with Google Cloud Vision API",
            "Field classification with Gemini AI",
            "Product type selection (CAR/BIKE/HEALTH)",
            "Vehicle insurance for CAR and BIKE",
            "Medical insurance for HEALTH",
            "JSON output in specified formats"
        ]
    }

