import pytest
from pydantic import ValidationError

from cardbudget.config import Settings


def test_loopback_is_only_valid_host(tmp_path):
    assert Settings(data_dir=tmp_path).host == "127.0.0.1"
    with pytest.raises(ValidationError):
        Settings(host="0.0.0.0", data_dir=tmp_path)
    with pytest.raises(ValidationError):
        Settings(host="192.168.1.20", data_dir=tmp_path)
