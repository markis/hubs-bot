# Hubs-bot - hub times bot for r/HudsonOH

This bot will check periodically check the front page of the hub times and grab any story explicitly declared as being part of the hub times.

### Development

`make build` will setup the environment and create a python virtual environment.

```console
  $ make build
```

`make test` will run the test suite

```console
  $ make test
```

Running the project locally requires the setting some environment variables. A sample `.envrc` file is provided in the project. Copy `.envrc.sample` to `.envrc` and update the environment variables.

```console
  $ cp .envrc.sample .envrc
```
