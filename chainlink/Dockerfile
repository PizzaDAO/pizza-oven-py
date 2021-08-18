FROM smartcontract/chainlink:0.10.11 as base

#ENV PORT=6688

#COPY ./chainlink/.env /chainlink/

#EXPOSE $PORT

# Start up the node in dev mode
FROM base AS dev
ENV CHAINLINK_DEV=true

# Start up the node in prod mode
FROM base AS prod
ENV CHAINLINK_DEV=false