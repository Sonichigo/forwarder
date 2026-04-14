import logging
import os
from datetime import datetime, timezone
from time import time
from zoneinfo import ZoneInfo
from urllib.parse import quote

import requests
from flask import Flask, request, Response, jsonify

app = Flask(__name__)

TARGET_BASE_URL = os.environ.get("TARGET_BASE_URL", "https://play.dbmarlin.com")

# Log to stdout/stderr in a container-friendly way
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger("archiver-forwarder")


def epoch_ms_to_formatted(value, tz_name: str) -> str:
    """Convert epoch milliseconds to formatted string for upstream DBmarlin API."""
    ms = int(value)
    dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc).astimezone(ZoneInfo(tz_name))
    formatted = dt.strftime("%Y-%m-%d+%H:%M:%S")
    logger.info("Converted epoch_ms=%s tz=%s formatted=%s", ms, tz_name, formatted)
    return formatted


def build_query_string(params: dict) -> str:
    parts = []
    for key, value in params.items():
        if key in ("from", "to"):
            encoded_value = quote(str(value), safe=":+")
        else:
            encoded_value = quote(str(value), safe="")
        parts.append(f"{key}={encoded_value}")
    return "&".join(parts)


@app.route("/archiver/rest/v1/activity/summary", methods=["GET"])
def rewrite_archiver_request():
    try:
        tz_name = request.args.get("tz", "Europe/London")
        from_raw = request.args.get("from")
        to_raw = request.args.get("to")

        logger.info(
            "Incoming request path=%s remote_addr=%s args=%s",
            request.path,
            request.remote_addr,
            request.args.to_dict(flat=True)
        )

        if not from_raw or not to_raw:
            logger.warning("Missing required parameters: from=%s to=%s", from_raw, to_raw)
            return jsonify({
                "error": "Both 'from' and 'to' query parameters are required"
            }), 400

        # Allow use of relative values for from/to with 0 = now and -xxxms = (now -xxx ms)
        if int(from_raw) < 1:
            from_raw = int(time() * 1000) + int(from_raw)
        if int(to_raw) < 1:
            to_raw = int(time() * 1000) + int(to_raw)

        # Build upstream request with formatted timestamps for DBmarlin
        rewritten_params = request.args.to_dict(flat=True)
        rewritten_params["from"] = epoch_ms_to_formatted(from_raw, tz_name)
        rewritten_params["to"] = epoch_ms_to_formatted(to_raw, tz_name)

        target_url = f"{TARGET_BASE_URL}{request.path}?{build_query_string(rewritten_params)}"
        logger.info("Rewritten upstream URL=%s", target_url)

        upstream = requests.get(target_url, timeout=30)
        logger.info(
            "Upstream response status=%s content_type=%s",
            upstream.status_code,
            upstream.headers.get("Content-Type")
        )

        # Parse upstream JSON
        data = upstream.json()

        # Generate timestamp as epoch millis (midpoint between from and to)
        mid_epoch_ms = int((int(from_raw) + int(to_raw)) / 2)

        # Determine host identifier from query params or default
        host_id = request.args.get("host", "default")

        # Inject epoch millis timestamp into each item
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    item["timestamp"] = mid_epoch_ms

        # Wrap in Harness CV expected structure:
        # { "all_hosts_data": [ { "host": "<id>", "results": [ {...}, ... ] } ] }
        wrapped = {
            "all_hosts_data": [
                {
                    "host": host_id,
                    "results": data if isinstance(data, list) else [data]
                }
            ]
        }

        logger.info(
            "Responding with host=%s timestamp_epoch_ms=%s data_points=%s",
            host_id,
            mid_epoch_ms,
            len(data) if isinstance(data, list) else 1
        )

        return jsonify(wrapped), upstream.status_code

    except ValueError:
        logger.exception("Invalid epoch value in request args=%s", request.args.to_dict(flat=True))
        return jsonify({
            "error": "'from' and 'to' must be epoch milliseconds"
        }), 400
    except Exception as e:
        logger.exception("Unhandled error while processing request")
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/healthz", methods=["GET"])
def healthz():
    logger.debug("Health check called")
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
