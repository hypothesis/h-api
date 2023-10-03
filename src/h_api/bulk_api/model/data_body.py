"""Models representing the data modifying payloads."""

from h_api.enums import DataType
from h_api.model.json_api import JSONAPIData
from h_api.schema import Schema


class UpsertBody(JSONAPIData):
    """Baseclass for upsert bodies with queries."""

    data_type = None
    """The DataType this body represents."""

    query_fields = []
    """Fields from the attributes to place into the query."""

    @classmethod
    def create(cls, attributes, id_reference):  # pylint: disable=arguments-differ
        """Create an upsert body with query.

        This method will use the declared `data_type` and `query_fields` to
        construct an upsert body with a query. This query will be generated
        by popping the specified fields from the attributes provided.

        :param attributes: The main payload (also used to create the query)
        :param id_reference: The user provided reference for this object
        :return: An UpsertBody instance
        """
        query = {field: attributes.pop(field, None) for field in cls.query_fields}

        return super().create(
            data_type=cls.data_type,
            attributes=attributes,
            meta={"query": query},
            id_reference=id_reference,
        )

    @property
    def query(self):
        """Get the query used to select which item to update."""

        return self.meta["query"]


class UpsertUser(UpsertBody):
    """The data to upsert a user."""

    validator = Schema.get_validator("bulk_api/command/upsert_user.json")
    data_type = DataType.USER
    query_fields = ["authority", "username"]


class UpsertGroup(UpsertBody):
    """The data to upsert a group."""

    validator = Schema.get_validator("bulk_api/command/upsert_group.json")
    data_type = DataType.GROUP
    query_fields = ["authority", "authority_provided_id"]


class CreateGroupMembership(JSONAPIData):
    """The data to add a user to a group."""

    validator = Schema.get_validator("bulk_api/command/create_group_membership.json")

    @classmethod
    def create(cls, user_ref, group_ref):  # pylint: disable=arguments-differ
        """Create a create group membership body for adding users to groups.

        :param user_ref: Custom user reference
        :param group_ref: Custom group reference
        :return: A CreateGroupMembership instance
        """
        return super().create(
            DataType.GROUP_MEMBERSHIP,
            relationships={
                "member": {
                    "data": {"type": DataType.USER.value, "id": {"$ref": user_ref}}
                },
                "group": {
                    "data": {"type": DataType.GROUP.value, "id": {"$ref": group_ref}}
                },
            },
        )

    @property
    def member(self):
        """Get the user which is a member of this group.

        :return: A value object with `id` and `ref` properties.
        """
        return _IdRef(self.relationships["member"]["data"]["id"])

    @property
    def group(self):
        """Get the group which this user is a member of.

        :return: A value object with `id` and `ref` properties.
        """
        return _IdRef(self.relationships["group"]["data"]["id"])


class _IdRef:  # pylint: disable=too-few-public-methods
    """A value object which represents an id reference or concrete id."""

    def __init__(self, value):
        if isinstance(value, dict):
            self.id, self.ref = None, value.get("$ref")
        else:
            self.id, self.ref = value, None
