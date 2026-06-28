import logging
from dataclasses import dataclass

import pythoncom
import win32com.client


logger = logging.getLogger(__name__)


class JVLinkError(RuntimeError):
    def __init__(self, method: str, code: int):
        super().__init__(f"{method} failed: return_code={code}")
        self.method = method
        self.code = code


@dataclass
class JVReadResult:
    return_code: int
    data: str
    filename: str

    @property
    def has_data(self) -> bool:
        return self.return_code > 0


class JVLinkClient:
    def __init__(self, sid: str = "UNKNOWN"):
        self.sid = sid
        self._jvlink = None
        self._opened = False

    def initialize(self) -> int:
        logger.info("Initializing JV-Link")
        self._jvlink = win32com.client.Dispatch("JVDTLab.JVLink")

        result = int(self._jvlink.JVInit(self.sid))
        self._raise_if_error("JVInit", result)

        logger.info("JVInit succeeded")
        return result

    def open(self, data_spec: str, from_time: str, option: int = 1):
        self._ensure_initialized()

        read_count = pythoncom.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        download_count = pythoncom.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        last_file_timestamp = pythoncom.VARIANT(
            pythoncom.VT_BYREF | pythoncom.VT_BSTR,
            "",
        )

        result = int(
            self._jvlink.JVOpen(
                data_spec,
                from_time,
                option,
                read_count,
                download_count,
                last_file_timestamp,
            )
        )
        self._raise_if_error("JVOpen", result)

        self._opened = True
        return {
            "return_code": result,
            "read_count": read_count.value,
            "download_count": download_count.value,
            "last_file_timestamp": last_file_timestamp.value,
        }

    def read(self, buffer_size: int = 110000) -> JVReadResult:
        self._ensure_opened()

        data = pythoncom.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, "")
        filename = pythoncom.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, "")

        result = int(self._jvlink.JVRead(data, buffer_size, filename))
        if result < 0:
            self._raise_if_error("JVRead", result)

        return JVReadResult(
            return_code=result,
            data=data.value,
            filename=filename.value,
        )

    def close(self) -> int:
        self._ensure_initialized()

        result = int(self._jvlink.JVClose())
        self._raise_if_error("JVClose", result)

        self._opened = False
        return result

    def get_com_object(self):
        self._ensure_initialized()
        return self._jvlink

    def _ensure_initialized(self):
        if self._jvlink is None:
            raise RuntimeError("JV-Link is not initialized.")

    def _ensure_opened(self):
        self._ensure_initialized()
        if not self._opened:
            raise RuntimeError("JV-Link is not opened.")

    def _raise_if_error(self, method: str, code: int):
        if code < 0:
            logger.error("%s failed return_code=%s", method, code)
            raise JVLinkError(method, code)
