import pytest

from h_api.exceptions import SchemaValidationError
from h_api.model.base import Model
from h_api.schema import Validator


class TestModel:
    def test_initialisation(self):
        # This looks dumb now... but more is coming
        data = {"a": 1}
        model = Model(raw=data)

        assert model.raw is data

    def test_extract_raw(self):
        data = {"a": 1}
        model = Model(raw=data)

        assert Model.extract_raw(data) is data
        assert Model.extract_raw(model) is data

    def test_dict_from_populated(self):
        result = Model.dict_from_populated(a=1, b=None, c="", d=[], e={})

        assert result == {"a": 1, "c": "", "d": [], "e": {}}

    def test_it_applies_schema_when_validator_present(self, ValidatingModel):
        with pytest.raises(SchemaValidationError):
            ValidatingModel("I am not a number")

    def test_it_does_nothing_without_a_validator(self, ValidatingModel):
        ValidatingModel.validator = None

        ValidatingModel("I am not a number")

    def test_it_passes_validation_message_with_errors(self, ValidatingModel):
        ValidatingModel.validation_error_title = "custom message"

        with pytest.raises(SchemaValidationError) as error:
            ValidatingModel("I am not a number")

        assert "custom message" in str(error.value)

    def test_stringification(self):
        class ChildClass(Model):
            """A subclass to test stringification."""

        model = ChildClass("body")

        assert str(model) == "<ChildClass: body>"

    @pytest.fixture
    def ValidatingModel(self):
        class ValidatingModel(Model):
            # I can't mock this easily as jsonschema.Validator raises errors
            # if you try and mock it?
            validator = Validator({"type": "number"})

        return ValidatingModel
