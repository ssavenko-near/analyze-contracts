# dump the names of all accounts that have a contract associated with them

while read -r account; do
  ~/neard --home ~/.near view-state dump-code --account-id $account --output ./wasm/$account.wasm
done < accounts.txt
