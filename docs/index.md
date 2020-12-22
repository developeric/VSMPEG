# Installation

Follow instructions on the [README](https://github.com/rlaPHOENiX/VSMPEG/blob/master/README.md)

# Usage

The most convenient way to use *any* VapourSynth script right now is with [VapourSynth Editor (aka vsedit)](https://forum.doom9.org/showthread.php?t=170965).

Open it, drag and drop [vsmpeg.vpy](https://github.com/rlaPHOENiX/VSMPEG/blob/master/vsmpeg.vpy) into it's text editor window, and it will open. It will now open that file location from then on automatically.

All the variables you see before this line:

    # /!\ Do not edit beyond here unless you know what your doing /!\

Can safely be edited as long as you read information next to that variable, and in this document below.

## Previewing

Once you have edited the variables to your liking, preview and check everything by pressing `[F5]` or clicking `Script`->`Preview`, in the menu bar.

## Encoding

You can encode by using `vspipe` through a Terminal/Command-Prompt/Powershell on the vsmpeg.vpy script, or by pressing `[F8]` or clicking `Script`->`Encode`, in the menu bar of vs-edit.

Both `vspipe` and vs-edit's Encode window allows you to pipe the output of the script to any program at all you wish (as long as that program accepts piped input via stdin).

Here's a quick example of encoding with ffmpeg:

Make sure you're script returns a YUV video, and that you set the `Header` dropdown to `Y4M` (yuv4mpeg), otherwise you will need to tell FFMPEG -f rawvideo and the -pix_fmt that the script is returning, making sure the -pix_fmt's channel count and channel order is correct.

For the Executable text field, give it the path to FFMPEG. In a setup where the ffmpeg executable is in your environment path variable, then you could simply put `ffmpeg` (the name of the executable, .exe isn't needed). If it's not in your path (I recommend doing so), otherwise just give it the full direct path to the ffmpeg.exe.

In the Arguments text area:

    -i -
    -preset medium
    -profile high
    -level 4.1
    -refs 6
    -crf 18
    "out.mp4"

Give it a name in the Preset text field, and hit save to re-use it later.

Go ahead and click Start now :)

# Variable Documentation

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

Input the file you wish to load here. If you're on Windows, note that paths may use \
instead of /. If the path has a \ rather than a /, put r before the start of the path,
e.g. r"C:\path\to\the\file.mkv".

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
https://github.com/rlaPHOENiX/VSGAN

Note: VSGAN is applied after everything else. You're clip will be converted to RGB24, and will
return as RGB24 unless you enable "output_yuv", which all it does is convert the RGB24 to YUV420P.
This is necessary as ESRGAN can only work with linear RGB instead of crappy YUV (why the fuck do
videos still use YUV, seriously though??)
