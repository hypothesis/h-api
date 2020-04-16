# h-api

Tools and components for calling the H API

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

Hacking
-------

### Installing h-api in a development environment

#### You will need

* [Git](https://git-scm.com/)

* [pyenv](https://github.com/pyenv/pyenv)
  Follow the instructions in the pyenv README to install it.
  The Homebrew method works best on macOS.
  On Ubuntu follow the Basic GitHub Checkout method.

#### Clone the git repo

```terminal
git clone https://github.com/hypothesis/h-api.git
```

This will download the code into a `h-api` directory
in your current working directory. You need to be in the
`h-api` directory for the rest of the installation
process:

```terminal
cd h-api
```

#### Run the tests

```terminal
make test
```

**That's it!** You’ve finished setting up your h-api
development environment. Run `make help` to see all the commands that're
available for linting, code formatting, packaging, etc.

### Updating the Cookiecutter scaffolding

This project was created from the
https://github.com/hypothesis/h-cookiecutter-pypackage/ template.
If h-cookiecutter-pypackage itself has changed since this project was created, and
you want to update this project with the latest changes, you can "replay" the
cookiecutter over this project. Run:

```terminal
make template
```

**This will change the files in your working tree**, applying the latest
updates from the h-cookiecutter-pypackage template. Inspect and test the
changes, do any fixups that are needed, and then commit them to git and send a
pull request.

If you want `make template` to skip certain files, never changing them, add
these files to `"options.disable_replay"` in
[`.cookiecutter.json`](.cookiecutter.json) and commit that to git.

If you want `make template` to update a file that's listed in `disable_replay`
simply delete that file and then run `make template`, it'll recreate the file
for you.
