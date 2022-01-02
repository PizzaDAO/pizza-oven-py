# Re-running a pizza

# Find the render task that created the pizza

If a pizza is completed or errored and needs to be rerun we can capture the mainnet job and run the order task locally to generate a new pizza and pin it to ipfs. after it is checked, the contract admin can

1. determine which pizza needs to be repalced by token id
2. connect to the mainnet cluster and run `Find Render Tasks` in postman filtering on ` "request.data.token_id": 571`
3. get the job from the result
4. re run `dining_setup` while you are connected to the mainnet api
5. run `Rerun kmitchen order` task in postman wiht the job id that you just got
6. the job runs synchronously so you can only run one at at a time.
7. after a while the job will finish and return the order response.
8. save the order response somewhere to use later when updating the artwork in the contract.

# Running a missing pizza
