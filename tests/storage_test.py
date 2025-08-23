import json

import pytest

import src.backend_solution.storage as st

def test_roundtrip_caching():
    sid = st.generate_session_id()

    request = {"a": {"b": "c"}, "d": "e"}
    st.save_request(sid, request)
    assert st.load_request(sid) == request

    result = [{"f": 1, "g": {"h": {"i": False}}}, {"j": 10}]
    st.save_results(sid, json.dump(result))
    assert st.load_results(sid) == result

def test_caching_curveballs():
    with pytest.raises(ValueError):
        st.save_request(None, {"a":"b"})
        st.load_request(None)
        st.save_request("", {"c": "d"})
        st.load_request("")



def test_purge():
    pass