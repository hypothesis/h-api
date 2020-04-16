"""Command wrappers which contain payload bodies."""

from copy import deepcopy
from functools import lru_cache

from h_api.bulk_api.model.config_body import Configuration
from h_api.bulk_api.model.data_body import (
    CreateGroupMembership,
    UpsertGroup,
    UpsertUser,
)
from h_api.enums import CommandType, DataType
from h_api.exceptions import UnsupportedOperationError
from h_api.model.base import Model
from h_api.schema import Schema


class Command(Model):
    """A single abstract command provided to the API."""

    validator = Schema.get_validator("bulk_api/wrapper.json")
    validation_error_title = "Cannot interpret command as the wrapper is malformed"

    def validate(self):  # pylint: disable=arguments-differ
        """Validate this object and it's body meet their declared schema."""
        super().validate()

        if isinstance(self.body, Model):
            self.body.validate()

    @classmethod
    def create(cls, type_, body):
        """Create a command.

        :param type_: The CommandType of the command
        :param body: The payload for the command
        :return: An instance of Command
        """
        return cls([CommandType(type_).value, cls.extract_raw(body)])

    @property
    def type(self):
        """Get the command type.

        :return: The CommandType of this command
        """
        return CommandType(self.raw[0])

    @property
    def body(self):
        """Get the body of this command.

        :return: The raw body
        """
        return self.raw[1]

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.body}>"


class ConfigCommand(Command):
    """A command containing job configuration instructions."""

    @classmethod
    def create(cls, config):  # pylint: disable=arguments-differ
        """Create a new ConfigCommand from a configuration instance.

        :param config: A Configuration object
        :return: A ConfigCommand containing that config
        """
        return super().create(CommandType.CONFIGURE, cls.extract_raw(config))

    @property
    @lru_cache(1)
    def body(self):
        """Get the body of this command.

        :return: A Configuration object
        """
        return Configuration(self.raw[1])


class DataCommand(Command):
    """Abstract command class for commands which alter data in the database.

    This object will interpret the instructions given to it and return an
    appropriate body object based on the contents.

    The types must be specified using the `data_classes` dict which maps from
    `DataType` to the class implementing the body. The body should be a child
    of `JSONAPIData`.
    """

    data_classes = None

    @property
    @lru_cache(1)
    def body(self):
        """Get the appropriate body object for this command.

        :return: A different class depending on `DataType` and `data_classes`
        :raise UnsupportedOperationError: If no type can be found for the
                                          given `DataType`
        """
        body = super().body

        data_type = DataType(body["data"]["type"])

        try:
            # pylint: disable=unsubscriptable-object
            # It's subscriptable if child classes have set it to a dict
            class_ = self.data_classes[data_type]

        except KeyError:
            raise UnsupportedOperationError("Invalid action on data type")

        # Don't validate this all the time, we did it on the way in. If we have
        # mutated it it might not match the schema we except from clients, but
        # it's still valid
        return class_(body, validate=False)

    @classmethod
    def prepare_for_execute(cls, batch, default_config):
        """Modify the commands and config in place before execution.

        An opportunity for this class to perform any modifications required
        before the objects can be sent for execution.

        :param batch: A list of instances of this class
        :param default_config: A dict of configuration global to all commands
                               in the batch
        """


class CreateCommand(DataCommand):
    """A command to create an object in the database."""

    data_classes = {DataType.GROUP_MEMBERSHIP: CreateGroupMembership}


class UpsertCommand(DataCommand):
    """A command to upsert an object in the database."""

    data_classes = {
        DataType.GROUP: UpsertGroup,
        DataType.USER: UpsertUser,
    }

    @classmethod
    def prepare_for_execute(cls, batch, default_config):
        """Merge the query into the attributes for exectution."""

        # Pop out this command as it's just for us
        merge_query = default_config.pop("merge_query", None)

        if not merge_query:
            return

        for command in batch:
            query = command.body.meta.get("query")
            if not query:
                continue

            new_attrs = deepcopy(query)
            new_attrs.update(command.body.attributes)

            command.body.attributes = new_attrs
