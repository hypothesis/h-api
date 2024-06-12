"""Classes for loading and parsing JSON schema."""

import json
from functools import lru_cache

import importlib_resources
from jsonschema import Draft7Validator
from referencing import Registry, Resource

from h_api.exceptions import SchemaValidationError


class Validator:  # pylint:disable=too-few-public-methods
    """A JSON schema validator."""

    def __init__(self, *args, **kwargs):
        self._validator = Draft7Validator(*args, **kwargs)

    def validate_all(self, instance, error_title="The data does not match the schema"):
        """Report all validation errors in the instance against this schema.

        :param instance: The instance to check
        :param error_title: Custom error message when errors are found
        :raise SchemaValidationError: When errors are found
        """

        errors = []

        for error in self._validator.iter_errors(instance):
            errors.append(error)

        if errors:
            raise SchemaValidationError(errors, title=error_title)


class Schema:
    """JSON Schema loader."""

    BASE_DIR = importlib_resources.files("h_api") / "resources/schema"
    LOCAL_REGISTRY = Registry(
        retrieve=lambda uri: Resource.from_contents(
            json.loads((Schema.BASE_DIR / uri).read_text())
        )
    )
    RESOLVER = LOCAL_REGISTRY.resolver()

    @classmethod
    def get_schema(cls, relative_path):
        """Load a schema object as a plain dict.

        :param relative_path: Path to the schema object
        :return: A dict representing the schema
        """

        return cls.RESOLVER.lookup(relative_path).contents

    @classmethod
    @lru_cache(32)
    def get_validator(cls, relative_path):
        """Get a validator for the provided schema.

        The schema is relative to the `resources/schema` directory.
        You can include extra url fragments on the end of the URL:

            my_schema.json#/$defs/myObject

        :param relative_path: Path to the schema object
        :return: A Validator object
        """
        return Validator({"$ref": relative_path}, registry=cls.LOCAL_REGISTRY)
