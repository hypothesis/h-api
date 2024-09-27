"""Generic model objects representing objects in JSON API style."""

from h_api.enums import DataType
from h_api.model.base import Model


class JSONAPIError(Model):
    """A JSON API error wrapper."""

    @classmethod
    def create(cls, error_bodies):
        """Create a new error from the provided error details.

        :param error_bodies: Instances of JSONAPIErrorBody or equivalent dicts
        :return: A JSONAPIError instance
        """
        return cls({"errors": [cls.extract_raw(body) for body in error_bodies]})


class JSONAPIErrorBody(Model):
    """A JSON API error body."""

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    # I know pylint... I know

    @classmethod
    def create(
        cls, exception, title=None, detail=None, pointer=None, status=None, meta=None
    ):
        """Create a new JSON-API style error body."""

        return cls(
            cls.dict_from_populated(
                code=exception.__class__.__name__,
                title=title or exception.args[0],
                detail=detail,
                meta=meta,
                status=str(int(status)) if status is not None else None,
                source={"pointer": pointer} if pointer else None,
            )
        )

    @property
    def detail(self):
        """Get the detail of this error."""
        return self.raw.get("detail", None)


class JSONAPIData(Model):
    """A single JSON API data object (request or response)."""

    # schema = Schema.get_validator('json_api.json#/$defs/document')
    # This would be nice but introduces a circular dependency with
    # Schema as it needs the error stuff above via SchemaValidationError

    # pylint: disable=too-many-arguments,too-many-positional-arguments

    @classmethod
    def create(
        cls,
        data_type,
        _id=None,
        attributes=None,
        meta=None,
        relationships=None,
        id_reference=None,
    ):
        """Create a JSON API style data object."""

        if id_reference is not None:
            if meta is None:
                meta = {}

            meta["$anchor"] = id_reference

        return cls(
            {
                "data": cls.dict_from_populated(
                    type=DataType(data_type).value,
                    id=_id,
                    attributes=attributes,
                    meta=meta,
                    relationships=relationships,
                )
            }
        )

    @property
    def id(self):
        """Get the id."""

        return self._data["id"]

    @property
    def type(self):
        """Get the data type of this object.

        :rtype: DataType
        """
        return DataType(self._data["type"])

    @property
    def attributes(self):
        """Get a dict of attributes for this object."""

        return self._data["attributes"]

    @attributes.setter
    def attributes(self, attributes):
        self._data["attributes"] = attributes

    @property
    def meta(self):
        """Get the data metadata (not the root metadata)."""

        return self._data.get("meta", {})

    @property
    def relationships(self):
        """Get the relationships between this object and others."""

        return self._data["relationships"]

    @property
    def id_reference(self):
        """Get the id reference.

        This is a custom extension to JSON API which allows you to give an item
        a reference which you can refer to in the same call. This is intended
        to allow you to refer to something which you don't yet know the id for.
        """
        return self.meta.get("$anchor")

    @property
    def _data(self):
        return self.raw["data"]
