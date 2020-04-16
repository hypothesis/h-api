"""Tools for deserialising and creating command objects."""
from h_api.bulk_api.model.command import (
    Command,
    ConfigCommand,
    CreateCommand,
    UpsertCommand,
)
from h_api.bulk_api.model.config_body import Configuration
from h_api.bulk_api.model.data_body import (
    CreateGroupMembership,
    UpsertGroup,
    UpsertUser,
)
from h_api.enums import CommandType, ViewType

# pylint: disable=too-few-public-methods


class CommandBuilder:
    """A class for creating commands."""

    @classmethod
    def from_data(cls, raw):
        """Create a command from a raw data structure.

        :param raw: The data to decode
        :returns: An appropriate child of `Command`
        :raise ValueError: If the command type is unknown
        """

        command = Command(raw)

        if command.type is CommandType.CONFIGURE:
            return ConfigCommand(raw)

        if command.type is CommandType.CREATE:
            return CreateCommand(raw)

        if command.type is CommandType.UPSERT:
            return UpsertCommand(raw)

        # As we use an enum, this really shouldn't happen
        raise ValueError(f"Unknown data type: {command.type}")

    @classmethod
    def configure(cls, effective_user, total_instructions, view=ViewType.NONE):
        """Create a configuration command.

        :param effective_user: The user to execute actions as
        :param total_instructions: The total number of instructions
        :param view: The return format requested by the client
        :return: A ConfigCommand object
        :rtype: ConfigCommand
        """
        return ConfigCommand.create(
            Configuration.create(effective_user, total_instructions, view=view),
        )

    class user:  # pylint: disable=invalid-name
        """User commands."""

        @classmethod
        def upsert(cls, attributes, id_reference):
            """Create a user upsert command.

            :param attributes: Dict of user fields and values
            :param id_reference: Custom reference to this user
            :return: An UpsertCommand object configured with a user body
            :rtype: UpsertCommand
            """
            return UpsertCommand.create(
                CommandType.UPSERT, UpsertUser.create(attributes, id_reference)
            )

    class group:  # pylint: disable=invalid-name
        """Group commands."""

        @classmethod
        def upsert(cls, attributes, id_reference):
            """Create a group upsert command.

            :param attributes: Dict of group fields and values
            :param id_reference: Custom reference to this group
            :return: An UpsertCommand object configured with a group body
            :rtype: UpsertCommand
            """
            return UpsertCommand.create(
                CommandType.UPSERT, UpsertGroup.create(attributes, id_reference)
            )

    class group_membership:  # pylint: disable=invalid-name
        """Group membership commands."""

        @classmethod
        def create(cls, user_ref, group_ref):
            """Create a group membership create.

            As the group and user ids are not known at command creation time,
            a custom reference can be supplied to the group which is then used
            here to link the two.

            :param user_ref: Custom reference to the user
            :param group_ref: Custom reference to the group
            :return: An CreateCommand object configured with a group
                     membership body
            :rtype: CreateCommand
            """
            return CreateCommand.create(
                CommandType.CREATE, CreateGroupMembership.create(user_ref, group_ref)
            )
