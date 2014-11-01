Picture Viewer
==============

This is quickly hacked together webapp that makes it possible to select images
in a gallery in one browser tab and have that image server-pushed (via
[Server-Sent Events][http://dev.w3.org/html5/eventsource/]) and displayed in a
different tab. Subsequent image clicks in the gallery replace the displayed
image in the viewer tab.

Super-useful when projecting one browser tab to different screen with say a
Chromecast since the gallery tab can then direct the projected one.

There's one "admin" view (`/gallery` handler) and one "display" view
(`/viewer` handler). Provide a path to the folder with images you want to serve.
Example:

```shell
./server.py --images_folder=./test_images
```

Then go to [http://localhost:8080/gallery][] for the admin view and to
[http://localhost:8080/viewer][] for the viewer page.

This code is provided on a "works for me" basis and an Apache v2 license.

For the love of god, don't expose this server to the Internet.
