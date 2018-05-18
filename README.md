# SPDX Build tool

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
