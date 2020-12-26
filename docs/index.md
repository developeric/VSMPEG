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

Official Documentation is available here: <https://www.vapoursynth.com/doc/vspipe.html>

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

Here's a basic example of FFMPEG usage, assuming Y4M header is used. Arguments taken from <https://trac.ffmpeg.org/wiki/Encode/H.264>

In the Arguments text area:

    -i -
    -c:v libx264
    -preset slow
    -crf 22
    "C:/Users/John/Videos/VSMPEG-out.mp4"

#### Presets

You can now type a name in the "Preset" text field, then hit Save. You can save more pre-sets by simply changing the name in the text field and hitting save again. To edit an existing preset, just keep the name unchange (or use the dropdown to change to a different saved preset, if any), make your edits, and hit save. Pretty semantic if you ask me. You can also delete presets by clicking the Delete button with the unwanted preset selected.

# Config File Documentation

## Verbose (bool)

This bool will tell various code functions in this script to print extra additional information over the frames of the output video. This allows you to learn more about the input file, as well as make sure the output is what you expect.

This will also print information that will help you if you are decimating. It will print which offset # the current frame is, which cycle and offsets it's currently using, and if that frame would be removed when Verbose is set to False based on the cycle and offsets currently used. This can help you speed up your decimation.

## Input (str)

Input the file you wish to load here.

Tip: Regardless of operating system, you can click a file, press CTRL+C (copy), then
CTRL+V (paste) the file into the "..." string below. What will happen is it will paste
the file path with a `file://` prefix. You don't need to remove the `file://` prefix.

## Deinterlacers (dict object)

This is a dictionary mapping of deinterlacer functions and their arguments (and how to import them) for use with PDeinterlacer. It's important the Environment keys are set up so that VSMPEG can actually get the function wanted. Make sure what you're telling VSMPEG to import is installed and available on your system.

Each deinterlacer in this dictionary, is using the following structure:

    # the function name will be the attribute of what you import
    # e.g. if Function_Name is `QTGMC` and Environment is `Import: havsfunc`
    # then it will be doing: `getattr(havsfunc, "QTGMC")` which is === `havsfunc.QTGMC`.
    VoidWeave:
        Environment:
            # for example `from pvsfunc.pdeinterlacer import PDeinterlacer`:
            From: pvsfunc.pdeinterlacer
            Import: PDeinterlacer
            # for example `import havsfunc`:
            #Import: havsfunc
        # the arguments to send to the function when used, can be replaced with Args: ~ to use no arguments
        Args:
            color: [0, 255, 0]
            bob: false

## Deinterlacer (str, None)

This is where you choose which deinterlacer from the list you wish to use. This value should be the function name from the list (the dictionary key). Make sure the import that the chosen Deinterlacer's Environment states, is available on your system.

You can set it to ~ (None in YAML) to disable deinterlacing, however, that is in no way recommended. Deinterlacing will only occur on frames marked in the metadata as interlaced, so you're progressive frames are safe.

## Decimation (dict object)

### Enabled (bool)

Whether to Decimate or not.

### Cycle (int)

Decimation Cycle, essentially chunking the clip into n frames for evaluation with the offset list below.

### Offsets (List[int], None)

Decimation Offsets, which frames to keep from the cycle. 0-indexed.

Note: To use VDecimate (not recommended: git.io/avoid-tdecimate) instead of SelectEvery, set the offsets to an empty list. When offsets are specified it will use SelectEvery.

### ResetCyclePerVobCell (bool)

Reset the current cycle's offset back to 0 (the start) every time it enters a new vob cell (if `Input` is to a .VOB file). Even if using a .VOB file, this may not be wanted. For example if you are decimating to remove hard pulldown, some videos may have had the hard pulldown applied seperately to each VOB cell, and some might have had it applied to the entire source video at once, then separated into VOB Cells afterwards (uncommon though). It's wise to verify if it's needed before finalizing you're decimation settings.

