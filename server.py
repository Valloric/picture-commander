#!/usr/bin/env python

import signal
import os
import httplib
from flask import ( Flask, render_template, send_from_directory, Response,
                    make_response, request )
import argparse
import threading

IMAGE_EXTENSIONS = { 'jpg', 'jpeg', 'png', 'webp', 'tiff', 'gif' }
cmd_args = None
current_image = ''
image_condition_var = threading.Condition()
app = Flask( __name__ )


class Image(object):
  def __init__(self, path, name):
    self.path = path
    self.name = name


@app.route( '/' )
def Root():
  return render_template( 'index.html' )


@app.route( '/gallery' )
def Gallery():
  response = make_response(
    render_template( 'gallery.html',
                     images = AdjustedImagePaths( AllImages() ) ) )
  response.headers[ 'Cache-Control' ] = 'no-cache'
  return response


@app.route( '/viewer' )
def Viewer():
  return make_response( render_template( 'viewer.html' ) )


@app.route( '/image_selected', methods = ['POST'] )
def ImageSelected():
  global current_image
  filename = request.form[ 'filename' ]
  with image_condition_var:
    current_image = filename
    image_condition_var.notify_all()
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
  with image_condition_var:
    while True:
      image_condition_var.wait()
      yield 'data: {0}\n\n'.format( current_image )


def AllImages():
  for root, _, filenames in os.walk( cmd_args.images_folder ):
    for filename in filenames:
      basename, extension = os.path.splitext( filename )
      extension = extension[ 1: ]
      if extension in IMAGE_EXTENSIONS:
        yield Image( os.path.abspath( os.path.join( root, filename ) ),
                     basename )



def AdjustedImagePaths( images ):
  absolute_image_root = os.path.abspath( cmd_args.images_folder )
  for image in images:
    image.path = image.path.replace( absolute_image_root, '/images' )
    yield image


def SetUpSignalHandlers():
  def SignalHandler( signum, frame ):
    os._exit( 0 )

  for sig in { signal.SIGTERM, signal.SIGINT }:
    signal.signal( sig, SignalHandler )


def ParseArguments():
  parser = argparse.ArgumentParser()
  parser.add_argument( '--images_folder', type = str, default = None,
                       required = True,
                       help = 'The folder with images to serve.')
  parser.add_argument( '--port', type = int, default = 8080,
                       help = 'The port to serve on.')
  parser.add_argument( '--host', type = str, default = '127.0.0.1',
                       help = 'The host to serve on.')
  args = parser.parse_args()
  args.images_folder = os.path.abspath(
    os.path.expanduser( args.images_folder ) )
  return args


def Main():
  global cmd_args
  SetUpSignalHandlers()
  cmd_args = ParseArguments()
  app.run( threaded = True,
           port = cmd_args.port,
           host = cmd_args.host,
           use_reloader = False,
           debug = False )


if __name__ == '__main__':
  Main()
