"""A value object for returning database modification results."""


class Report:  # pylint: disable=too-few-public-methods
    """A model for reporting the result of database modification."""

    def __init__(self, id_, public_id=None):
        """Create a report.

        :param id_: The id of the updated resource
        :param public_id: The user friendly id of the resource
        :raise ValueError: If the id is None
        """
        if id_ is None:
            raise ValueError("id_ is required for successful outcomes")

        self.id = id_  # pylint: disable=invalid-name
        self.public_id = id_ if public_id is None else public_id

    def __repr__(self):
        return f"<{self.__class__.__name__}: '{self.id}' ({self.public_id})>"
