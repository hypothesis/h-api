"""Implementations of an 'Observer' which is informed of commands."""


import json

from h_api.enums import CommandStatus


class Observer:
    """A callback for being informed of every command processed by BulkJob.

    This implementation serves as the base class and takes no action when
    informed of a command.
    """

    def observe_command(self, command, status):
        """Take any required action when provided with a command.

        A call back for various stages in the command life cycle.

        :param command: Command being inspected
        :param status: Status of the command
        """
        pass


class SerialisingObserver(Observer):
    """An Observer which serialises commands to provided handle."""

    def __init__(self, handle):
        """Create the observer.

        :param handle: A file like object
        """
        self.handle = handle

    def observe_command(self, command, status):
        """Write all commands the handle as JSON."""

        if status != CommandStatus.AS_RECEIVED:
            return

        # By this point we've done so much validation it should be basically
        # impossible for this to not serialise.
        self.handle.write(json.dumps(command.raw) + "\n")
