# Optimo IoT cloud & edge public API

## HTTP API

Documented in OpenAPI .yml files.
Serve with swagger:

Cloud:

```
    docker pull swaggerapi/swagger-ui
    docker run -p 8081:8080 -e SWAGGER_JSON=/tmp/cloud_api.yml -v ./:/tmp swaggerapi/swagger-ui
```

Edge (local):

```
    docker pull swaggerapi/swagger-ui
    docker run -p 8081:8080 -e SWAGGER_JSON=/tmp/local_api.yml -v ./:/tmp swaggerapi/swagger-ui
```