Tip: If you set this to False, then apply you're decimation settings, and you notice that the decimation pattern changes after a while in the video, then this may need to be set to True. If it still happens, then the duplicate frames or the frames you wish to remove don't follow the pattern you may expect, or perhaps don't follow a pattern at all. Perhaps the content is just like that. Checking for Fades, Pans & Scans, Transitions, and see if it has the fade or transition changing every frame. If it does change, then the video probably isn't supposed to be decimated (at least for the pattern you're providing).

## ChromaLocation (int, None)

Position matrix for the value of ChromaLocation:

    ▄▄▄▄▄▄▄▄▄
    █ 2 3 ▪ █
    █ 0 1 ▪ █  `None` == Don't override, hope for the best it's using a good location
    █ 4 5 ▪ █
    ▀▀▀▀▀▀▀▀▀

This value is not standardised in any way, as in, there's no one value you HAVE to use in a situation, ANY can be used. However, the value is NOT stored in the metadata making it VERY difficult to figure out which one to use when playing back the video. Due to this, ITU and SMPTE started to give out recommended values based on Codec and other metadata like Scan type, however, these recommendation documents are usually paywalled so I cannot give you a list (unless someone finds it and can make a Pull request or tell me via a GitHub Issue where one can see a list of the values from a reputable source).

A wrong chroma location when viewing the image/video will cause the color to look as if they are bleeding out of an edge, and can cause the color at an edge of the video to be lost forever and look Gray. This isn't to be confused with color droop (where the color is positioned correctly, but may be too wide or tall to fit in its defined position, inside the object), but can usually be a closely related issue.

Tip: It's incredibly hard to notice a color bleed, and even harder on live-action content. Look for bright pink/purpleish colors, and blood-red, they tend to get compressed the most, and tend to mess up in terms of color bleed way easier than any other color, so its easier to notice.

[Example](https://slow.pics/c/6W2HO16L) and it's problems:

-   Bad chroma location being used. It was encoded with a chroma location that differs to the most popular MPEG-2 recommendation of 0 (center left). Possibly encoded with a chroma location of 2 (top left).
-   Has a slight color droop in specific parts of the image, e.g. Lois's orange hair, Lois's red lips, The top of the door frame.

A TON more information on Chroma Location and Subsampling is available here:

-   <http://avisynth.nl/index.php/Sampling#mpeg-1_versus_mpeg-2_sampling> (goes in depth, and also links to sources of the information)
-   <https://www.pcmag.com/encyclopedia/term/chroma-subsampling> (visually shows the chroma location positioning for various YUV color space formats, but doesn't link to their sources)

## Debox (dict object)

### Enabled (bool)

Whether to Debox or not.

### Operations (List[tuple(axis str, aspect str, offset int)])

These tell PDebox to remove Pillarboxing or Letterboxing in specific orders, as many times as you define.

Axis (str): This is which resolution direction it crops aka Pillarboxing or Letterboxing. `w` for Pillarboxing, `h` for Letterboxing.

Aspect (str): This is the aspect ratio you wish to crop to. It MUST be a smaller aspect ratio than the current aspect ratio on the chosen Axis. E.g. if a source is 16:9 1920x1080, and you use Axis of `w` (Pillarboxing) and want to crop to 1440x1080, you would use the aspect of `4:3`.

Offset (int): If there's more boxing on one side than the other, you can use the offset to adjust the weight of the crop on either side of the axis. It cannot be a float, it must be an integer, but it can be a negative integer to put weight on the left-most side of the axis.

## Crop (dict object)

### Enabled (bool)

Whether to Crop or not.

### Left (int), Right (int), Top (int), Bottom (int)

How much to crop from that axis. It cannot be a float. The resulting crop may need to be mod2 and such, depending on the clip's format. I cannot control this, it is checked by VapourSynth itself (and yes I'm aware it's stupidly annoying and possibly obstructive).

## AspectRatio (dict object)

### Value (str, None)

This is to define what Aspect Ratio you want to resize you're clip to.

-   `~` (None): keep it at whatever it loaded in with, as in, do nothing and skip.
-   `DAR`: Use the Display Aspect Ratio (what aspect ratio a Player software or Hardware would display it as).
-   e.g. `16:9` (Specific Aspect Ratio string): Use a specific Aspect Ratio.

### Axis (str)

Which axis (`width` or `height`) to resize to obtain the chosen Aspect Ratio (if chosen). I recommend width for most use cases. However, it's really just specific to what you need. If you're not sure which to use, then you could just use `~` (to disable) and when encoding, use the encoder software's Display Aspect Ratio (Possibly named PAR or SAR, it's a confusing mess, would take too long to explain why) argument to specify the wanted Display Aspect Ratio. This gives the benefit of smaller file size, smaller bitrates (allowing further device support) and less overall pixels to play back which would use less resources.

### Kernel (func)

Which Resize Kernel to use for the resize process. This has to be a function readily available in [core.resize](https://vapoursynth.com/doc/functions/resize.html). The value is case-sensitive and must be exactly the same as the function name.

Example's and the use case:

-   [Point](https://en.wikipedia.org/wiki/Nearest-neighbor_interpolation): aka Nearest neighbor or NN, is a simple linear algorithm that essentially duplicates pixels when needed to fit the size. This would be used for anything you want to keep pixelated, like old NES game screenshots or gameplay, Pixel-art, QR-codes, e.t.c. It's important however that the content you are resizing with Point is also pixelated still and not blurry (e.g. by being resized previously with another non-linear algorithm), or you may get odd results.
-   [Bilinear](https://en.wikipedia.org/wiki/Bilinear_interpolation) and [Bicubic](https://en.wikipedia.org/wiki/Bicubic_interpolation): These are non-linear interpolation algorithms that are much nicer to look at on anything that would be blurry or generally anything that isnt pixelated or animated. Bicubic tends to look sharper but may result in halo'ing/glow/ringing artifacts around edges.
-   [Lanczos](https://en.wikipedia.org/wiki/Lanczos_algorithm): This one is not recommended, it is known for creating sharper images than Bicubic, but is notorious for creating halo'ing/glow/ringing artifacts around edges. It's also common advice to not use this on anything that would be even a small bit noisy (either by compression, or by FILM grain).
-   [Spline16, 32, and 64](https://en.wikipedia.org/wiki/Spline_interpolation): These are non-linear cubic spline-based interpolation algorithms that is cubic like Bicubic, however, tries to be as sharp as possible, but with less halo'ing/glow/ringing artifacts. Each incrementation of the 16/32/64 are the "Taps", the higher the Taps count, the more accurate but slow and resource intensive it will be. It's essentially the benefits of Lanczos, with the artifact'ness level of Bicubic give or take.

More algorithm's and information:

-   <https://www.vapoursynth.com/doc/functions/resize.html>
-   <http://avisynth.nl/index.php/Resize>

## VSGAN (dict object)

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

### Enabled (bool)

Whether to run VSGAN or not.

### Comparer (func)

You can use functions to compare the before and after of VSGAN. It must be a function readily available in `core.std`. A list of functions in `core` can be found [here](https://vapoursynth.com/doc/functions.html). I cannot find a page that lists only the ones available in core.std.

Regardless, there's really only two that matter:

-   [Interleave](https://vapoursynth.com/doc/functions/interleave.html): Will alternate between Before and After.
-   [StackHorizontal](https://vapoursynth.com/doc/functions/stack.html): Will show the Before on the left and After on the right, both at the same time in the same frame. The smallest resolution of the two will be resized to the biggest for the fairest comparison. There's also StackVertical but what kind of psychopath would use that for comparing.

### ConvertColorSpace (dict object)

#### Enabled (bool)

Wheter to convert the color space or leave it as RGB24. Since VSGAN HAS to convert the input to RGB24, and return as RGB24, you may want to convert that to something else.

**Note: Converting from RGB->YUV or YUV->RGB is lossy, so I recommend doing this only when absolutely necessary, e.g. encoding to a video file, as the encoder would have to convert to YUV anyway, so might as well have VapourSynth do it instead of the encoder.**

#### Format (str)

This should be any of the following values: <https://vapoursynth.com/doc/pythonreference.html#format-constants>
Just note, only YUV420P8 has really been tested. It's incredibly difficult to know how you wish to convert the color format just by which color format you want, there's lots more that is usually invovled especially for YUV, like Chroma Subsampling, Matrix, e.t.c. Everything like that is going to be assumed and estimated based on the input clip. So be warned. Feel free to look at the code (near the very end of the VSGAN related code in vsmpeg.vpy to see how it's doing it, and if needed, contribute any fixes or estimation improvements).

### Operations (List[dict])

These tell VSGAN what models you want to run, and how you want to prepare the input each run.
It does each run in the order of top to bottom.

#### enabled (bool)

Each operation can be enabled or disabled at will for easy testing of chaining runs.

#### model (str)

Same possibilites as `Input`. This should be a path to a .pth model file that was trained for ESRGAN.

#### device (str, int)

PyTorch device string, there's many possibilities for values here but typical values are `cpu`, `cuda`, `0`, `1`, e.t.c.

-   `cpu`: Use the CPU, do not do this for VSGAN! Even on amazing CPU's you are going to bottlekneck your entire system clock and straight up freeze your system to death. Even if you wait for it to finish, it will take literal hours for a single 480p frame. It's simply not feasible to do ESRGAN (regardless of VSGAN or not) via CPU.
-   `cuda`: This is a generic device that refers to any available cuda-capable GPU. For VSGAN to work with a GPU, it needs to support cuda, so make sure you install the NVIDIA CUDA Drivers, and yes this does mean AMD GPU's are unsupported, scream at pytorch for support, not me.
-   `0`, `1`, ...: Device ID by #. This generally refers to GPU #'s. e.g. in my system I have a 1080ti and a 2080ti, 0 refers to my 2080ti (which is my display output) and 1 refers to my 1080ti.

If you want to get you're GPU's `#` (e.g. `0`, `1`, ...) then you can do so by opening a terminal/cmd/powershell after installing all the dependencies of VSGAN, and running `python` to get into a python shell. Now run the following python code:

```py
import torch

print(f"Is CUDA working and available? {torch.cuda.is_available()}")
for n in range(torch.cuda.device_count()):
    print(f"Device: {n} is your: {torch.cuda.get_device_name(n)}")
```

This should return for example:

    Is CUDA working and available? True
    Device: 0 is your: GeForce RTX 2080 Ti
    Device: 1 is your: GeForce GTX 1080 Ti

#### chunk (bool)

Explanation can be found on the [VSGAN docs](https://github.com/rlaPHOENiX/VSGAN#vsganrunclipclip-chunkbool).

#### presample (int, false)

The new height it will resize to before running VSGAN. The aspect ratio is preserved. Set to false-y value, e.g. `false`, `None`, `0`, to disable.

#### resample (int, false)

The new height it will resize to after running VSGAN. The aspect ratio is preserved. Set to false-y value, e.g. `false`, `None`, `0`, to disable.
