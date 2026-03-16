import requests
import json
import base64
import os

# Configuration
RPC_URL = "http://localhost:3030"  # local validator RPC
ACCOUNTS_FILE = "accounts.txt"
OUTPUT_DIR = "contracts"

def get_contract_code(account_id):
    """Fetches base64 encoded Wasm for a given account ID."""
    payload = {
        "jsonrpc": "2.0",
        "id": "dontcare",
        "method": "query",
        "params": {
            "request_type": "view_code",
            "finality": "final",
            "account_id": account_id
        }
    }
    try:
        response = requests.post(RPC_URL, json=payload).json()
        if "result" in response and "code_base64" in response["result"]:
            # Code is returned as base64 encoded Wasm binary
            return response["result"]["code_base64"]
    except Exception as e:
        print(f"Error querying {account_id}: {e}")
    return None

def main():
    # 1. Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")

    # 2. Read accounts and process each
    if not os.path.exists(ACCOUNTS_FILE):
        print(f"Error: {ACCOUNTS_FILE} not found.")
        return

    with open(ACCOUNTS_FILE, "r") as f:
        # Filter out empty lines and whitespace
        accounts = [line.strip() for line in f if line.strip()]

    print(f"Starting dump for {len(accounts)} accounts...")

    for account in accounts:
        code_b64 = get_contract_code(account)
        
        if code_b64:
            # If code exists, it's a binary blob; decode and save
            wasm_bytes = base64.b64decode(code_b64)
            output_path = os.path.join(OUTPUT_DIR, f"{account}.wasm")
            
            with open(output_path, "wb") as wasm_file:
                wasm_file.write(wasm_bytes)
            print(f"✓ Saved: {output_path}")
        else:
            print(f"✗ No contract found for: {account}")

    print("\nProcessing complete.")


if __name__ == "__main__":
    main()
