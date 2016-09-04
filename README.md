# streamplt
A set of utility scripts to run streaming matplotlib visualizations.
Depends on ZMQ for the communication.

## Examples

### StreamLinePlot

Start up a streaming plot:

```bash
python -m streamplt.line_plot
```

By default the StreamLinePlot will be listening on `ipc:///tmp/stream`.
You can change this with the command line arg, `--address`.
From a separate terminal, start a client pushing random walk data to `/tmp/stream`:

```bash
python -m streamplt.test_client
```
