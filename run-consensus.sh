./consensus/prysm.sh \
    beacon-chain \
    --execution-endpoint=/tmp/geth.ipc \
    --mainnet \
    --checkpoint-sync-url=https://beaconstate.info \
    --genesis-beacon-api-url=https://beaconstate.info \
    --datadir data  