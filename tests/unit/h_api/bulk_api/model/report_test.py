import pytest

from h_api.bulk_api.model.report import Report


class TestReport:
    def test_it(self):
        report = Report("id")

        assert report.id == "id"
        assert report.public_id == "id"

    def test_it_raises_ValueError_without_id(self):
        with pytest.raises(ValueError):
            Report(None)

    def test_different_ids(self):
        report = Report("private_id", "public_id")

        assert report.id == "private_id"
        assert report.public_id == "public_id"

    def test_stringification(self):
        report = Report("private_id", "public_id")

        assert str(report) == "<Report: 'private_id' (public_id)>"
