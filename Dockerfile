FROM python:3.9.15

WORKDIR /server

# By copying over requirements first, we make sure that Docker will cache
# our installed requirements rather than reinstall them on every build
COPY requirements.txt /server/requirements.txt
RUN pip install -r requirements.txt

COPY . /server
EXPOSE 8022
CMD ["python", "./test_asyncssh/server.py"]