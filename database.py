import sqlite3
from models import BikeInsurancePolicy

def save_policy(policy: BikeInsurancePolicy):
    # Connect to the database (creates it if not already there)
    conn = sqlite3.connect("insurance.db")
    cursor = conn.cursor()

    # Create table if it doesn't exist (now includes email + submitted_at)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS policies (
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
    ''')

    # Insert the new policy data, including submitted_at
    cursor.execute('''
        INSERT INTO policies VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        policy.name,
        policy.email,
        policy.insurer,
        policy.policy_number,
        policy.policy_start_date.isoformat(),
        policy.policy_end_date.isoformat(),
        policy.date_of_policy.isoformat(),
        policy.expiry_date.isoformat(),
        policy.vehicle_type,
        policy.submitted_at  # already in "July 9, 2025 at 06:45 PM" format
    ))

    # Save and close the connection
    conn.commit()
    conn.close()
