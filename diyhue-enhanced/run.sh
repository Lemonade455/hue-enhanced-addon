#!/usr/bin/with-contenv bashio

CONFIG_PATH=$(bashio::config 'config_path')
MAC=$(bashio::config 'mac')
DEBUG=$(bashio::config 'debug')
NO_SERVE_HTTPS=$(bashio::config 'no_serve_https')
DECONZ_IP=$(bashio::config 'deconz_ip')
BUTTON_SECURITY=$(bashio::config 'button_security')
BUTTON_TIMEOUT=$(bashio::config 'button_timeout')
LED_INDICATOR=$(bashio::config 'led_indicator')

bashio::log.info "╔══════════════════════════════════════════════════╗"
bashio::log.info "║        diyHue Enhanced Starting                  ║"
bashio::log.info "║        With 3-LED Security Support               ║"
bashio::log.info "╚══════════════════════════════════════════════════╝"

if [[ ! $MAC =~ ^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$ ]]; then
    bashio::log.fatal "Invalid MAC address format! Must be XX:XX:XX:XX:XX:XX"
    bashio::log.fatal "Use 'ip addr' or 'ifconfig' to find your MAC address"
    exit 1
fi

bashio::log.info "Configuration:"
bashio::log.info "  Config Path: ${CONFIG_PATH}"
bashio::log.info "  MAC Address: ${MAC}"
bashio::log.info "  Debug: ${DEBUG}"
bashio::log.info "  HTTPS: $(if [ \"$NO_SERVE_HTTPS\" = \"true\" ]; then echo \"Disabled\"; else echo \"Enabled\"; fi)"
bashio::log.info "  Enhanced Security: ${BUTTON_SECURITY}"
bashio::log.info "  Button Timeout: ${BUTTON_TIMEOUT}s"
bashio::log.info "  LED Indicator: ${LED_INDICATOR}"

if [ ! -d "${CONFIG_PATH}" ]; then
    bashio::log.info "Creating config directory: ${CONFIG_PATH}"
    mkdir -p "${CONFIG_PATH}"
fi

export CONFIG_PATH
export MAC
export DEBUG
export BUTTON_SECURITY
export BUTTON_TIMEOUT  
export LED_INDICATOR
export IP_ADDRESS=$(hostname -I | awk '{print $1}')

cd /opt/hue-emulator || exit 1

if [ -f "./select.sh" ]; then
    bashio::log.info "Selecting architecture-specific binaries..."
    ./select.sh
fi

PYTHON_CMD="python3 -u HueEmulator3.py"

if [ "${DEBUG}" = "true" ]; then
    PYTHON_CMD="${PYTHON_CMD} --debug true"
    bashio::log.info "Debug mode enabled"
fi

if [ "${NO_SERVE_HTTPS}" = "true" ]; then
    PYTHON_CMD="${PYTHON_CMD} --no-serve-https"
    bashio::log.info "HTTPS disabled"
fi

if [ -n "${DECONZ_IP}" ]; then
    PYTHON_CMD="${PYTHON_CMD} --deconz ${DECONZ_IP}"
    bashio::log.info "deCONZ integration enabled: ${DECONZ_IP}"
fi

PYTHON_CMD="${PYTHON_CMD} --config-path ${CONFIG_PATH}"
PYTHON_CMD="${PYTHON_CMD} --mac ${MAC}"

bashio::log.info "Starting diyHue Enhanced..."
bashio::log.info "Bridge IP: ${IP_ADDRESS}"
bashio::log.info "Web UI: http://${IP_ADDRESS}"
bashio::log.info ""
bashio::log.info "🔗 To pair with Hue app:"
bashio::log.info "   1. Open Hue app"
bashio::log.info "   2. Search for bridge"
bashio::log.info "   3. Go to http://${IP_ADDRESS}/#linkbutton"
if [ "${BUTTON_SECURITY}" = "true" ]; then
    bashio::log.info "   4. Press ACTIVATE (will show 3 LED indicators)"
    bashio::log.info "   5. Connect in app within ${BUTTON_TIMEOUT} seconds"
else
    bashio::log.info "   4. Press ACTIVATE and connect in app"
fi
bashio::log.info ""

exec ${PYTHON_CMD}
