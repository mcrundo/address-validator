# Address Validation Service

AWS Lambda service that validates and normalizes postal addresses using the [Google Maps Address Validation API](https://developers.google.com/maps/documentation/address-validation).

## Architecture

```mermaid
flowchart LR
    A[Rails App] -->|POST /validate| B[API Gateway<br/>HTTP API]
    B --> C[Lambda<br/>Python 3.12]
    C -->|validateAddress| D[Google Maps API]
    D --> C
    C --> B
    B --> A

    E[Secrets Manager] -.->|API key| C
    C -.->|logs| F[CloudWatch]
    C -.->|traces| G[X-Ray]
    C -.->|failures| H[SQS DLQ]
    F -.->|alarms| I[SNS]
```

```
Rails App (AddressValidationJob)
  └─ POST /validate
       └─ API Gateway (HTTP API)
            └─ Lambda (Python 3.12)
                 ├─ Google Maps Address Validation API
                 └─ Returns normalized address fields

Supporting services:
  ├─ Secrets Manager → Google Maps API key + service API key
  ├─ CloudWatch → Lambda logs + alarms (errors, latency, throttles)
  ├─ X-Ray → request tracing
  ├─ SQS → dead letter queue for failed invocations
  ├─ SNS → alarm notifications (optional)
  └─ IAM → least-privilege execution role
```

## API

Full OpenAPI 3.1 spec: [`docs/openapi.yaml`](docs/openapi.yaml)

### `GET /health`

Health check — no auth required, no external calls.

```sh
curl https://<api-id>.execute-api.us-east-2.amazonaws.com/health
```

```json
{"status": "ok"}
```

### `POST /validate`

Validate and normalize an address.

**Request:**

```sh
curl -X POST https://<api-id>.execute-api.us-east-2.amazonaws.com/validate \
  -H "Content-Type: application/json" \
  -d '{
    "address": {
      "lines": ["1600 Amphitheatre Parkway"],
      "city": "Mountain View",
      "state": "CA",
      "postal_code": "94043",
      "country": "US"
    }
  }'
```

**Response (200):**

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

**Error (400):**

```json
{
  "error": "address.lines must be a non-empty array of strings"
}
```

**Error (502):**

```json
{
  "error": "Google Maps API request timed out"
}
```

### Request fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `address.lines` | `string[]` | yes | — | Street address lines |
| `address.city` | `string` | no | `""` | City or locality |
| `address.state` | `string` | no | `""` | State or administrative area |
| `address.postal_code` | `string` | no | `""` | ZIP or postal code |
| `address.country` | `string` | no | `"US"` | ISO 3166-1 alpha-2 country code |

### Response fields

| Field | Type | Description |
|-------|------|-------------|
| `line1` | `string` | Primary street address |
| `line2` | `string \| null` | Secondary line (unit, suite) or null |
| `city` | `string` | City or locality |
| `state` | `string` | State abbreviation |
| `postal_code` | `string` | ZIP code (may include +4) |
| `country` | `string` | ISO 3166-1 alpha-2 code |

## Prerequisites

- Python 3.12
- Docker (for local invocation)
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
ruff check src tests           # lint
ruff format --check src tests  # format check
mypy                           # type check
pytest                         # tests
```

## Local invocation

Run the Lambda locally using the AWS Lambda Runtime Interface Emulator:

```sh
cp .env.example .env  # add your API key
docker compose up --build
```

Then invoke:

```sh
curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -H "Content-Type: application/json" \
  -d '{"body": "{\"address\": {\"lines\": [\"1600 Amphitheatre Parkway\"], \"city\": \"Mountain View\", \"state\": \"CA\", \"postal_code\": \"94043\", \"country\": \"US\"}}"}'
```

## Infrastructure

See [`terraform/`](terraform/) for the AWS infrastructure:

| Resource | Purpose |
|----------|---------|
| Lambda (x3) | Handler, authorizer, and health check functions |
| API Gateway | HTTP API with `POST /validate` and `GET /health` routes |
| IAM | Least-privilege execution role |
| Secrets Manager | Google Maps API key + service API key (values set out-of-band) |
| CloudWatch | Log groups + alarms (errors, latency, throttles, DLQ depth) |
| SQS | Dead letter queue for failed handler invocations (14-day retention) |
| X-Ray | Active tracing on all Lambda functions |
| SNS | Alarm notifications (optional — set `alarm_email` variable) |

### Deployment

Merges to `main` trigger automated deployment via [GitHub Actions](.github/workflows/deploy.yml):

1. Package Lambda (install deps + zip)
2. `terraform apply`
3. Smoke test against the live endpoint

PRs run `terraform plan` and post the output as a comment.

### First-time setup

1. **Create the Terraform state bucket:**
   ```sh
   aws s3 mb s3://address-validation-tf-state --region us-east-2 --profile aws
   aws s3api put-bucket-versioning --bucket address-validation-tf-state \
     --versioning-configuration Status=Enabled --region us-east-2 --profile aws
   ```

2. **Set secrets after first deploy:**
   ```sh
   # Google Maps API key
   aws secretsmanager put-secret-value \
     --secret-id address-validation/dev/google-maps-api-key \
     --secret-string "<your-google-maps-api-key>" \
     --region us-east-2 --profile aws

   # Service API key (for x-api-key header)
   aws secretsmanager put-secret-value \
     --secret-id address-validation/dev/api-key \
     --secret-string "$(openssl rand -hex 32)" \
     --region us-east-2 --profile aws
   ```

3. **Set Lambda environment variables:**
   ```sh
   # Handler
   aws lambda update-function-configuration \
     --function-name address-validation-handler-dev \
     --environment "Variables={GOOGLE_MAPS_API_KEY=<key>,LOG_LEVEL=INFO}" \
     --region us-east-2 --profile aws

   # Authorizer
   aws lambda update-function-configuration \
     --function-name address-validation-authorizer-dev \
     --environment "Variables={API_KEY=<key>,LOG_LEVEL=INFO}" \
     --region us-east-2 --profile aws
   ```

### Monitoring

- **CloudWatch Alarms**: error rate, p99 latency, throttles, DLQ depth
- **X-Ray**: request tracing (AWS Console → X-Ray → Traces)
- **Dead Letter Queue**: failed invocations retained for 14 days
- **Alarm notifications**: set `alarm_email` Terraform variable to receive email alerts

## License

[MIT](LICENSE)
