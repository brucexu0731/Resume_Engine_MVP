FROM public.ecr.aws/lambda/python:3.12

COPY requirementsDocker.txt ${LAMBDA_TASK_ROOT}/requirements.txt

RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt

COPY main.py ${LAMBDA_TASK_ROOT}

EXPOSE 8080

CMD ["main.lambda_handler"]