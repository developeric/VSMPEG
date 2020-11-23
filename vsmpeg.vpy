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
from pymediainfo import MediaInfo
import havsfunc


"""
1. INSTALLATION

Follow instructions here: https://github.com/rlaPHOENiX/VSMPEG/blob/master/README.md

2. USAGE

It's super simple, configure the IO_MAP variable found below.
The IO_MAP variable is asking what you want the output to be.
"""

DEBUG = False
IO_MAP = {
	"file": "file:///run/media/phoenix/emby-4-sea/discs/dvd/American Dad/American.Dad.V03.USA.NTSC.3xDVD9.MPEG-2.DD.5.1-PHOENiX/Disc 2/VIDEO_TS/VTS_07_1.VOB",
	"scan": {
		"type": "progressive",  # output will always be progressive
		"means": (
			havsfunc.QTGMC, {"FPSDivisor": 2},  # QTGMC with same-rate output
			#havsfunc.srestore, {"frate": 24000/1001},
		)
	},
	"resolution": {
		"width": 640,
		"height": 480,
		"means": {
			"kernel": core.resize.Spline64,
			"dar": ("auto", 0),  # 0=change width, 1=change height, "auto"=auto if possible
			#"depillarbox": ("4:3", 0),  # remove black bars from left and right, int is +/- offset
			#"deletterbox": ("21:9", 0),  # remove black bars from top and bottom, int is +/- offset
			#"crop": [3, 0, 0, 0],  # left, right, top, bottom
		}
	},
	"fps": {
		"type": "cfr",  # output will always be CFR, VFR is unsupported
		"numerator": 24000,
		"denominator": 1001,
		"means": {
			"split_per_vob_cell": True,  # reset cycle every time it enters a new vob cell (if using .VOB)
			"SelectEvery": (5, [0, 1, 3, 4]),  # cycle (int), offsets (list<int>)
			#"VDecimate": (5),  # args of VDecimate. (not recommended: git.io/avoid-tdecimate)
		}
	},
	"color": {
		"chroma_location": None,  # None=auto, 0=left, 1=center, 2=topleft, 3=top, 4=bottomleft, 5=bottom
	},
	"VSGAN": {
		# """
		# Super-resolution Generative Adversarial Network (port of ESRGAN).
		# Allows you to use trained models on each frame of the video.
		# VSGAN is applied after Deinterlacing, Decimation and Deboxing but before aspect_ratio fixer below.
		
		# More info: 
		# https://github.com/rlaPHOENiX/VSGAN
		# """
		"enabled": False,
		"compare": 1,  # Compare between input and output of VSGAN, 0=Off, 1==Interleave, 2==StackHorizontal, 3==mvsfunc.Preview
		"output_yuv": False,  # Convert Result frame to YUV, recommended if encoding to video with FFMPEG, otherwise disable
		"executions": [
			{
				"enabled": True,
				"model": r"/home/phoenix/github/BasicSR-vic/experiments/adntsc2hd/models/300000_G.pth",
				"device": 1,
				"chunk": False,
				"presample": False,
				"resample": 1080
			},
			{
				"enabled": False,
				"model": r"/home/phoenix/Downloads/2x_real_pokemodel_v2_final_G.pth",
				"device": 1,
				"chunk": False,
				"presample": False,
				"resample": 1080
			},
			{
				"enabled": False,
				"model": r"/home/phoenix/github/BasicSR-vic/experiments/pkmnbd2hd/models/140000_G.pth",
				"device": 1,
				"chunk": False,
				"presample": 1080,
				"resample": 1080
			},
		]
	}
}

# /!\ Do not edit beyond here unless you know what your doing /!\

# == Argument Stage ==
args = ["i", "res", "fps", "chroma_loc", "debug"]
for arg in args:
	if arg in locals():
		DEBUG = False
		arg_v = locals()[arg].decode("utf-8")
		if arg == "i":
			IO_MAP["file"] = arg_v
		elif arg == "res":
			arg_v = [int(x) for x in arg_v.split("x")]
			IO_MAP["resolution"]["width"] = arg_v[0]
			IO_MAP["resolution"]["height"] = arg_v[1]
		elif arg == "fps":
			arg_v = [int(x) for x in arg_v.split("/")]
			IO_MAP["fps"]["numerator"] = arg_v[0]
			IO_MAP["fps"]["denominator"] = arg_v[1] if len(arg_v) == 2 else 1
		elif arg == "chroma_loc":
			IO_MAP["color"]["chroma_location"] = int(arg_v)
		elif arg == "debug":
			DEBUG = bool(arg_v)

