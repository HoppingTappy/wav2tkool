#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path
import argparse
import wavFile
import m4aFile
import subprocess
import platform

def main():

	parser =	argparse.ArgumentParser(
				prog=__file__,
				usage="%(prog)s [options]",
				add_help=True,
				)

	parser.add_argument(	'inFile', #help='input file name',
							)

#	parser.add_argument(	'-f', '--freq', #help='output file name',
#							type=int, default=48000)

	args = parser.parse_args()

	inPath = Path(args.inFile)

	if platform.system() == "Windows":
		isWindows = True
	else:
		isWindows = False

	if isWindows:
		ext = ".exe"
	else:
		ext = ""

#	soxPath = Path(Path(__file__).resolve().parent.parent / "sox/sox.exe").resolve()

	ffmpegFileName = "ffmpeg" + ext
	ffmpegPath = Path(Path(__file__).resolve().parent / ffmpegFileName).resolve()

	if not ffmpegPath.exists():
		print(ffmpegFileName +" が見つかりません")
		return

#	targetFreq = args.freq

#	targetPath = inPath.with_stem(inPath.stem + "_"+str(targetFreq))

	srcWav = wavFile.WavFile()
	srcWav.read(inPath)


	if srcWav.checkChunk("smpl"):
		loopEnable = True
		loopStartPoint = srcWav.Chunk["smpl"].Start[0]
		loopEndPoint = srcWav.Chunk["smpl"].End[0]
		loopLength = loopEndPoint - loopStartPoint

#		srcSampleRate = srcWav.Chunk["fmt "].SampleRate
#		loopStartPoint = int(loopStartPoint * targetFreq / srcSampleRate)
#		loopEndPoint = int(loopEndPoint * targetFreq / srcSampleRate)
	else:
		loopEnable = False

#	cp = subprocess.run([soxPath, str(inPath), "-r 48000", str(targetPath)])

#	targetWav = wavFile.WavFile()
#	targetWav.read(targetPath)
#
#	if loopEnable:
#		targetWav.add("smpl")
#		targetWav.setSmpl(loopStartPoint,loopEndPoint)
#
#		byteLength = targetWav.Chunk["fmt "].BlockAlign
#		targetWav.Chunk["data"].Data = targetWav.Chunk["data"].Data[:(loopEndPoint+1)*byteLength]

#	targetWav.write(inPath)
#	targetPath.unlink()




	if loopEnable:
		cp = subprocess.run([ffmpegPath, "-y","-i",str(inPath),"-vn",'-metadata','LOOPSTART=' + str(loopStartPoint),'-metadata','LOOPEND=' + str(loopEndPoint),'-metadata','LOOPLENGTH=' + str(loopLength),"-acodec","libvorbis", "-f", "ogg",inPath.with_suffix(".ogg")])
		cp = subprocess.run([ffmpegPath, "-y","-i",str(inPath),"-vn",'-metadata','LOOPSTART=' + str(loopStartPoint),'-metadata','LOOPEND=' + str(loopEndPoint),'-metadata','LOOPLENGTH=' + str(loopLength),"-acodec","aac"      , "-f", "mp4",inPath.with_suffix(".m4a")])

		m4a = m4aFile.M4aFile()
		m4a.read(inPath.with_suffix(".m4a"))
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"].add("----")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1].add("name")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1]["name"].setData("LOOPSTART")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1].add("data")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1]["data"].setData(str(loopStartPoint))


		m4a.Chunks["moov"]["udta"]["meta"]["ilst"].add("----")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1].add("name")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1]["name"].setData("LOOPLENGTH")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1].add("data")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1]["data"].setData(str(loopLength))

		m4a.Chunks["moov"]["udta"]["meta"]["ilst"].add("----")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1].add("name")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1]["name"].setData("LOOPEND")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1].add("data")
		m4a.Chunks["moov"]["udta"]["meta"]["ilst"][-1]["data"].setData(str(loopEndPoint))

		m4a.write(inPath.with_suffix(".m4a"))

	else:
		cp = subprocess.run([ffmpegPath, "-y","-i",str(inPath),"-vn","-acodec","libvorbis", "-f", "ogg",inPath.with_suffix(".ogg")])
		cp = subprocess.run([ffmpegPath, "-y","-i",str(inPath),"-vn","-acodec","aac"      , "-f", "mp4",inPath.with_suffix(".m4a")])



if __name__ == "__main__":
	main()
