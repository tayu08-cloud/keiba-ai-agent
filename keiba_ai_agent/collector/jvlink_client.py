import win32com.client


class JVLinkClient:
    def __init__(self, sid="UNKNOWN"):
        self.sid = sid
        self._jvlink = None

    def initialize(self):
        self._jvlink = win32com.client.Dispatch("JVDTLab.JVLink")
        result = self._jvlink.JVInit(self.sid)

        if result != 0:
            raise RuntimeError(f"JVInit failed: {result}")

        return result

    def get_com_object(self):
        if self._jvlink is None:
            raise RuntimeError("JV-Link is not initialized.")

        return self._jvlink
