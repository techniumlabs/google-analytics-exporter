# Prometheus Exporter for Google Analytics
This is a prometheus exporter for Google Analytics.

### Configure
To run this you need `credential.json` file for the google service account, `settings.yaml` for specifying the site that need to be monitored and optional `cinit.yaml` if you need secrets that need to pulled in from vault. 

### Run
There is a prebuilt docker container that you can use at `techniumlabs/google-analytics-exporter:0.0.1-r7`

```
docker run -v $(pwd)/cinit.yaml:/app/.cinit.yaml -v $(pwd)/settings.yaml:/app/settings.yaml -v $(pwd)/credential.json:/app/credential.json -v $(pwd)/analytics.py:/app/analytics.py -p 8000:8000 -it techniumlabs/google-analytics-exporter:0.0.1
```

### Develop

## Build
To build the docker image run `make build`


### Reference
1. ![Google Analytics API Explorer](https://ga-dev-tools.appspot.com/dimensions-metrics-explorer/)