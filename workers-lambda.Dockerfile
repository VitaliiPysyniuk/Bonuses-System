FROM amazon/aws-lambda-python:3.8

COPY ./lambda_workers/* ${LAMBDA_TASK_ROOT}
COPY ./models/models.py ${LAMBDA_TASK_ROOT}/models

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"


CMD [ "lambda_function.lambda_handler" ]
