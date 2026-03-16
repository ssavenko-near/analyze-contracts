# example (which actually worked. as some point with some config) of deploying the contract from the CLI to localnet

near config add-connection --network-name localnet --connection-name localnet --rpc-url http://localhost:3030/ --wallet-url http://localhost:3030/ --explorer-transaction-url http://localhost:3030/
near account import-account using-private-key $(KEY_FROM_~/.near/validator_key.json) network-config localnet
near contract deploy test.near use-file ~/downloads/mpc-contract-v3.0.3.wasm without-init-call network-config localnet sign-with-keychain send
