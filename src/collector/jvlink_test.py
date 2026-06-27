import win32com.client


def main():
    print("JV-Link 接続テスト開始")

    try:
        jv = win32com.client.Dispatch("JVDTLab.JVLink")
        print("✅ JV-Link を呼び出せました")
        print(jv)
    except Exception as e:
        print("❌ JV-Link 接続に失敗しました")
        print(e)


if __name__ == "__main__":
    main()
