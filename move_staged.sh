#!/bin/bash

for file in `find . -name \*.staged`; do mv $file ${file/.staged/}; done

