#!/usr/bin/env python3

# vapoursynth
from vapoursynth import core
# std
import os
import math
import functools
import binascii
import subprocess
# pip packages
from pvsfunc.psourcer import PSourcer
from pvsfunc.pdeinterlacer import PDeinterlacer
from pvsfunc.pdebox import PDebox
from pvsfunc.pdecimate import PDecimate
from pvsfunc.helpers import anti_file_prefix
from pyd2v import D2V
import havsfunc


"""
Documentation and information:
https://rlaphoenix.github.io/VSMPEG
"""

DEBUG = True
Input = "file:///mnt/emby/tv/The IT Crowd/The.IT.Crowd.S01.PAL.DVD.DD.2.0.MPEG-2.REMUX-RPG/The.IT.Crowd.S01E03.Fifty-Fifty.PAL.DVD.DD.2.0.MPEG-2.REMUX-RPG.mkv"

# >>> Scan

Deinterlacer = [
    (lambda clip, tff: clip, {}),  # 0 == Disable deinterlacing
    (havsfunc.QTGMC, {
        "FPSDivisor": 2,
        "Preset": "Placebo",
        "MatchPreset": "Placebo",
        "MatchPreset2": "Placebo",
        "InputType": 0,
        "SourceMatch": 3,
        "Lossless": 2,
        "Sharpness": 0.2,
        "ShutterBlur": 0,
        "ShutterAngleSrc": 0,
        "ShutterAngleOut": 0,
        "SBlurLimit": 0
    }),
    (PDeinterlacer.VoidWeave, {
        "bob": True
    }),
][1]

# >>> Frame-rate

Decimation = (0, [0, 1, 3, 4])  # cycle of 0 = disabled
ResetCyclePerVobCell = True

# >>> Color

ChromaLocation = None

# >>> Resizing and Cropping

Debox = [
    # mode, wanted aspect ratio, offset +/- int
    #("w", [4, 3], 0),  # remove centered pillarboxing (sides) to 4:3 aspect ratio
    #("h", [21, 9], 0),  # remove centered letterboxing (top/bot) to 21:9 aspect ratio
]
# default: []
Crop = []  # left, right, top, bottom. Set to empty list ([]) to disable.
AspectRatio = [
    None,     # Do nothing, use the stored resolution's Stored Aspect Ratio (SAR).
    "DAR",    # Use the DAR (Display Aspect Ratio) from the input file's metadata.
    [16, 9],  # Force a specific aspect ratio
][1]
# Change Aspect Ratio by resizing the:
AspectRatioMode = "width"  # "width", "height"
# Kernel to use when resizing the Aspect Ratio
AspectRatioKernel = core.resize.Spline64  # core.resize.* is accepted, possibly more!

# >>> VSGAN

VSGAN = {
    "enabled": False,
    "compare": 0,  # Compare between input and output of VSGAN, 0=Off, 1==Interleave, 2==StackHorizontal, 3==mvsfunc.Preview
    "output_yuv": True,  # Convert Result frame to YUV, recommended if encoding to video with FFMPEG, otherwise disable
    "executions": [
        {
            "enabled": False,
            "model": r"/home/phoenix/Git/BasicSR-vic/experiments/adntsc2hd/models/300000_G.pth",
            "device": 1,
            "chunk": False,
            "presample": False,
            "resample": 1080
        },
        {
            "enabled": False,
            "model": r"/home/phoenix/Git/BasicSR-vic/experiments/pkmnbd2hd/models/140000_G.pth",
            "device": 1,
            "chunk": False,
            "presample": 1080,
            "resample": 1080
        },
        {
            "enabled": True,
            "model": r"/home/phoenix/Downloads/11000_G.pth",
            "device": 1,
            "chunk": False,
            "presample": False,
            "resample": False
        },
    ]
}

# /!\ Do not edit beyond here unless you know what your doing /!\

