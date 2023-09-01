# Build image
FROM python:3.11-slim AS requirements-stage

ARG CHROME_VERSION_MAIN=107
ENV CHROME_VERSION_MAIN=${CHROME_VERSION_MAIN}
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /tmp

# Install required deps
RUN apt-get update && apt-get install -y unzip
RUN pip install poetry tqdm requests pydantic

# Build requirements.txt file
COPY ./pyproject.toml ./poetry.lock /tmp/
RUN poetry export --output=requirements.txt --without-hashes

# Download chromedriver and chrome
COPY ./scripts/download_chrome.py download_chrome.py
RUN python download_chrome.py --main-version ${CHROME_VERSION_MAIN} \
    --chrome-filename /tmp/chrome.zip \
    --chromedriver-filename /tmp/chromedriver.zip
RUN unzip -j /tmp/chromedriver.zip -d /tmp
RUN unzip -j /tmp/chrome.zip -d /tmp/chrome

# Main image
FROM python:3.11-slim

ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /code
ENV PYTHONPATH "/code"

RUN apt update && apt install -y ca-certificates fonts-liberation \
    libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 \
    libexpat1 libfontconfig1 libgbm1 libgcc1 libglib2.0-0 \
    libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 \
    libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 \
    libxcb1 libxcomposite1 libxcursor1 libxdamage1 \
    libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 \
    libxss1 libxtst6 lsb-release wget xdg-utils

# Copy requirements.txt, chromedriver, chrome from requirements-stage
COPY --from=requirements-stage /tmp/ /tmp/
COPY --from=requirements-stage /tmp/chromedriver /usr/bin/chromedriver
COPY --from=requirements-stage /tmp/chrome /opt/chrome


# Install google chrome and make chromedriver executable
RUN chmod +x /usr/bin/chromedriver

COPY ./ /code/

RUN pip install -r /tmp/requirements.txt
