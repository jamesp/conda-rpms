import textwrap

from conda_rpms.build import name_version_release


def _check_output(spec):
    expected = {'name': 'foo', 'release':'2', 'version':'1'}
    actual = name_version_release(textwrap.dedent(spec).split('\n'))
    assert expected == actual

def test_multiple_names():
    spec = """
            Name: foo
            Version: 1
            Release: 2
            Name: bar
            """
    _check_output(spec)

def test_multiple_versions():
    # should return the first version number
    spec = """
            Name: foo
            Version: 1
            Release: 2
            Version: 3
            """
    _check_output(spec)

def test_multiple_releases():
    # should return the first Release number
    spec = """
            Name: foo
            Version: 1
            Release: 2
            Release: 3
            """
    _check_output(spec)