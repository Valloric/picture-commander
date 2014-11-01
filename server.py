#!/usr/bin/env python

import sys
import signal
import chan
import os
import httplib
from flask import ( Flask, render_template, send_from_directory, Response,
                    make_response, request )
import argparse

IMAGE_EXTENSIONS = { 'jpg', 'jpeg', 'png', 'webp', 'tiff', 'gif' }
cmd_args = None
image_channel = chan.Chan( buflen = 5 )
app = Flask( __name__ )


@app.route( '/' )
def Root():
  return render_template( 'index.html' )


@app.route( '/gallery' )
def Gallery():
  response = make_response(
    render_template( 'gallery.html',
                     images = AdjustedImagePaths( AllImages() ) ) )
  response.headers['Cache-Control'] = 'no-cache'
  return response


@app.route( '/viewer' )
def Viewer():
  return make_response( render_template( 'viewer.html' ) )


@app.route( '/image_selected', methods=['POST'] )
def ImageSelected():
  filename = request.form[ 'filename' ]
  image_channel.put( filename )
  print 'User selected', filename
  return ( '', httplib.OK )


@app.route( '/images/<path:filename>' )
def Images( filename ):
  return send_from_directory( cmd_args.images_folder, filename )


@app.route( '/stream' )
def Stream():
  return Response( EventStream(), mimetype = 'text/event-stream' )


@app.route( '/shutdown' )
def Shutdown():
  os._exit( 0 )


def EventStream():
  for image in image_channel:
    yield 'data: {0}\n\n'.format( image )


def AllImages():
  for root, _, filenames in os.walk( cmd_args.images_folder ):
    for filename in filenames:
      extension = os.path.splitext( filename )[ 1 ][ 1: ]
      if extension in IMAGE_EXTENSIONS:
        yield os.path.abspath( os.path.join( root, filename ) )


def AdjustedImagePaths( images ):
  absolute_image_root = os.path.abspath( cmd_args.images_folder )
  for image_path in images:
    yield image_path.replace( absolute_image_root, '/images' )


def SetUpSignalHandlers():
  def SignalHandler( signum, frame ):
    sys.exit()

  for sig in [ signal.SIGTERM,
               signal.SIGINT ]:
    signal.signal( sig, SignalHandler )


def ParseArguments():
  parser = argparse.ArgumentParser()
  parser.add_argument( '--images_folder', type = str, default = None,
                       required = True,
                       help = 'The folder with images to serve.')
  return parser.parse_args()


def Main():
  global cmd_args
  SetUpSignalHandlers()
  cmd_args = ParseArguments()
  app.run( threaded = True, port = 8080, use_reloader = False, debug = False )


if __name__ == '__main__':
  Main()
