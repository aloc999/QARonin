import xml.etree.ElementTree as ET

from triage import classify, triage


def test_classify_buckets():
    assert classify("Timeout 30000ms exceeded")[0] == "flaky-infra"
    assert classify("Connection refused")[0] == "environment"
    assert classify("AssertionError: expected 8 got 0")[0] == "assertion"
    assert classify("weird ☃")[0] == "needs-human"


def test_triage_junit(tmp_path):
    f = tmp_path / "j.xml"
    f.write_text(
        '<testsuite tests="2" failures="2">'
        '<testcase classname="a" name="t1"><failure message="Timeout">waited</failure></testcase>'
        '<testcase classname="a" name="t2"><failure message="mismatch">expected x</failure></testcase>'
        "</testsuite>"
    )
    rows = triage(str(f))
    assert {r["bucket"] for r in rows} == {"flaky-infra", "assertion"}
    assert all(r["owner"] and r["advice"] for r in rows)


def test_triage_clean_suite(tmp_path):
    f = tmp_path / "j.xml"
    f.write_text('<testsuite tests="1"><testcase classname="a" name="t1"/></testsuite>')
    assert triage(str(f)) == []
