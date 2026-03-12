import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.guard_logic import check_safety

def test():
    print("Testing Allergy...")
    res = check_safety("Penicillin", ["Aspirin"], ["Penicillin"])
    print(f"Results: {res}")
    
    print("\nTesting Unknown...")
    res = check_safety("Tylenol", ["Aspirin"], ["Penicillin"])
    print(f"Results: {res}")

if __name__ == "__main__":
    test()
