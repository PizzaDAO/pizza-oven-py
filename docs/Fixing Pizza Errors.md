# Re-running a pizza

# Find the render task that created the pizza

Ifa pizza is completed or errored and needs to be rerun we can capture the mainnet job and run the order task locally to generate a new pizza and pin it to ipfs. after it is checked, the contract admin can

1. using the cloudflare datastore, filter the `render_task` collection by `request.data.token_id == TOKEN_ID`
2. capture the job id
3. get the job from the mainnet order api using the jobid.
4. re run `dining_setup` while you are connected to the mainnet api
5. in your local `.cache/render_task` create a file named `render_task-JOB_ID.json` where JOB_IS is the job id captured eariler
6. remove the `metadata_hash` and the `responseURL` values and set them to `null`
7. change the status to `new`
8. make a copy of it so that we don't overwrite the mainnnet data (juist in case)
9. disconnect the mainnet node
10. validate that your local .env config is set to use the `pinata` ipfs node
11. spin up your local node & run dining setup
12. re run `dining_setup` while connected to your local node
13. call `rerun_render_task` using postman
14. wait for the pizza to finish
15. on the command line capture the ipfs hash for the `medatada`

# Running a missing pizza
