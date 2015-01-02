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

to start a local server listing images in/below the current directory. Your default browser will start a new tab at http://127.0.0.1:8000/
Requires PIL.


Chrome, xdg-open, custom MIME type
----------------------------------

This section setups a custom URI scheme that starts imagemee
when e.g. `imagemee:/home/user/photos` link is clicked.
This was tested under Debian with XFCE, but should work
under other standard desktop environments as well (GNOME, KDE, LXDE).

1. Create a `imagemee.desktop` file in `~/.local/share/applications/`. Here's mine
   ```
   [Desktop Entry]
   Version=1.0
   Name=Imagemee
   GenericName=Image Gallery Server
   TryExec=python3
   Exec=python3 /path/to/imagemee/imagemee.py %U
   Terminal=true
   Type=Application
   Categories=Network;
   MimeType=x-scheme-handler/imagemee;
   ```

2. Update the applications database
   ```
   $ update-desktop-database ~/.local/share/applications
   ```

3. Set the default application for opening URIs of this mimetype.
   ```
   $ xdg-mime default imagemee.desktop x-scheme-handler/imagemee
   ```

Chrome will now use `xdg-open` to open `imagemee:path` links (will ask first time).
One can now add a bookmark for easy access to imageMee.
