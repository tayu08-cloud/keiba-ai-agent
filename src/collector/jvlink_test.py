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
import win32com.client


def main():
    print("JV-Link 初期化テスト開始")

    jv = win32com.client.Dispatch("JVDTLab.JVLink")

    try:
        result = jv.JVInit("UNKNOWN")
        print("JVInit result:", result)
    except Exception as e:
        print("JVInitでエラー")
        print(e)


if __name__ == "__main__":
    main()
import win32com.client


def main():
    print("JV-Link 初期化テスト開始")

    try:
        jv = win32com.client.Dispatch("JVDTLab.JVLink")
        result = jv.JVInit("UNKNOWN")
        print("JVInit result:", result)
    except Exception as e:
        print("JVInitでエラー")
        print(e)


if __name__ == "__main__":
    main()

