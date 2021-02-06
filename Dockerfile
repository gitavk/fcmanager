FROM python:2.7-slim

RUN apt-get update && apt-get install -y \
		gcc \
		gettext \
		postgresql-client libpq-dev \
        python-dev \
	--no-install-recommends && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY requirements.pip ./
RUN pip install -r requirements.pip

# COPY . .

EXPOSE 8080
