# VSMPEG

VapourSynth script to automatically handle fields of an MPEG video file to return a Progressive CFR video stream.

[![Python Version](https://img.shields.io/badge/python-3.6%2B-informational?style=flat)](https://python.org)
[![License](https://img.shields.io/github/license/rlaPHOENiX/VSMPEG?style=flat)](https://github.com/rlaPHOENiX/VSMPEG/blob/master/LICENSE)
[![Codacy](https://app.codacy.com/project/badge/Grade/82e2d74e4bdb4f32a98345a114bbb75f)](https://codacy.com/gh/rlaPHOENiX/VSMPEG/dashboard?utm_source=github.com&utm_medium=referral&utm_content=rlaPHOENiX/VSMPEG&utm_campaign=Badge_Grade)
[![Issues](https://img.shields.io/github/issues/rlaPHOENiX/pvsfunc?style=flat)](https://github.com/rlaPHOENiX/VSMPEG/issues)
[![PR's Accepted](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)](https://makeapullrequest.com)

* * *

## Installation

### Important Information on how to efficiently use and update VSMPEG

To make everything very simple in terms of some later installation steps and updating steps, I recommend using [git](https://git-scm.com) (CLI) or [GitHub Desktop](https://desktop.github.com) (GUI) to clone (download) the Git repo to your system. This makes it a lot easier to update VSMPEG when there's changes (`git pull` via cli or click "Pull Origin" in GitHub Desktop, when available). VSMPEG does not use a releases or versioning system, think of the master/main branch as being the latest version all the time, any new commits should be used ASAP.

Any updates to `config.example.yml` should be manually looked at to understand the changes between your current config.yml and the new changes. Always check the related commit's Title and Description (if any) as it may include information on why or what was changed. We cannot guarantee that the config file's structure or values don't change over time, if we did it could be very restricting against further updates or improvements to VSGAN. GitHub Desktop has a History tab which will show you the commits which you can click through and see changes to config.example.yml, or on GitHub itself see the [Commit History of config.example.yml](https://github.com/rlaPHOENiX/VSMPEG/commits/master/config.example.yml). **It is up to YOU to remember to check for, and apply, any updates to the config file.**

### Dependencies

Install dependencies in the listed order:

1.  [Python](https://python.org) 3.6+ and [pip](https://pip.pypa.io/en/stable/installing). The required pip packages are listed in the [requirements.txt](https://github.com/rlaPHOENiX/VSMPEG/blob/master/requirements.txt) file.
2.  [VapourSynth](https://vapoursynth.com). Ensure the Python version you have installed is supported by the version you are installing. The supported Python versions may differ per OS.
3.  That's all the dependencies VSMPEG directly requires. However, you may need to follow the dependencies listed by [pvsfunc](https://github.com/rlaPHOENiX/pvsfunc#dependencies) which is a pivotal component of VSMPEG.

### Installing Python and VapourSynth

1.  Ensure the Python version you have installed (or are going to install) is supported by the version of VapourSynth you are installing. The supported Python versions in correlation to a VapourSynth version may differ per OS, noticeably on Windows, due to it's Python environment in general.
2.  When installing Python and VapourSynth, you will be given the option to "Install for all users" by both. Make sure you're chosen answer matches for both installations or VapourSynth and Python wont be able to find each other.

Important note for Windows users: It is very important for you to tick the checkbox "Add Python X.X to PATH" while installing. The Python installer's checkbox that states "Install launcher for all users", is not referring to the Python binaries. To install for all users, you must click "Customize installation" and in there, after "Optional Features" section, it will have a checkbox titled "Install for all users" unticked by default, tick it.

### Installing the required pip packages

Use Terminal/Command-Prompt/PowerShell to navigate to the downloaded (or cloned) location (e.g. `cd C:/Users/John/Documents/VSMPEG`) and then run `pip install -r requirements.txt`.

Note: I do not recommend running pip install with administrator permission!

### pvsfunc and it's dependencies

[pvsfunc](https://github.com/rlaPHOENiX/pvsfunc#dependencies) is used all over VSMPEG, in fact, VSMPEG is realistically just a wrapper for pvsfunc, an example use-case of pvsfunc. This means you must make sure to install any needed dependencies for pvsfunc.

Go to the Dependencies section of `pvsfunc`'s README and read what is needed for what file you are trying to work with. From there, the README will also provide instructions on how to install them. If you need the dependency but don't have it (as you didn't realise you needed it for your input file), then pvsfunc (and therefore VSMPEG) will error out and tell you what is needed to be installed, so don't worry too much.

* * *

## Brief Introduction to VapourSynth and VapourSynth Script (.vpy) files

"A video processing framework with simplicity in mind"—[VapourSynth Project](https://github.com/vapoursynth/vapoursynth)

To add more to that, it's a _Script-based_ NLE ([Non-linear editing system](https://wikipedia.org/wiki/Non-linear_editing_system)).

It's not GUI software rather a scripting framework for videos that uses the [Python programming language](https://wikipedia.org/wiki/Python_(programming_language)).

VapourSynth Script files use the .vpy extension (revision on .py being the Python script extension).

### Wait, No GUI?! That must be painful!

For your typical YouTube video it's unconventional yes, but that isn't the goal of a project like this. A Script-based NLE is scripted to handle a specific use case, and be able to be utilised by other programs like GUI editors, video players, hardware players, and such.

You won't need you're YouTube video's edits to be reproducable automatically on other people's PC's, but an edit like filtering colors, stabilization algorithms, machine learning edits, deinterlacing, e.t.c would be. You can generally think of VapourSynth as a framework for plugin creation, though it's extremely versatile and portable and not locked to one program but can be used by any program (as long as it supports it).

This project (VSMPEG) is a great example of a use-case of VapourSynth as it deals with the shenanigans of MPEG video entirely automated (depending on the optional stuff you enable/want to do). This script isn't realtime right now, even on high-end hardware, however, if it becomes the case of the deinterlacing algorithms to shrink in processing time or hardware to improve, this script could be used in realtime as sort of an intermediate layer or plugin to automatically handle DVD playback automatically without any configuration by the user. That would be awesome.

* * *

## Usage

### With VapourSynth-Editor (aka vs-edit)

[VapourSynth-Editor (vs-edit)](https://forum.doom9.org/showthread.php?t=170965) is an IDE for VapourSynth Script files. It integrates convenient features like a full fledged previewing system, a Syntax-highlighter, auto-completion, benchmarking, and more.

This saves you ton's of headaches of using VapourSynth from the command line, especially the previewing system! The previewing system alone makes this project worth using, however, it does bring problems like 2x memory usage when unnecessary which causes a memory leak once you start refreshing the preview buffer a few times ([See issue #644](https://github.com/vapoursynth/vapoursynth/issues/644)). The project also seems like it has been abandoned or at the very least inactive for quite some time.

It's been inactive for so long that a fork project has been created known as "VapourSynth Editor 2" (what a bad name honestly). This also seems fairly inactive, or at least slow in development right now. It has great aspirations, but the slow development and odd way they are doing public testing ([Release candidates](https://en.wikipedia.org/wiki/Software_release_life_cycle#Release_candidate)) is often odd and unsafe as they only release them as compiled Windows binaries without the source code being provided.

Even with all the problems in relation to VapourSynth IDE projects, they are still very much useful whichever you wish to use. Personally right now I recommend using the original VapourSynth Editor as it is generally more stable and is less intimidating UI-wise, with very handy features that the fork has removed.

Alright, let's get to using it, once installed open it up and simply drag and drop the `vsmpeg.vpy` file from your downloaded (or cloned) folder into VapourSynth-Editor. Try not to move the file location any further so that VapourSynth-Editor can find and open the file when re-opened.

You can edit vsmpeg.vpy from here to do whatever you wish, but do remember that updating via `git pull` or GitHub Desktop will want you to remove your local changes so it doesnt conflict with the latest changes on the VSMPEG GitHub repository.

For configuring the pre-made code in a noob-proof way, copy the config.example.yml as config.yml, open it in a YAML syntax supported editor (Visual Studio Code, notepad++, e.t.c), and edit away the options. The config.yml has more information on how to configure and what the options are and do.

From here, feel free to use the full feature set of VapourSynth-Editor, like the Previewing (`F5`), Benchmarking (`F7`), and Encoding (`F8`) features.
