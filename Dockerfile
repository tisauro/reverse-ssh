FROM python:3.9.15

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /server

# By copying over requirements first, we make sure that Docker will cache
# our installed requirements rather than reinstall them on every build
COPY requirements.txt /server/requirements.txt
RUN pip install -r requirements.txt

#COPY . /server
#EXPOSE 8022
#CMD ["python", "./test_asyncssh/server.py"]