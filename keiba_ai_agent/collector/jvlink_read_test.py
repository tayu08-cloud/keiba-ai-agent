import logging
import sys

from keiba_ai_agent.collector.jvlink_client import JVLinkClient, JVLinkError
from keiba_ai_agent.parser.jg_parser import parse_jg_record


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    data_spec = sys.argv[1] if len(sys.argv) >= 2 else "RACE"
    from_time = sys.argv[2] if len(sys.argv) >= 3 else "20240101000000"
    option = int(sys.argv[3]) if len(sys.argv) >= 4 else 1

    print("=== JV-Link raw read test ===")
    print(f"data_spec={data_spec}")
    print(f"from_time={from_time}")
    print(f"option={option}")

    client = JVLinkClient()

    try:
        client.initialize()
        result = client.read_first(data_spec=data_spec, from_time=from_time, option=option)
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

    if result.data.startswith("JG"):
        print("=== Parsed JG data ===")
        print(parse_jg_record(result.data))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
