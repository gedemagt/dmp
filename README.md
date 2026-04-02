# DMP

## Get started

1. Install `uv` to manage your python installation following their instructions: https://docs.astral.sh/uv/getting-started/installation/

2. Then install the DMP tool using `uv`
    ```bash
    uv tool install git+https://github.com/gedemagt/dmp
    ```
3. Finally, open the DMP tool from the command line:
    ```bash
    dmp
    ```
## Usage

Add your key-bindings in the top. You add a key (on the left), 
and a corresponding value (essentially what goes into the event)
for short-press and long-press respectively. 

__Note__: `s` is reserved for starting and stopping.

Start/stop a run by pressing the "Start/Stop" button or press the `s` key
on your keyboard.

This starts a timer, and when you press your key-bindings an event is put into the
log.

When you stop the run, the event log is saved as a `.csv` file in
the directory from where you started the DMP tool.