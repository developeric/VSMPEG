# Installation

Follow instructions on the [README](https://github.com/rlaPHOENiX/VSMPEG/blob/master/README.md)

# Usage

The most convenient way to use _any_ VapourSynth script right now is with [VapourSynth Editor (aka vs-edit)](https://forum.doom9.org/showthread.php?t=170965).

Open it, drag and drop [vsmpeg.vpy](https://github.com/rlaPHOENiX/VSMPEG/blob/master/vsmpeg.vpy) into it's text editor window, and it will open. It will now open that file location from then on automatically.

Now, just copy config.example.yml as config.yml, and edit it to your liking. Further information on the config options are shown below.

## Previewing

Using vs-edit, you can preview the output of your script like a basic video player. Simply press `[F5]` or clicking `Script`->`Preview` in the menu bar to open the Preview window.

## Encoding

You can encode by using `vspipe` through a Terminal/Command-Prompt/Powershell on the vsmpeg.vpy script, or by pressing `[F8]` or clicking `Script`->`Encode`, in the menu bar of vs-edit.

Both `vspipe` and vs-edit's Encode window allows you to pipe the output of the script to any program at all you wish (as long as that program accepts piped input via stdin).

### With VSPipe

VSPipe is a command-line program allowing you to simply provide a path to a vapoursynth script file and pipe the output to any program that takes in frame data via stdin.

Official Documentation is available here: https://www.vapoursynth.com/doc/vspipe.html

An explanation of the -y/--y4m switch and how to use YUV/RGB is available under Header in the [With VapourSynth-Editor](#with-vapoursynth-editor) section.

### With VapourSynth-Editor

First thing's first, open the Encoding window by pressing `[F8]` or clicking `Script`->`Encode`, in the menu bar of vs-edit.

#### Header

first thing you need to pay attention to is the `Header` dropdown, right now it only has support for `Y4M` (YUV4MPEG). The header is data added to the start of all YUV frame data that allows programs like FFMPEG, x264, e.t.c to more easily understand the incoming data, and adjust itself as needed automatically. Essentially it tells programs what it is, and some metadata about each frame.

If you select `Y4M`, then the script must return a video with a color space from the YUV color space family, e.g. YUV420P8, YUV444P12. If you wish to use another color family like RGB, e.g. RGB24, then you need to set the Header to `No header` and specifically tell the program the format of the incoming piped data.

For example, for RGB24, you can tell FFMPEG `-f rawvideo -pix_fmt gbrp` _before_ `-i -`. However, for that to work you must swap the Planar channel order from R G B (0,1,2), to G B R (1,2,0), which can be done with `clip = core.std.ShufflePlanes(clip, planes=[1,2,0], colorfamily=vs.RGB)`. This is necessary because RGB24 (0,1,2 Planar Order) is not defined as any -pix_fmt by FFMPEG for whatever stupid reason that is. Ideally FFMPEG should be have a -pix_fmt named `rgbp` but it doesn't. But as I said, with a simple Planar re-order, it's possible. Finally I just want to make it clear that this is an FFMPEG problem, not a problem with VapourSynth or VapourSynth-editor.

#### Executable

For the Executable text field, give it the path to the program you wish to pipe data through stdin, e.g. FFMPEG. In a setup where the executable is in your environment path variable, then you could simply put the name of the executable without `.exe` at the end. If it's not in your path just give it the full direct path to the executable (with `.exe`!). I recommend taking the time to use an installer for the executable if available, or put the executable into `C:/Program Files/Program Name` for example, and adding it to your _System_ PATH variable for ease of use from now on. Without the executable in your PATH, it's a lot harder to use it in a terminal/command-prompt.

#### Arguments

Just like in a terminal/command-prompt, here's where you tell the program what you want it to do.
VapourSynth-Editor allows you to add newlines for readability without affecting operation.

Here's a basic example of FFMPEG usage, assuming Y4M header is used. Arguments taken from https://trac.ffmpeg.org/wiki/Encode/H.264

In the Arguments text area:

    -i -
    -c:v libx264
    -preset slow
    -crf 22
    "C:/Users/John/Videos/VSMPEG-out.mp4"

#### Presets

You can now type a name in the "Preset" text field, then hit Save. You can save more pre-sets by simply changing the name in the text field and hitting save again. To edit an existing preset, just keep the name unchange (or use the dropdown to change to a different saved preset, if any), make your edits, and hit save. Pretty semantic if you ask me. You can also delete presets by clicking the Delete button with the unwanted preset selected.

# Variable Documentation (old, latest code may or may not use these)

## DEBUG

### bool

This bool will tell various code functions in this script to print extra additional
information over the frames of the output video. This allows you to learn more
about the input file, as well as make sure the output is what you expect.

This will also print information that will help you if you are decimating.
It will print which offset # the current frame is, which cycle and offsets it's currently
using, and if that frame would be removed when DEBUG is set to False based on the
cycle and offsets currently used. This can help you speed up your decimation.

## Input

### str

Input the file you wish to load here. If you're on Windows, note that paths may use \\
instead of /. If the path has a \\ rather than a /, put r before the start of the path,
e.g. r"C:\\path\\to\\the\\file.mkv".

Tip: Regardless of operating system, you can click a file, press CTRL+C (copy), then
CTRL+V (paste) the file into the "..." string below. What will happen is it will paste
the file path with a `file://` prefix. You don't need to remove the `file://` prefix.

## Deinterlacer

### <tuple>(function: func, arguments: dict)

Only Frames marked as interlaced will run through the selected function.
Functions require the first argument to be the `clip` input, and also require
an argument named `tff` (case in-sensitive).

Items in this `Deinterlacer` list must be a 2-item tuple containing the function
to execute, and any arguments to supply to the function. Arguments to do with
field order (tff/bff) and clip should not be set here, that is handled automatically.

Tip: Make sure any further required arguments for the function you provide is set here
or PDeinterlacer will fail to run the function.

## Decimation

### <tuple>(cycle: int, offsets: <list>[<int>])

Note: To use VDecimate (not recommended: git.io/avoid-tdecimate), set the offsets to an
empty list. When offsets are specified it will use SelectEvery.

## ResetCyclePerVobCell

### bool

Reset the current cycle's offset back to 0 (the start) every time it enters a new vob
cell (if `Input` is to a .VOB file). Even if using a .VOB file, this may not be wanted.
It depends on how the video was had been encoded for the frames you wish to decimate away.
It's wise to verify if it's needed before finalizing you're decimation settings.

Tip: If you set this to False, then apply you're decimation settings, and you notice that
the decimation pattern changes after a while in the video, then this may need to be set
to True. If it still happens, then the hard pulldown used may not have followed a pattern
when they encoded it, or the content itself (e.g. animation) may just be like that. Check
for Fades, Pans & Scans, Transitions, and see if also occurs on those.

## ChromaLocation

### int or None

Position matrix for the value of ChromaLocation:

    ▄▄▄▄▄▄▄▄▄
    █ 2 3 ▪ █
    █ 0 1 ▪ █  `None` == Don't override, hope for the best it's using a good location
    █ 4 5 ▪ █
    ▀▀▀▀▀▀▀▀▀

A value of 1 on a source would be ideal, however Codec spec sheets or SMPTE/ITU recommendation
sheets in some cases stated to use other values, e.g. 0 for MPEG-1 or MPEG-2 Interlaced content.

The problem is this was never ever standardised, so it was fully up to the person in charge
of encoding, or the encoding software what was used. Why is this a problem? It means we don't
know what chroma location was used on the file for sure, as it isn't in the metadata of the file.

A wrong chroma location when viewing the image/video will cause the color to look as if they are
bleeding out of an edge. This isn't to be confused with color droop (where the color is positioned correctly, but may be too wide or tall to fit in its defined position, inside the object).

Tip: It's incredibly hard to notice a color bleed, and even harder on live-action content. Look
for bright pink/purpleish colors, and blood-red, they tend to get compressed the most, and tend
to fuck up in terms of color bleed way easier than any other color, so its easier to notice.

## VSGAN

Super-resolution Generative Adversarial Network (port of ESRGAN). Allows you to use trained
ESRGAN models on each frame of the Input. Chances are you don't need this if you are just
trying to deinterlace a video and get it all good to go. That however doesn't mean it's not
useful.

More info:
<https://github.com/rlaPHOENiX/VSGAN>

Note: VSGAN is applied after everything else. You're clip will be converted to RGB24, and will
return as RGB24 unless you enable "output_yuv", which all it does is convert the RGB24 to YUV420P.
This is necessary as ESRGAN can only work with linear RGB instead of crappy YUV (why the fuck do
videos still use YUV, seriously though??)
