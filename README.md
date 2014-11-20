imageMee
========

imageMee is a tiny image gallery server. Started as a fork of 
[imageMe](https://github.com/unwitting/imageme), but then heavily modified.
It doesn't write anything to the filesystem (as imageMe does).

Usage
-----

Just run
```
python3 imagemee.py
```

to start a local server listing images in/below the current directory. Point your favorite browser at http://127.0.0.1:8000/
Requires PIL.
