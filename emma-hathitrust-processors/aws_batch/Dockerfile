FROM python:3.7-slim

RUN pip install pipenv

# Add and install Python modules
ADD Pipfile /tmp
RUN cd /tmp; pipenv install

# Bundle app source
ADD batch.py /tmp

# Run
WORKDIR /tmp
ENTRYPOINT ["pipenv", "run", "python", "batch.py"]
