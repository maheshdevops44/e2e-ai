FROM ubuntu:22.04

# Install system dependencies including Python and Playwright requirements
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    curl \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    fonts-dejavu \
    fonts-freefont-ttf \
    fontconfig \
    libappindicator3-1 \
    libasound2-dev \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libnss3-tools \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    traceroute \
    xvfb \
    ffmpeg \
    iputils-ping \
    postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    # Create python/pip symlinks \
    ln -sf /usr/bin/python3.11 /usr/bin/python && \
    ln -sf /usr/bin/python3.11 /usr/bin/python3

# Set up certificates
# Downloading certificates
RUN curl -sk https://raw.github.sys.cigna.com/cigna/certfix/main/certs/generated/combined.pem -o combined.pem &&\
    cp combined.pem /etc/ssl/certs/combined.pem &&\
    cp combined.pem /usr/local/share/ca-certificates/combined.pem &&\
    cat combined.pem >> /etc/ssl/certs/cert.pem

# #RUN curl -sk https://raw.github.sys.cigna.com/cigna/certfix/master/zscaler.pem -o zscaler.pem &&\
#    # cat zscaler.pem >> /etc/ssl/certs/zscaler.pem

COPY cert.pem /usr/local/share/ca-certificates/cert.pem
COPY cert.pem /etc/ssl/certs/cert.pem

# Set environment variables for applications to use system certificates
ENV REQUESTS_CA_BUNDLE=/usr/local/share/ca-certificates/combined.pem
ENV NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/combined.pem
ENV SSL_CERT_FILE=/etc/ssl/certs/combined.pem

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Install Playwright browsers with dependencies
RUN playwright install chromium

# Copy application code
COPY . /app
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/videos /app/screenshots
RUN mkdir -p /app/tests && chmod -R 777 /app/tests
RUN mkdir -p /app/network_logs && chmod -R 777 /app/network_logs

EXPOSE 8000

RUN mkdir -p /tmp/certs && \
    awk 'BEGIN {c=0;} /BEGIN CERTIFICATE/{c++} { print > "/tmp/certs/cert." c ".crt"}' < /etc/ssl/certs/combined.pem && \
    cp /tmp/certs/cert.*.crt /usr/local/share/ca-certificates/ && \
    rm -rf /tmp/certs

RUN update-ca-certificates --fresh

# # Import system CAs into Chromium's NSS DB so the browser trusts your enterprise certs
RUN mkdir -p /root/.pki/nssdb && \
    certutil -N -d sql:/root/.pki/nssdb --empty-password && \
    for cert in /usr/local/share/ca-certificates/*.crt; do \
        certutil -A -d sql:/root/.pki/nssdb -n "$(basename "$cert")" -t "C,," -i "$cert"; \
    done

# cmd - uvicorn api:app --host 0.0.0.0 --port 8000
# CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["/bin/bash", "entry-script.sh"]
