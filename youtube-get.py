#! /usr/bin/env python

import re
import mechanize
import argparse
from subprocess import check_call

#+------------------------------------+
#| Script arguments                   |
#+------------------------------------+

parser = argparse.ArgumentParser(description='Youtube search wrapper for youtube-dl.')
parser.add_argument('search', metavar='QUERY',
    type=str,
    help="See results for Youtube search QUERY.")
parser.add_argument('-v','--video',
    action="store_true",
    help="Download video as mp4.")
parser.add_argument('-a','--audio',
    action="store_true",
    help="Extract video audio")
parser.add_argument('-mp3',
    action="store_true",
    help="Download audio as mp3, default False")
parser.add_argument('-f','--first',
    action="store_true",
    help="Download first result (no prompt), default False")
args = parser.parse_args()

#+------------------------------------+
#| Mechanize set-up                   |
#+------------------------------------+

youtube_url = "http://www.youtube.com"
url_regex   = '/watch\?v=.{11}'
br = mechanize.Browser()
br.set_handle_equiv(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.set_handle_refresh(False)
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
br.addheaders = [('User-agent', 'Firefox')]
response = br.open(youtube_url)
br.form  = list(br.forms())[1]

#+------------------------------------+
#| Internal Functions                 |
#+------------------------------------+

def populateResults(query):
  global results
  results = []
  control = br.form.find_control("search_query")
  if control.type == "text":  # means it's class ClientForm.TextControl
    control.value = query
  response = br.submit()
  for link in br.links():
    if (re.search(url_regex,link.url) and not re.search('Thumbnail',link.text)):
      results.append(link)

def downloadAudio(results,selection):
  global yt_dl
  global done
  if args.mp3:
    arg = ["--format","bestaudio","--extract-audio","--audio-format=mp3"]
  else:
    arg = ["-x"]
  for n in selection:
    check_call( yt_dl + arg + [youtube_url + results[int(n)].url] )
  done = True

def downloadVideo(results,selection):
  global yt_dl
  global done
  for n in selection:
    check_call( yt_dl + [youtube_url + results[int(n)].url] )
  done = True

def nextPage():
  global start
  global end
  start = end
  end   = end + 10

#+------------------------------------+
#| Global Vars                        |
#+------------------------------------+

start = 0
end   = 10
yt_dl   = ["youtube-dl"]
results = []

#+------------------------------------+
#| Download top choice, -f, or not    |
#+------------------------------------+

populateResults(args.search)

if (args.first):
  if (args.video):
    check_call( yt_dl + [args.search] )
  else:
    if args.mp3:
      arg = ["--format","bestaudio","--extract-audio","--audio-format=mp3"]
    else:
      arg = ["-x"]
    check_call( yt_dl + arg + [args.search] )
  done = True
else:
  print "\nSelect result to download:\n\tm for more\n\taudio <index>\n\tvideo <index>\n"
  done = False

options = {'video'  : downloadVideo,
           'audio'  : downloadAudio}

#+------------------------------------+
#| Menu Loop                          |
#+------------------------------------+

while not done:
  top = results[start:end]
  if len(top) == 0:
    print "No more"
  else:
    for result in top:
      print "%d : %s" % (results.index(result),result.text)
  selection = raw_input("?> ").split(' ')
  try:
    index = int(selection[0])
    if (args.video):
      downloadVideo( results, selection )
    else:
      downloadAudio( results, selection )
  except ValueError:
    if selection[0] == 'm':
      nextPage()
    else:
      options[selection[0]]( results, selection[1:] )

