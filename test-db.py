# test_oracle_db.py
from oracle_client import fetch_case_data

def test_fetch():
    print("=== Valid Case ===")
    print(fetch_case_data("123456"))
    print("\n=== Invalid Case ===")
    print(fetch_case_data("999999"))

if __name__ == "__main__":
    test_fetch()
