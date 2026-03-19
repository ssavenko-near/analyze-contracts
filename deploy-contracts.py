import os
import subprocess
import glob

# requires 
# - `near config add-connection --network-name localnet --connection-name localnet --rpc-url http://localhost:3030/ --wallet-url http://localhost:3030/ --explorer-transaction-url http://localhost:3030/`
# - copy the validator_key.json from neard home to ~/.near-credentials/localtnet/test.near.json
# - replace the `s/secret_key/private_key/g` in the `test.near.json`

# call to setup the `localnet` network configuration

# Configuration
CONTRACTS_DIR = 'contracts'
LOCAL_RPC_URL = 'http://127.0.0.1:3030' # Default local neard RPC endpoint
MASTER_ACCOUNT = 'test.near' # The default account on a local neard instance
# Path to the local master account's private key file (e.g. ~/.near/validator_key.json)
LOCAL_KEY_PATH = '/home/slavas/.near/validator_key.json'

# Ensure the near-cli knows to use 'localnet' environment
os.environ['NEAR_ENV'] = 'localnet'

def parse_private_key_from_deploy_output(output):
    """Parses the private key from the near-cli output after account creation."""
    for line in output.splitlines():
        if line.startswith("SECRET KEYPAIR:"):
            return line.split("SECRET KEYPAIR:")[1].strip()


def deploy_contract(wasm_file, account_id):
    """Deploys a pre-compiled WASM contract using near-cli-rs on localnet."""
    contract_name = os.path.splitext(os.path.basename(wasm_file))[0]

    # Use near-cli-rs with specific options for local network and key
    print(f"--- Deploying {wasm_file} to {account_id} on localnet ---")
    
    # 1. Create the subaccount first, funded by the master account
    # near account create-account fund-myself <new-account> '10 NEAR' autogenerate-new-keypair print-to-terminal sign-as test.near network-config localnet sign-with-keychain send
    create_account_command = [
        'near', 'account', 'create-account', 'fund-myself', account_id, '10 NEAR', 'autogenerate-new-keypair', 'print-to-terminal',
        'sign-as', MASTER_ACCOUNT,
        'network-config', 'localnet', 'sign-with-keychain', 'send'
    ]

    # print(f"Creating account {account_id}...")
    # private_key = None
    # try:
    #     result = subprocess.run(create_account_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #     print(f"Account creation output: {result.stdout.decode()}")
    #     private_key = parse_private_key_from_deploy_output(result.stdout.decode())
    #     print(f"Successfully created account {account_id}")
    # except subprocess.CalledProcessError as e:
    #     print(f"Account creation failed for {account_id}: {e.output.decode()}")

    # 2. Deploy the contract to the new account
    # near contract deploy tjrdnjs2035.test.near use-file <contract-path.wasm> without-init-call network-config localnet sign-with-plaintext-private-key <private-key> send
    deploy_command = [
        'near', 'contract', 'deploy', 'test.near', 'use-file', wasm_file,
        # 'near', 'contract', 'deploy', account_id, 'use-file', wasm_file,
        'without-init-call', 'network-config', 'localnet',
        'sign-with-keychain',
        # 'sign-with-plaintext-private-key', private_key,
        'send'
    ]

    print(f"Deploying contract {contract_name} to account {account_id}...")
    try:
        subprocess.run(deploy_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Successfully deployed {contract_name} to {account_id}")
    except subprocess.CalledProcessError as e:
        print(f"Deployment failed for {contract_name}: {e.stderr.decode()}")


def main():
    """Iterates through all wasm files in the contracts directory and deploys them."""
    wasm_files = glob.glob(os.path.join(CONTRACTS_DIR, '*.wasm'))

    if not wasm_files:
        print(f"No WASM contract files found in {CONTRACTS_DIR} directory.")
        return

    for wasm_file in wasm_files:
        contract_name = os.path.splitext(os.path.basename(wasm_file))[0]
        # Extract hex prefix (first part before the first dot) to keep account ID short
        hex_prefix = contract_name.split('.')[0]
        account_id = f"{hex_prefix}.{MASTER_ACCOUNT}"
        deploy_contract(wasm_file, account_id)
        print("-" * 40)


if __name__ == "__main__":
    main()
