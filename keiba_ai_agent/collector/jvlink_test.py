from keiba_ai_agent.collector.jvlink_client import JVLinkClient


def main():
    print("=== JV-Link テスト ===")

    client = JVLinkClient()
    client.initialize()

    print(client.get_com_object())


if __name__ == "__main__":
    main()
    