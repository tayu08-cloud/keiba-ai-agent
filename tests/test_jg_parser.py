import pytest

from keiba_ai_agent.parser.jg_parser import Horse, parse_jg_record


def test_parse_jg_record_extracts_minimum_fields():
    raw = "JG12025062720250628020105002022100614ハーフェン　　　　　　　　　　　　　00190\r\n"

    parsed = parse_jg_record(raw)

    assert isinstance(parsed, Horse)
    assert parsed.record_type == "JG"
    assert parsed.raw == raw.rstrip("\r\n")
    assert parsed.horse_name == "ハーフェン"
    assert parsed.extra["horse_name_candidates"][0] == "ハーフェン"


def test_parse_jg_record_rejects_non_jg_record():
    with pytest.raises(ValueError):
        parse_jg_record("RA120250627")
