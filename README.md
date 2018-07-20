# SPDX Build tool

[![Build Status](https://travis-ci.org/ndip007/spdx-build-tool.svg?branch=develop)](https://travis-ci.org/ndip007/spdx-build-tool)

## Project synopsis / summary:
Support a continuous integration (CI) generation of SPDX files by creating a plugins or extensions to build tools. These plugins or extensions will generate valid SPDX documents based on the build file metadata and source files.
The Yocto build environment currently has some SPDX file generation capabilities, but there is a need for some additional work to integrate some of the existing tools into a more complete integrated toolset. The SPDX Maven Plugin is an example of an existing build tool SPDX generator.

## What is the project about? Why is it important?
This project is about the inclusion of high quality license information (for license compliance) to allow its use by downstream users of the code.
This is very important because many build environments do not always include license information in their metadata, and do not produce sufficient information for good license compliance.
THis project is generally about implementing a build tool spdx file generator plugin for build environments such as the following:
- MSBuild
- PIP
- NPM (Note: NPM does include SPDX compliance license information and tools)
- DEB


## How to test the project.

### 0. Requirements.
Install python3 venv
`sudo apt-get install python3-venv`
Install python 3
`sudo apt-get update`
`sudo apt-get install python3`
`sudo apt-get install python3=3.5.1*`

### 1. Pull the project.
Pull the project into a folder say "spdx"

### 2. Create a virtual environment for the project.
In the folder "spdx", run the command `python3 -m venv .`.
This will create a virtual environment for the project.

### 3. Activate the virtual environment.
In the "spdx" folder, run `source bin/activate`.
This will activate the virtual environment for the project.

### 4. Install the project requirements.
Now run the command `pip install -r build-tool/requirements.txt`.

### 5. Install the project.
cd into the directory "build-tool", ie `cd spdx-build-tool`.
Run `pip install -e .`

### 6. The entry points.
There are several entry points, but the one that does the analysis, parsing and download is `spdx-build`.
So, Run `spdx-build '~/Desktop/(some-project)/'`.
