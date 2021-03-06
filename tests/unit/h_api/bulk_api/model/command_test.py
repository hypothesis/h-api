from copy import deepcopy
from unittest.mock import create_autospec

import pytest

from h_api.bulk_api.model.command import (
    Command,
    ConfigCommand,
    DataCommand,
    UpsertCommand,
)
from h_api.bulk_api.model.config_body import Configuration
from h_api.bulk_api.model.data_body import UpsertUser
from h_api.enums import CommandType, DataType
from h_api.exceptions import SchemaValidationError, UnsupportedOperationError
from h_api.model.base import Model


class TestCommand:
    def test_from_raw(self, upsert_user_body):
        command = Command([CommandType.CREATE.value, upsert_user_body])

        self._check_command(command, upsert_user_body)

    def test_create(self, upsert_user_body):
        command = Command.create(CommandType.CREATE, UpsertUser(upsert_user_body))

        self._check_command(command, upsert_user_body)

    @pytest.mark.parametrize(
        "raw",
        (
            [],
            ["create"],
            {},
            ["wrong", {}],
            [CommandType.CREATE.value, {}],
            [CommandType.CONFIGURE.value, []],
        ),
    )
    def test_we_apply_validation(self, raw):
        with pytest.raises(SchemaValidationError):
            Command(raw)

    def test_if_body_is_a_model_we_apply_its_validation(self, model):
        class CommandWithModelBody(Command):
            validator = None
            body = model

        command = CommandWithModelBody(CommandType.UPSERT, {})

        try:
            command.validate()
        finally:
            model.validate.assert_called_once()

    def test_stringification(self):
        class CommandChild(Command):
            validator = None
            "Subclass to test stringification"

        command = CommandChild.create(CommandType.CREATE, "body")

        assert str(command) == "<CommandChild body>"

    def _check_command(self, command, body):
        assert isinstance(command, Command)

        assert command.type == CommandType.CREATE
        assert command.body == body
        assert command.raw == [CommandType.CREATE.value, body]

    @pytest.fixture
    def model(self):
        return create_autospec(Model, instance=True)


class TestConfigCommand:
    def test_from_raw(self, configuration_body):
        command = ConfigCommand([CommandType.CONFIGURE.value, configuration_body])

        self._check_command(command, configuration_body)

    def test_create(self, configuration_body):
        command = ConfigCommand.create(Configuration(configuration_body))

        self._check_command(command, configuration_body)

    def _check_command(self, command, body):
        isinstance(command, ConfigCommand)

        assert command.type == CommandType.CONFIGURE
        assert isinstance(command.body, Configuration)
        assert command.body.raw == body

        assert command.raw == [CommandType.CONFIGURE.value, body]


class TestDataCommand:
    def test_from_raw(self, UpsertUserCommand, upsert_user_body):
        command = UpsertUserCommand([CommandType.UPSERT.value, upsert_user_body])

        assert isinstance(command, UpsertUserCommand)
        assert isinstance(command.body, UpsertUser)

    def test_we_cannot_create_another_type(self, UpsertUserCommand, upsert_group_body):
        with pytest.raises(UnsupportedOperationError):
            UpsertUserCommand([CommandType.CREATE.value, upsert_group_body])

    @pytest.fixture
    def UpsertUserCommand(self):
        class UpsertUserCommand(DataCommand):
            data_classes = {DataType.USER: UpsertUser}

        return UpsertUserCommand


class TestUpsertCommand:
    def test_prepare_for_execute_pops_merge_query_from_config(self, user_command):
        config = {"merge_query": True, "another": True}

        UpsertCommand.prepare_for_execute([user_command], config)

        assert config == {"another": True}

    def test_prepare_for_execute_merges_queries(self, upsert_command):
        query = deepcopy(upsert_command.body.meta["query"])
        assert query

        for key in query.keys():
            assert key not in upsert_command.body.attributes

        UpsertCommand.prepare_for_execute([upsert_command], {"merge_query": True})

        for key in query.keys():
            assert key in upsert_command.body.meta["query"]
            assert key in upsert_command.body.attributes

    def test_prepare_for_execute_does_not_merge_when_told_not_to(self, upsert_command):
        query = deepcopy(upsert_command.body.meta["query"])

        UpsertCommand.prepare_for_execute([upsert_command], {"merge_query": False})

        assert upsert_command.body.query == query

        for key in query.keys():
            assert key not in upsert_command.body.attributes

    @pytest.fixture(params=[0, 1])
    def upsert_command(self, request, user_command, group_command):
        return [user_command, group_command][request.param]
