import json
import sys
import os

# Add the project directory to sys.path to allow `python src/ui_sim.py` to work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.guard_logic import check_safety
from src.config import MOCK_PATIENT_PATH

def run_clinic_sim():
    # 1. Load the Patient Context
    with open(MOCK_PATIENT_PATH, 'r') as f:
        patient = json.load(f)
    
    print(f"\n=== CLINICIAN DASHBOARD ===")
    print(f"Patient: {patient['name']} | ID: {patient['patient_id']}")
    print(f"Current Meds: {', '.join(patient['active_medications'])}")
    print(f"Known Allergies: {', '.join(patient['allergies'])}")
    print("=" * 27)

    while True:
        new_drug = input("\nEnter New Prescription (or 'q' to quit): ").strip()
        if new_drug.lower() == 'q':
            break
        
        # 2. Run the Guard Logic
        results = check_safety(new_drug, patient['active_medications'], patient['allergies'])
        
        # 3. Display Results with "Color-Coded" logic
        if not results:
            print("\033[92m[SAFE]\033[0m No known interactions found.")
        else:
            for alert in results:
                color = alert.get('color', 'gray')
                # Map internal color names to Terminal ANSI colors
                ansi_color = "\033[91m" if color == 'red' else "\033[93m" if color == 'yellow' else "\033[90m"
                
                print(f"{ansi_color}[{alert['severity'].upper()}] {alert['description']}\033[0m")

if __name__ == "__main__":
    run_clinic_sim()
