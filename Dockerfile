# To enable ssh & remote debugging on app service change the base image to the one below
FROM mcr.microsoft.com/azure-functions/python:4-python3.12-appservice
# FROM mcr.microsoft.com/azure-functions/python:4-python3.12

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    PYTHON_ENABLE_INIT_INDEXING=1

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /home/site/wwwroot
