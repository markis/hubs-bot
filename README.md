# Hubs-bot - Hub Times Bot for r/HudsonOH

This bot will periodically check the front page of the hub times and grab any story explicitly declared as being part of the Hub Times, then post it to r/HudsonOH.

### Development

`make` will setup the environment and create a python virtual environment.

```console
  $ make
```

`make test` will run the test suite

```console
  $ make test
```

Running the project locally requires setting some environment variables. A sample `.envrc` file is provided in the project. Copy `.envrc.sample` to `.envrc` and update the environment variables.

```console
  $ cp .envrc.sample .envrc
```
