# I failed to make this work, this should have been faster than requesting the contracts from local RPC

#!/bin/bash

# Configuration
SHARD_ID=0                 # Change to your target shard
HOME_DIR="$HOME/.near"      # Path to your validator data
OUTPUT_DIR="./shard_wasms/${SHARD_ID}"

mkdir -p "$OUTPUT_DIR"

echo "Starting bulk extraction from Shard $SHARD_ID..."

# 1. Stream the state dump
# 2. Filter for records containing code
# 3. Extract account_id and code_base64
# 4. Decode and save
~/neard --home "$HOME_DIR" view-state dump-state  --stream | \
jq -c 'select(.code_base64 != null)' | while read -r line; do
    
    ACCOUNT=$(echo "$line" | jq -r '.account_id')
    
    # Standardize filename (handle subaccounts like 'app.near')
    FILENAME="${OUTPUT_DIR}/${ACCOUNT}.wasm"
    
    # Decode the base64 string into a binary wasm file
    echo "$line" | jq -r '.code_base64' | base64 -d > "$FILENAME"
    
    echo "Extracted: $ACCOUNT"
done

echo "Done. All contracts are in $OUTPUT_DIR"
