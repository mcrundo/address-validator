FROM public.ecr.aws/lambda/python:3.12

COPY src/address_validation/ ${LAMBDA_TASK_ROOT}/address_validation/
COPY requirements.lock ${LAMBDA_TASK_ROOT}/

RUN pip install --no-cache-dir -r requirements.lock -t ${LAMBDA_TASK_ROOT}

CMD ["address_validation.handler.handler"]
