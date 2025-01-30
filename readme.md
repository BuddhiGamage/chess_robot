sudo apt install tesseract-ocr
sudo apt install stockfish

neeed to install kinova api through whl. 

problem in python 3.10 
AttributeError: module 'collections' has no attribute'MutableMapping'
add following after line 45 in containers.py

import collections.abc
collections.MutableMapping = collections.abc.MutableMapping
collections.MutableSequence = collections.abc.MutableSequence