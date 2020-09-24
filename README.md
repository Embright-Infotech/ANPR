# ANPR -Based on YOLOv4 Tiny
[![Darknet Continuous Integration](https://github.com/AlexeyAB/darknet/workflows/Darknet%20Continuous%20Integration/badge.svg)](https://github.com/AlexeyAB/darknet/actions?query=workflow%3A%22Darknet+Continuous+Integration%22)
[![CircleCI](https://circleci.com/gh/AlexeyAB/darknet.svg?style=svg)](https://circleci.com/gh/AlexeyAB/darknet)
[![TravisCI](https://travis-ci.org/AlexeyAB/darknet.svg?branch=master)](https://travis-ci.org/AlexeyAB/darknet)
[![Contributors](https://img.shields.io/github/contributors/AlexeyAB/Darknet.svg)](https://github.com/AlexeyAB/darknet/graphs/contributors)
[![License: Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg)](https://github.com/AlexeyAB/darknet/blob/master/LICENSE)

### Built on top of AlexyAB's Darknet repository <img src="http://pjreddie.com/media/files/darknet-black-small.png" style="float: left; margin-right: 10px;" width="30"/>
AlexyAB's Darknet repository: https://github.com/AlexeyAB/darknet

### Screenshots
<img src="/screens/sc1.png" style="float: left; margin-right: 10px;" width="500"/><img src="/screens/sc2.png" style="float: left; margin-right: 10px;" width="500"/>

### Installation

This code was written and tested on a Linux machine but the installation steps will be similar for Windows an MacOS

Clone the darknet repository

```bash
git clone https://github.com/AlexeyAB/darknet.git
```
Download these files and copy them to the cloned darknet repository

Open the Makefile and change these lines as folows

```python
GPU=1 # 0 to 1 if you have a GPU
CUDNN=1 # 0 to 1 if you want to use CUDNN
CUDNN_HALF=0 # 0 to 1 if you have a higher end GPU
OPENCV=1 # 0 to 1 to use opencv will not work if you dont set it to 1
AVX=1 # 0 to 1 useful if you need to run it in a CPU
OPENMP=0 # 0 to 1 (user preference)
LIBSO=1 # 0 to 1 Important the code wont run without it will generate a libdarknet.so
ZED_CAMERA=0 # 0 to 1 (user preference)
ZED_CAMERA_v2_8=0 # 0 to 1 (user preference)
```
Run make

```bash
make -j4
```
Darknet will be compiled with GPU support


