from expect import expect_import

# TODO: Define dummy module in a string.


def test_importer():
    dummy_module = expect_import("dummy_module")
    assert dummy_module.main() == (1, 2)
