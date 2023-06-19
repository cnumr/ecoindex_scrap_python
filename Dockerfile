# Build image
FROM python:3.11-slim

ARG CHROME_VERSION_MAIN=111
ENV CHROME_VERSION_MAIN=${CHROME_VERSION_MAIN}
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /tmp

RUN apt update && apt install -y unzip wget

# Download chromedriver and chrome
RUN wget "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION_MAIN}" -O /tmp/chrome_version
RUN wget "https://chromedriver.storage.googleapis.com/$(cat /tmp/chrome_version)/chromedriver_linux64.zip" \
    && unzip -o chromedriver_linux64.zip && rm chromedriver_linux64.zip \
    && mv chromedriver ${CHROMEDRIVER_PATH} \
    && chmod +x ${CHROMEDRIVER_PATH}
RUN wget "https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_$(cat /tmp/chrome_version)-1_amd64.deb" \
    -O google-chrome-stable.deb
RUN apt update && \
    apt -y install libpq-dev gcc /tmp/google-chrome-stable.deb && \
    rm -rf /var/lib/apt/lists/* && \
    rm /tmp/google-chrome-stable.deb

WORKDIR /code
ENV PYTHONPATH "/code"

COPY poetry.lock pyproject.toml ./
RUN pip install poetry && \
    poetry export --output requirements.txt --without-hashes && \
    pip install -r requirements.txt

COPY ./ ./
