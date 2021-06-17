# VSMPEG

Boilerplate VapourSynth script that handles a few common operations. It internally uses [pvsfunc] to handle scan, vfr,
and vst.

[![Build Tests](https://img.shields.io/github/workflow/status/rlaPHOENiX/VSMPEG/Version%20test?label=Python%203.6%2B%20builds)](https://github.com/rlaPHOENiX/VSMPEG/actions?query=workflow%3A%22Version+test%22)
[![License](https://img.shields.io/github/license/rlaPHOENiX/VSMPEG?style=flat)](https://github.com/rlaPHOENiX/VSMPEG/blob/master/LICENSE)
[![DeepSource](https://deepsource.io/gh/rlaPHOENiX/VSMPEG.svg/?label=active+issues)](https://deepsource.io/gh/rlaPHOENiX/VSMPEG/?ref=repository-badge)
[![Tip Me via Bitcoin](https://img.shields.io/badge/Bitcoin-tip%20me-f7931a.svg?logo=bitcoin)](https://raw.githubusercontent.com/rlaPHOENiX/VSMPEG/master/docs/assets/images/19LMDTZhwuiELUPbpj1wrnBKPZpDj699Mk.webp)

## Installation

Requires [Python] 3.6+ and [VapourSynth] ([C Libraries], not the PyPI/PIP package).

`pip install -r requirements.txt`

From here, there's optional dependencies based on the files you intend to use VSMPEG with. See the dependencies list
on the [pvsfunc] README.

  [C Libraries]: <https://www.vapoursynth.com/doc/installation.html>

### Installing Python and VapourSynth

Ensure the Python version you have installed (or are going to install) is supported by the version of VapourSynth
you are installing. The supported Python versions in correlation to a VapourSynth version may differ per OS,
notably on Windows due to its Python environment in general.

When installing Python and VapourSynth, you will be given the option to "Install for all users" by both. Make sure
your chosen answer matches for both software or VapourSynth and Python won't be able to locate each other.

### Installing the required pip packages

Use Terminal to navigate to the downloaded (or cloned) location (e.g. `cd C:/Users/John/Documents/VSMPEG`) and then
run `pip install -r requirements.txt`.

Note: I do not recommend running `pip` with administrator permission!

### pvsfunc and it's dependencies

[pvsfunc] is used all over VSMPEG, in fact, VSMPEG is really just
a wrapper for pvsfunc; an example use-case of pvsfunc. This means you must make sure to install any needed
dependencies for pvsfunc.

Go to the Dependencies section of [pvsfunc]'s README and see what is needed for the input file you are working with.
From there, the README will also provide instructions on how to install them. If you need the dependency but don't
have it, then pvsfunc (and therefore VSMPEG) will error out and tell you what is needed to be installed.

## Usage

This is a brief explanation of usage of VSMPEG, more verbose information and other ways of using VSMPEG can be found
on the documentation below.

### With VapourSynth-Editor (aka vs-edit)

[VapourSynth Editor] is an IDE for VapourSynth Script files. It integrates convenient features like a full-fledged
previewing system, a Syntax-highlighter, auto-completion, benchmarking, and more.

This saves you ton's of headaches of using VapourSynth from the command line, especially the previewing system.
The previewing system alone makes this project worth using.

Once installed open it up and simply drag and drop the `vsmpeg.vpy` file from your downloaded (or cloned) folder
into VapourSynth Editor. Try not to move the file location any further so that VapourSynth-Editor can find and open
the file when re-opened.

You can edit `vsmpeg.vpy` from here to do whatever you wish. See how stuff is done, remove stuff, add stuff, whatever.

For configuring the pre-made code in a noob-proof way, copy the config.example.yml as config.yml, open it in a YAML
syntax supported editor (e.g. Visual Studio Code), and edit away the options. The config.yml has more information on
how to configure and what the options are and do.

From here, feel free to use the full feature set of VapourSynth-Editor, like Previewing (`F5`), Benchmarking (`F7`),
and Encoding (`F8`).

## Documentation

You can view the documentation at <https://rlaphoenix.github.io/VSMPEG> or in the [/docs] folder.

## Introduction to VapourSynth and VapourSynth Script (.vpy) files

"A video processing framework with simplicity in mind"—[VapourSynth]

To add more to that, it's a _Script-based_ NLE ([Non-linear editing system]).

It's not GUI software rather a scripting framework for videos that uses the [Python programming language].

VapourSynth Script files use the `.vpy` file-extension (play on `.py` being the Python script extension).

### Why Script-based editors are a thing, when conventional GUI editors exist

For your typical YouTube video editing, it's unconventional, yes, but that isn't the goal of a project like this.
A Script-based NLE is scripted to handle a specific use case, and be able to be utilised by other programs like GUI
editors, video players, hardware players, and such.

You won't need you're YouTube video's edits to be reproducible automatically on other people's PC's or source files,
but a script that is for filtering colors, stabilization, machine learning, deinterlacing, e.t.c would be.

You can generally think of VapourSynth as a framework for plugin creation, though it's extremely versatile and
portable and not locked to one program but can be used by any program (as long as it supports it).

This project (VSMPEG) is a great example of a use-case of VapourSynth as it deals with the shenanigans of MPEG video
entirely automated (depending on the optional stuff you enable/want to do). This script isn't realtime right now,
even on high-end hardware. However, if it becomes the case of the deinterlacing algorithms to shrink in processing
time or hardware to improve, this script could be used in realtime as a sort of intermediate layer or plugin to
automatically handle MPEG-1 and MPEG-2 (e.g. DVD) playback automatically without any configuration by the user.
That would be awesome!

## Troubleshooting

### Failed to initialize VapourSynth environment!

The application you are using (e.g. [VapourSynth Editor], vs-pipe) cannot find the VapourSynth library.
Either you have only installed via `pip install vapoursynth`, and not installed the local C library or have
installed the VapourSynth C library under a different Python version or Environment.

Fix:
Follow ["Installing Python and VapourSynth"](#installing-python-and-vapoursynth).
You _might_ need to fully uninstall the current Python and VapourSynth installation.


  [Python]: <https://python.org>
  [VapourSynth]: <https://vapoursynth.com>
  [pvsfunc]: <https://github.com/rlaPHOENiX/pvsfunc>
  [VapourSynth Editor]: <https://forum.doom9.org/showthread.php?t=170965>
  [Non-linear editing system]: <https://wikipedia.org/wiki/Non-linear_editing_system>
  [Python programming language]: <https://wikipedia.org/wiki/Python_(programming_language)>
  [/docs]: <https://github.com/rlaPHOENiX/VSMPEG/blob/master/docs/index.md>
