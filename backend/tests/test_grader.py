from app.services.grader import normalize_output


def test_normalize_output_trims_whitespace_and_windows_newlines():
    assert normalize_output("Hello\r\nWorld\n") == "Hello\nWorld"
