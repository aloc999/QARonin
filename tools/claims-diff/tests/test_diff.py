from diff import diff_tables


def test_identical_csv(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id,total\n1,10.0\n")
    b.write_text("id,total\n1,10.0\n")
    assert diff_tables(a, b) == []


def test_changed_json(tmp_path):
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text('[{"id": 1, "total": 10.0}]')
    b.write_text('[{"id": 1, "total": 12.5}]')
    delta = diff_tables(a, b)
    assert delta and any("12.5" in line for line in delta)


def test_added_row_detected(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id\n1\n")
    b.write_text("id\n1\n2\n")
    assert any(line.startswith("+2") for line in diff_tables(a, b))
