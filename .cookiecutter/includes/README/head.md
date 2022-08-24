
This package is not likely to be of use to you
----------------------------------------------

Unless you work for Hypothesis, then this package is not going to be very
useful to you. Feel free to have a poke about, but don't be surprised if it
doesn't make much sense.

At the present time not only should you not use this package, our 
authentication will also prevent it.

Usage
-----

To construct NDJSON for Bulk API calls:

```python
from h_api.enums import ViewType

from h_api.bulk_api import CommandBuilder, BulkAPI, Executor

nd_json = BulkAPI.to_string([
    # It's your job to put the right commands here. 
    # This also accepts a generator

    CommandBuilder.configure(
        effective_user="acct:example@lms.hypothes.is", 
        total_instructions=4, 
        view=ViewType.BASIC),

    CommandBuilder.user.upsert({
        "username": "username",
        "authority": "authority",
        "display_name": "display_name",
        "identities": [{
            "provider": "provider",
            "provider_unique_id": "provider_unique_id"
        }],
    }, "user_ref"),

    CommandBuilder.group.upsert({
        "name": "name",
        "authority": "authority",
        "authority_provided_id": "authority_provided_id"
    }, "group_ref"),
    
    # These references here match those we assigned to the objects above
    CommandBuilder.group_membership.create("user_ref", "group_ref")
])

# It's now your job to send this off to H
```

To accept and process an NDJSON request like the above:
```python
class MyExectutor(Executor):
    def execute_batch(self, command_type, data_type, default_config, batch):
        """Implement your insertion logic here and return Report Objects"""
        
rows = BulkAPI.from_byte_stream(http_streaming_body, executor=MyExectutor())

if rows:
    # Turn each row into JSON and return to your caller
    # You have to do this
```
