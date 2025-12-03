# Run security patcher
RUN python3 /opt/hue-emulator/patch_security.py || true
ARG BUILD_FROM=ghcr.io/hassio-addons/debian-base:7.3.3
FROM ${BUILD_FROM}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG BUILD_ARCH=amd64
RUN \
  apt-get update \
  && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-setuptools \
    openssl \
    nmap \
    curl \
    git \
    unzip \
    iproute2 \
  && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
    requests==2.31.0 \
    ws4py==0.5.1 \
    Flask==3.0.0 \
    Flask-Login==0.6.3 \
    Werkzeug==3.0.1 \
    zeroconf==0.131.0 \
    paho-mqtt==1.6.1 \
    flask-socketio==5.3.5

WORKDIR /tmp
RUN \
  curl -J -L -o diyhue.tar.gz \
    "https://github.com/diyhue/diyHue/archive/refs/heads/master.tar.gz" \
  && mkdir -p /opt/hue-emulator \
  && tar xzvf diyhue.tar.gz --strip-components=2 -C /opt/hue-emulator diyHue-master/BridgeEmulator \
  && rm diyhue.tar.gz

COPY rootfs/ /

RUN chmod a+x /run.sh \
  && chmod a+x /opt/hue-emulator/select.sh

ARG BUILD_DATE
ARG BUILD_REF
ARG BUILD_VERSION

LABEL \
  io.hass.name="diyHue Enhanced" \
  io.hass.description="diyHue with 3-LED security support" \
  io.hass.arch="${BUILD_ARCH}" \
  io.hass.type="addon" \
  io.hass.version=${BUILD_VERSION}

WORKDIR /opt/hue-emulator

EXPOSE 80 443 1900/udp 2100/udp 1982/udp

CMD ["/run.sh"]
