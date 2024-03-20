(cd go-ethereum && make geth)

sudo ./go-ethereum/build/bin/geth \
    --syncmode full \
    --datadir data \
    --http \
    --http.api eth,net,engine,admin \
    --ipcpath /tmp/geth.ipc \
    --gcmode archive \
    --cache.noprefetch 