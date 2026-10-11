#aws lambda base image
FROM public.ecr.aws/lambda/python:3.12

# copy and install dependencies
COPY requirementsDocker.txt ${LAMBDA_TASK_ROOT}/requirements.txt
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Copy application source code
COPY main.py lambda_handler.py ${LAMBDA_TASK_ROOT}/

#exposing 8080 for local testing
EXPOSE 8080

# Lambda entry point
CMD ["lambda_handler.lambda_handler"]