# == File Stage ==
# remove file: prefix from path, cross-os
IO_MAP["file"] = anti_file_prefix(IO_MAP["file"])
# if the fps has been modified in the container, revert it back to the original
# todo ; only do this for AVC
mi = MediaInfo.parse(IO_MAP["file"])
mi_video = [x for x in mi.tracks if x.track_type == "Video"]
if len(mi_video) > 0:
	mi_video = mi_video[0]
	if mi_video.original_frame_rate:
		# has a modified frame rate, lets restore back to original
		fps_fix_path = f"{IO_MAP['file']}.fpsfix.mkv"
		original_fps = None
		if mi_video.framerate_original_num and mi_video.framerate_original_den:
			original_fps = f"{mi_video.framerate_original_num}/{mi_video.framerate_original_den}"
		else:
			original_fps = f"{mi_video.original_frame_rate}"
		if not os.path.exists(fps_fix_path):
			subprocess.check_output([
				"mkvmerge","--output", fps_fix_path,
				 "--default-duration", f"{mi_video.track_id-1}:{original_fps}fps",
				IO_MAP["file"]
			], cwd=os.path.dirname(IO_MAP["file"]))
		IO_MAP["file"] = fps_fix_path
# load file path with PSourcer
psourcer = PSourcer(IO_MAP["file"], debug=DEBUG)
sourcer = psourcer.sourcer
clip = psourcer.clip

# == Scan Stage ==
# Deinterlace
clip = PDeinterlacer(clip, *IO_MAP["scan"]["means"], debug=DEBUG).clip

# == FPS Stage ==
# Decimate
if [clip.fps.numerator, clip.fps.denominator] != [IO_MAP["fps"]["numerator"], IO_MAP["fps"]["denominator"]]:
	decimation_means = [k for k in IO_MAP["fps"]["means"].keys() if k != "split_per_vob_cell"][0]
	decimation_mode = {"SelectEvery": 0, "VDecimate": 1}[decimation_means]
	decimation_means = IO_MAP["fps"]["means"][decimation_means]
	clip = PDecimate(
		clip=clip,
		per_vob_id=IO_MAP["fps"]["means"]["split_per_vob_cell"],
		mode=decimation_mode,
		cycle=decimation_means[0],
		offsets=decimation_means[1] if len(decimation_means) >= 2 else None,
		debug=DEBUG
	).clip

# == Color stage ==
# Chroma location
if type(IO_MAP["color"]["chroma_location"]) is int:
	if IO_MAP["color"]["chroma_location"] < 0 or IO_MAP["color"]["chroma_location"] > 5:
		raise ValueError("IO_MAP->color->chroma_location value is invalid. Must be an integer between 0..5")
	clip = core.resize.Point(
		clip,
		chromaloc=IO_MAP["color"]["chroma_location"],
		chromaloc_in=clip.get_frame(0).props["_ChromaLocation"]
	)

# == Resolution stage ==
def res_differ():
	return [clip.width, clip.height] != [IO_MAP["resolution"]["width"], IO_MAP["resolution"]["height"]]
# Debox
if res_differ:
	for k, v in {k: v for k, v in IO_MAP["resolution"]["means"].items() if k.endswith("box")}.items():
		clip = PDebox(
			clip,
			aspect_ratio=v[0],
			mode={"depillarbox": 0, "deletterbox": 1}[k],
			offset=v[1]
		).clip
# Cropping
if "crop" in IO_MAP["resolution"]["means"] and res_differ():
	clip = core.std.Crop(clip, *IO_MAP["resolution"]["means"]["crop"])
# DAR
if "dar" in IO_MAP["resolution"]["means"] and res_differ():
	dar = IO_MAP["resolution"]["means"]["dar"]
	if dar[0] == "auto":
		if sourcer == "core.d2v.Source":
			d2v = D2V(clip.get_frame(0).props["PVSFilePath"])
			dar = (d2v.settings["Aspect_Ratio"], dar[1])
		else:
			dar = (None,)
	if dar[0]:
		aspect_ratio = [int(x) for x in dar[0].split(":")]
		calculated_width = math.ceil(clip.height * (aspect_ratio[0] / aspect_ratio[1]))
		calculated_height = math.ceil(clip.width / (aspect_ratio[0] / aspect_ratio[1]))
		clip = IO_MAP["resolution"]["means"]["kernel"](
			clip=clip,
			**{{0: "width", 1: "height"}[dar[1]]: {0: calculated_width, 1: calculated_height}[dar[1]]}
		)
if res_differ():
	clip = core.text.Text(
		clip,
		"Warning: The wanted resolution could not be obtained. " +
		"Make sure you enabled one of it's means options. " +
		"It's possible the wanted resolution simply couldn't be obtained with the means used as well."
	)

# == VSGAN Stage ==
if IO_MAP["VSGAN"]["enabled"]:
	import mvsfunc
	from vsgan import VSGAN
	if IO_MAP["VSGAN"]["compare"]:
		og = clip
	for execution in IO_MAP["VSGAN"]["executions"]:
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
	if IO_MAP["VSGAN"]["output_yuv"]:
		clip = mvsfunc.ToYUV(clip, css="4:2:0", depth=8)
	if IO_MAP["VSGAN"]["compare"]:
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
		clip = core.std.Interleave(clip) if IO_MAP["VSGAN"]["compare"] == 1 else core.std.StackHorizontal(clip) if IO_MAP["VSGAN"]["compare"] == 2 else mvsfunc.Preview(clip)

clip.set_output()
