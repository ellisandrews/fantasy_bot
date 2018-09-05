FROM python:2

COPY . .

RUN pip install -r requirements.txt

RUN /bin/bash -c "source ./env_variables.sh"

CMD [ "python", "./run_bot.py" ]
