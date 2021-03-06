from h_matchers import Any

from h_api.enums import DataType
from h_api.model.json_api import JSONAPIData, JSONAPIError, JSONAPIErrorBody


class TestJSONAPIErrorBody:
    def test_create(self):
        meta = {"metadata": 1}
        body = JSONAPIErrorBody.create(
            KeyError("message"),
            title="title",
            detail="detail",
            pointer="_pointer",
            status=200,
            meta=meta,
        )

        assert isinstance(body, JSONAPIErrorBody)
        assert body.raw == {
            "code": "KeyError",
            "title": "title",
            "detail": "detail",
            "meta": meta,
            "source": {"pointer": "_pointer"},
            "status": "200",
        }

        assert body.detail == "detail"

    def test_degenerate_create(self):
        body = JSONAPIErrorBody.create(KeyError("message"))

        assert body.raw == {"code": "KeyError", "title": "message"}

        assert body.detail is None


class TestJSONAPIError:
    def test_create(self):
        body = JSONAPIErrorBody.create(KeyError("message"))
        error = JSONAPIError.create([body, body])

        assert isinstance(error, JSONAPIError)

        assert error.raw == {"errors": [body.raw, body.raw]}


class TestJSONAPIData:
    def test_create(self):
        attributes = {"attrs": 1}
        meta = {"some_meta": "value"}
        relationships = {"rel_type": {"data": {"type": "foo", "id": "1"}}}

        data = JSONAPIData.create(
            DataType.GROUP,
            "my_id",
            attributes=attributes,
            meta=meta,
            id_reference="my_ref",
            relationships=relationships,
        )

        assert isinstance(data, JSONAPIData)
        data_block = {
            "type": "group",
            "id": "my_id",
            "attributes": attributes,
            "meta": meta,
            "relationships": relationships,
        }

        assert data.raw == {"data": data_block}

        assert data.id == "my_id"
        assert data.type == DataType.GROUP
        assert data.meta == {"some_meta": "value", "$anchor": "my_ref"}
        assert data.attributes == attributes
        assert data.relationships == relationships
        assert data.id_reference == "my_ref"

    def test_degenerate_create(self):
        data = JSONAPIData.create("group")

        assert data.raw == {"data": {"type": "group"}}

    def test_create_with_id_reference_but_no_meta(self):
        data = JSONAPIData.create("group", id_reference="ref")

        assert data.raw == {"data": Any.dict.containing({"meta": {"$anchor": "ref"}})}
