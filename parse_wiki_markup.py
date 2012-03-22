#
#  Parses wikipedia dumps to "text-wiki" format.
#  Output has one article per line, in format "title tab string-escaped article content"
#  String-escaped means that control characters such as new line are written as \n
#
#  usage: cat wiki.xml | python parse_wiki_markup.py > corpus.txt
#

# note: dividing program to functions is SO outdated :)
# note: many wiki markup constructs such as &quot; or &dash; are not parsed, but output is an average quite good
# note: recursive [[ x | [[ y | z ]] ]] is not parsed correctly!
# todo: fix these remaining problems!

import cStringIO
import re
import sys

#used to discard some metadata
re_all = re.compile("&[lg]t;|\{\{|\}\}")

inside = False
title = None
text = cStringIO.StringIO()
for line in sys.stdin:
  cont = False
  if line.find('<title>') != -1 and line.find('</title>') != -1:
    title = line[line.find('<title>') + 7 : line.find('</title>') ]
  if line.find('<text') != -1:
    inside = True
    cont = True
    if line.count('{{') > line.count('}}'):
      text.write("{{")
  if line.find('</text>') != -1:
    if title != None and len(text.getvalue()) > 20:
      # write article content
      # discard all text between {{ and }}
      # print text in [[ XXX | text ]]
      # discard '
      # discard between tags eg &lt;center&gt &lt;/center&gt
      # discard tags eg &lt;center&gt
      # note: recursive [[ x | [[ y | z ]] ]] is not parsed correctly!
      # note: other commands such as &quot; are not handled
      text = text.getvalue().replace("'","")
      sys.stdout.write(title+'\t')
      text1 = cStringIO.StringIO()
      lt_depth = 0 # strts &lt;
      block_depth = 0 #starts {{
      while 1:
        m = re_all.search(text)
        if m == None:
          if max(lt_depth,block_depth) == 0:
            text1.write(text)
          break
        loc = m.start(0)
        if max(lt_depth,block_depth) == 0 and not (text[loc+1]=="l" and text[loc+4] == "/"):
          text1.write(text[0:loc])
        if block_depth == 0 and text[loc+1] == "g":
          lt_depth = max(0,lt_depth-1)
        elif block_depth == 0 and text[loc+1] == "l":
          lt_depth += 1
        elif text[loc:loc+2] == "{{":
          block_depth += 1
        elif text[loc:loc+2] == "}}":
          block_depth = max(0,block_depth -1)
        text = text[m.end(0):]
      text = text1.getvalue()
      text1 = sys.stdout
      while 1:
        beg,sep,end = text.partition('[[')
        text1.write(beg.encode("string-escape"))
        if len(end) == 0:
          break
        else:
          beg,sep,text = end.partition(']]')
          if beg.find('|') != -1:
            s = beg.split('|')[-1]
            if s[0:2] == "[[":
              text1.write(s[2:].encode("string-escape"))
            else:
              text1.write(s.encode("string-escape"))
          elif len(beg) > 0:
            text1.write(beg.encode("string-escape"))
      sys.stdout.write('\n')
      title = None
      text = cStringIO.StringIO()
    inside = False
  if cont:
    continue
  if inside:
    text.write(line)
 

