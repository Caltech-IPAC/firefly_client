import firefly_client


def test_version():
    v_str = (
        firefly_client.__dict__["__version__"]
        if "__version__" in firefly_client.__dict__
        else "development"
    )
    print("Version: %s" % v_str)
    assert v_str is not None
    assert isinstance(v_str, str)
