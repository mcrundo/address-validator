# Address Validation Service

AWS Lambda service that validates and normalizes postal addresses using the [Google Maps Address Validation API](https://developers.google.com/maps/documentation/address-validation).

## Architecture

```
Rails App (AddressValidationJob)
  └─ POST /validate
       └─ API Gateway (HTTP API)
            └─ Lambda (Python 3.12)
                 └─ Google Maps Address Validation API
                 └─ Returns normalized address fields
```

### Request

```json
POST /validate

{
  "address": {
    "lines": ["1600 Amphitheatre Parkway"],
    "city": "Mountain View",
    "state": "CA",
    "postal_code": "94043",
    "country": "US"
  }
}
```

### Response

```json
{
  "line1": "1600 Amphitheatre Pkwy",
  "line2": null,
  "city": "Mountain View",
  "state": "CA",
  "postal_code": "94043-1351",
  "country": "US"
}
```

## Prerequisites

- Python 3.12
- [Terraform CLI](https://developer.hashicorp.com/terraform/install)
- AWS account with credentials configured

## Setup

```sh
bin/setup
source .venv/bin/activate
```

## Running checks

```sh
bin/ci
```

Or individually:

```sh
ruff check src tests        # lint
ruff format --check src tests  # format check
mypy                        # type check
pytest                      # tests
```

## Infrastructure

See [`terraform/`](terraform/) for the AWS infrastructure (Lambda, API Gateway, IAM, Secrets Manager).

## License

[MIT](LICENSE)