# load file path with PSourcer
psourcer = PSourcer(Input, debug=DEBUG)
sourcer = psourcer.sourcer
clip = psourcer.clip

# >>> Scan

# Deinterlace
clip = PDeinterlacer(clip, *Deinterlacer, debug=DEBUG).clip

# >>> Frame-rate

# Decimate
for cycle, offsets in [Decimation]:
    if cycle != 0:
        clip = PDecimate(
            clip=clip,
            per_vob_id=ResetCyclePerVobCell,
            mode={False: 0, True: 1}[len(offsets) == 0],
            cycle=cycle,
            offsets=offsets or None,
            debug=DEBUG
        ).clip

# >>> Color

# Chroma location
if type(ChromaLocation) is int:
    if ChromaLocation < 0 or ChromaLocation > 5:
        raise ValueError("ChromaLocation value is invalid. Must be an integer between 0..5")
    clip = core.resize.Point(
        clip,
        chromaloc=ChromaLocation,
        chromaloc_in=clip.get_frame(0).props["_ChromaLocation"]
    )

# >>> Resizing and Cropping

# Debox
for mode, aspect, offset in Debox:
    clip = PDebox(
        clip,
        aspect_ratio=":".join([str(x) for x in aspect]),
        mode={"w": 0, "h": 1}[mode],
        offset=offset
    ).clip

# Crop
if len(Crop):
    clip = core.std.Crop(clip, *Crop)

# Aspect Ratio
if AspectRatio:
    if AspectRatio == "DAR":
        if sourcer == "core.d2v.Source":
            d2v = D2V(clip.get_frame(0).props["PVSFilePath"])
            AspectRatio = [int(x) for x in d2v.settings["Aspect_Ratio"].split(":")]
        else:
            # todo ; needs support for other codecs, perhaps via pymediainfo?
            AspectRatio = None
    if AspectRatio:
        ar_w = math.ceil(clip.height * (AspectRatio[0] / AspectRatio[1]))
        ar_h = math.ceil(clip.width / (AspectRatio[0] / AspectRatio[1]))
        clip = AspectRatioKernel(
            clip=clip,
            **{AspectRatioMode: {"w": ar_w, "h": ar_h}[AspectRatioMode[0]]}
        )

# == VSGAN Stage ==
if VSGAN["enabled"]:
    import mvsfunc
    from vsgan import VSGAN
    if VSGAN["compare"]:
        og = clip
    for execution in VSGAN["executions"]:
        if not execution["enabled"]:
            continue
        vsgan_device = VSGAN(execution["device"])
        vsgan_device.load_model(anti_file_prefix(execution["model"]))
        if execution["presample"]:
            clip = core.resize.Spline36(
                clip,
                width=execution["presample"] * (clip.width / clip.height),
                height=execution["presample"]
            )
        clip = vsgan_device.run(clip, chunk=execution["chunk"])
        if execution["resample"]:
            clip = core.resize.Spline36(
                clip,
                width=execution["resample"] * (clip.width / clip.height),
                height=execution["resample"]
            )
    if VSGAN["output_yuv"]:
        clip = mvsfunc.ToYUV(clip, css="4:2:0", depth=8)
    if VSGAN["compare"]:
        # match the res and format between the before clip and current clip
        if og.height != clip.height or og.width != clip.width:
            og = core.resize.Spline36(og, width=clip.width, height=clip.height)
        if og.format != clip.format:
            # assuming RGB24 as VSGAN returns an RGB24 clip, maybe check if RGB or YUV
            og = mvsfunc.ToRGB(og, depth=clip.format.bits_per_sample)
        clip = [
            core.text.Text(og, "Original"),
            core.text.Text(clip, "Result")
        ]
        clip = core.std.Interleave(clip) if VSGAN["compare"] == 1 else core.std.StackHorizontal(clip) if VSGAN["compare"] == 2 else mvsfunc.Preview(clip)

clip.set_output()
