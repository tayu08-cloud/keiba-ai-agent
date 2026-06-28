import logging
import sys

from keiba_ai_agent.collector.jvlink_client import JVLinkClient, JVLinkError


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    data_spec = "RACE"
    from_time = "20240101000000"

    client = JVLinkClient()

    try:
        client.initialize()
        result = client.read_first(data_spec=data_spec, from_time=from_time, option=1)
    except JVLinkError as exc:
        logging.exception("JV-Link error: method=%s code=%s", exc.method, exc.code)
        return 1
    except Exception:
        logging.exception("Unexpected error")
        return 1

    if result is None:
        print("No data returned.")
        return 0

    print("=== JV-Link raw data ===")
    print(f"filename: {result.filename}")
    print(f"return_code: {result.return_code}")
    print(result.data)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
