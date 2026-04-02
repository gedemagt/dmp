# DMP

## Installation
To install the DMP tool, the easiest way is to use `uv` - a tool to manage your python installation and tools. 
You can find the installation instructions for `uv` here: https://docs.astral.sh/uv/getting-started/installation/

After installing `uv`, you can install the DMP tool using the following command:
```bash
uv tool install git+https://github.com/gedemagt/dmp
```

## Get started

1. Install `uv` to manage your python installation following their instructions: https://docs.astral.sh/uv/getting-started/installation/

2. Then install the DMP tool using `uv`

3. Finally, open the DMP tool from the command line:
    
## Usage

Open a terminal and run the following command to start the DMP tool:
```bash
 dmp
 ```
First time you will be asked to choose a directory to save your runs. You can change this later.

Next, add your key-bindings in the top. You add a key (on the left), 
and a corresponding value (essentially what goes into the event)
for short-press and long-press respectively. 

__Note__: `s` is reserved for starting and stopping.

Start/stop a run by pressing the "Start/Stop" button or press the `s` key
on your keyboard.

This starts a timer, and when you press your key-bindings an event is put into the
log.

During the run, the event log is auto-saved as a `<start-time>.csv` file in the directory you have chosen.

When you stop the run, you can press `Save As` to save a 
particular run at a custom location.