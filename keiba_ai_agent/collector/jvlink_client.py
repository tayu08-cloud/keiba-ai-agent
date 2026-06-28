import logging
from dataclasses import dataclass

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
        return self.return_code > 0 and bool(self.data)


class JVLinkClient:
    def __init__(self, sid: str = "UNKNOWN"):
        self.sid = sid
        self._jvlink = None
        self._opened = False

    def initialize(self) -> int:
        logger.info("Initializing JV-Link")
        self._jvlink = win32com.client.Dispatch("JVDTLab.JVLink")

        result = self._to_int_return_code("JVInit", self._jvlink.JVInit(self.sid))
        self._raise_if_error("JVInit", result)

        logger.info("JVInit succeeded")
        return result

    def open(self, data_spec: str, from_time: str, option: int = 1):
        self._ensure_initialized()

        logger.info(
            "Calling JVOpen data_spec=%s from_time=%s option=%s",
            data_spec,
            from_time,
            option,
        )

        raw_result = self._jvlink.JVOpen(data_spec, from_time, option, 0, 0, "")
        logger.info("JVOpen raw_result=%r type=%s", raw_result, type(raw_result).__name__)

        if isinstance(raw_result, tuple):
            result = self._to_int_return_code("JVOpen", raw_result[0])
            read_count = raw_result[1] if len(raw_result) > 1 else 0
            download_count = raw_result[2] if len(raw_result) > 2 else 0
            last_file_timestamp = raw_result[3] if len(raw_result) > 3 else ""
        else:
            result = self._to_int_return_code("JVOpen", raw_result)
            read_count = 0
            download_count = 0
            last_file_timestamp = ""

        self._raise_if_error("JVOpen", result)
        self._opened = True

        return {
            "return_code": result,
            "read_count": read_count,
            "download_count": download_count,
            "last_file_timestamp": last_file_timestamp,
        }

    def read(self, buffer_size: int = 110000) -> JVReadResult:
        self._ensure_opened()

        raw_result = self._jvlink.JVRead("", buffer_size, "")
        logger.info("JVRead raw_result=%r type=%s", raw_result, type(raw_result).__name__)

        if isinstance(raw_result, tuple):
            result = self._to_int_return_code("JVRead", raw_result[0])
            data = raw_result[1] if len(raw_result) > 1 else ""
            filename = raw_result[2] if len(raw_result) > 2 else ""
        else:
            result = self._to_int_return_code("JVRead", raw_result)
            data = ""
            filename = ""

        self._raise_if_error("JVRead", result)

        return JVReadResult(
            return_code=result,
            data=data,
            filename=filename,
        )

    def read_first(self, data_spec: str, from_time: str, option: int = 1) -> JVReadResult | None:
        self.open(data_spec=data_spec, from_time=from_time, option=option)

        try:
            while True:
                result = self.read()

                if result.return_code == 0:
                    logger.info("JVRead reached EOF")
                    return None

                if result.has_data:
                    return result
        finally:
            self.close()

    def close(self) -> int:
        self._ensure_initialized()

        logger.info("Calling JVClose")
        result = self._to_int_return_code("JVClose", self._jvlink.JVClose())
        self._raise_if_error("JVClose", result)

        self._opened = False
        logger.info("JVClose succeeded")
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

    def _to_int_return_code(self, method: str, value) -> int:
        logger.debug("%s raw return=%r type=%s", method, value, type(value).__name__)

        if hasattr(value, "value"):
            value = value.value

        return int(value)
