import json
import os

# Load data from JSON files
def load_json_data(filename):
    with open(os.path.join(os.path.dirname(__file__), '..', 'data', filename), 'r') as f:
        return json.load(f)

def get_charity_impact_data(charity_id):
    """
    Get impact data for a specific charity.
    """
    try:
        with open(os.path.join(DATA_DIR, 'impact_data.json'), 'r') as f:
            all_impact_data = json.load(f)
            return all_impact_data.get(str(charity_id), {})
    except FileNotFoundError:
        # Return placeholder data if file doesn't exist yet
        return {
            "charity_id": charity_id,
            "total_funds_received": 125000,
            "total_funds_utilized": 98500,
            "beneficiaries_helped": 1240,
            "projects_completed": 8,
            "ongoing_projects": 3,
            "funds_allocation": {
                "direct_aid": 65,
                "infrastructure": 20,
                "education": 10,
                "administration": 5
            },
            "monthly_impact": [
                {"month": "Jan", "beneficiaries": 120, "funds_used": 12000},
                {"month": "Feb", "beneficiaries": 150, "funds_used": 15000},
                {"month": "Mar", "beneficiaries": 180, "funds_used": 16500},
                {"month": "Apr", "beneficiaries": 200, "funds_used": 18000},
                {"month": "May", "beneficiaries": 190, "funds_used": 17000},
                {"month": "Jun", "beneficiaries": 210, "funds_used": 20000}
            ],
            "verification_status": "Verified",
            "last_audit_date": "2025-02-15"
        }

# Assume campaign['image_filename'] holds the filename like "campaign1.jpg"
def load_local_image(image_filename):
    # Construct the local image path
    image_path = os.path.join(os.path.dirname(__file__), "..", "assets", "images", image_filename)
    # If the file doesn't exist, return the default image path
    if not os.path.exists(image_path):
        default_image = os.path.join(os.path.dirname(__file__), "..", "assets", "images", "na.jpg")
        print(f"Image not found: {image_path}. Using default: {default_image}")
        return default_image
        
    print(f"Loading image from: {image_path}")  # For debugging
    return image_path

def get_transaction_history(charity_id):
    """
    Get transaction history for a specific charity.
    """
    try:
        with open(os.path.join(DATA_DIR, 'transactions.json'), 'r') as f:
            all_transactions = json.load(f)
            return all_transactions.get(str(charity_id), [])
    except FileNotFoundError:
        # Return placeholder data if file doesn't exist yet
        return [
            {"date": "2025-03-15", "transaction_id": "0.0.1234567", "amount": 5000, "purpose": "Education program", "status": "Completed"},
            {"date": "2025-03-10", "transaction_id": "0.0.1234566", "amount": 7500, "purpose": "Food distribution", "status": "Completed"},
            {"date": "2025-03-05", "transaction_id": "0.0.1234565", "amount": 10000, "purpose": "Medical supplies", "status": "In progress"},
            {"date": "2025-02-28", "transaction_id": "0.0.1234564", "amount": 15000, "purpose": "Infrastructure", "status": "Completed"},
            {"date": "2025-02-20", "transaction_id": "0.0.1234563", "amount": 8000, "purpose": "Emergency relief", "status": "Completed"}
        ]

def get_verified_metrics(charity_id):
    """
    Get blockchain-verified metrics for a specific charity.
    """
    try:
        with open(os.path.join(DATA_DIR, 'verification_data.json'), 'r') as f:
            all_verification_data = json.load(f)
            return all_verification_data.get(str(charity_id), {})
    except FileNotFoundError:
        # Return placeholder data if file doesn't exist yet
        return {
            "verification_proof": "0x8f7d56a12e8f4dba9bc947c098562c25a7d24e4973168c5152a444d99e671877",
            "impact_score": 87,
            "transparency_rating": 92,
            "fund_utilization_efficiency": 89,
            "beneficiary_satisfaction": 85,
            "sustainable_development_goals": ["No Poverty", "Zero Hunger", "Quality Education"]
        }

# Mock function for Hedera integration - would be replaced with actual SDK calls
def verify_on_hedera(charity_id, report_id):
    """
    Simulate verification on Hedera network.
    In production, this would use the Hedera SDK to verify data on the ledger.
    """
    return {
        "success": True,
        "timestamp": "2025-03-23T14:25:30Z",
        "consensus_node": "0.0.3",
        "topic_id": "0.0.12345"
    }