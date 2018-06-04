#!/usr/bin/python3

import os
import re
import shlex
import subprocess
import sys
import tempfile

import matplotlib as mpl
import matplotlib.pyplot as plt
plt.switch_backend("pgf")
import matplotlib.type1font
import numpy as np
import PIL
import scipy.ndimage
import wordcloud

try:
  import helper
except ModuleNotFoundError:
  sys.path.append(os.path.join(os.path.dirname(__file__), "..", "py"))

import helper.basis
import helper.grid



def run(args, pipe=False, **kwargs):
  print("Running \"{}\"...".format(" ".join([shlex.quote(arg)
                                             for arg in args])))
  if pipe: kwargs["stdout"] = subprocess.PIPE
  process = subprocess.run(args, check=True, **kwargs)
  if pipe: return process.stdout.decode()



class MyWordCloud(wordcloud.WordCloud):
  textsToRemove = [
    "TODO write Hello here is some text without a meaning",
    "This text should show what a printed text will look like at this place",
    "sin α cos β",
    "If you read this text you will get no information",
    "Really Is there no information Is there a difference between this text "
      "and some nonsense like Huardest gefburn Kjift",
    "not at all A blind text like this gives you information",
    "about the selected font how",
    "the letters are written",
    "and an impression of the",
    "look",
    "This text should contain all letters of the",
    "alphabet and it should",
    "be written in of the original language",
    "There is no need",
    "for special contents",
    "but the length of words should match the language",
  ]
  
  wordsToReplace = {
    "Alg" : "Alg.",
    "Sec" : "Sec.",
    "Fig" : "Fig.",
    "Prop" : "Prop.",
    "Therefore" : "therefore",
    "Let" : "let",
    "Consequently" : "consequently",
    "hft" : None,
    "kmax" : None,
    "Hence" : "hence",
    "Kpole" : None,
    "Höl" : None,
    "Val" : None,
    "Pfl" : None,
    "PROP" : None,
    "OSITION" : None,
    "PRO" : None,
    "PROO" : None,
    "POSITION" : None,
    "According" : "according",
    "See Appendix" : "see Appendix",
    "Cor" : "Cor.",
    "wfs" : None,
    "nak" : None,
    "LGO" : None,
    "tion" : None,
    "Thus" : "thus",
    "Approximation" : "approximation",
    "FIGURE" : None,
    "Engineering" : "engineering",
    "Numerical" : "numerical",
    "Another" : "another",
    "supp" : None,
  }
  
  millimeterPerInch = 25.4
  
  def __init__(self, font_properties={}, dpi=72,
               regexp=r"[\w\-]+", stopwords=[],
               background_color="white", **kwargs):
    kwargs = dict(kwargs)
    self.font_properties = font_properties
    self.dpi = dpi
    self.pixelPerMillimeter = dpi / self.millimeterPerInch
    
    if kwargs.get("mask", None) is not None:
      height, width = kwargs["mask"].shape
      self.widthInMillimeters  = width / self.pixelPerMillimeter
      self.heightInMillimeters = height / self.pixelPerMillimeter
    else:
      self.widthInMillimeters  = kwargs["width"]
      self.heightInMillimeters = kwargs["height"]
      width  = int(self.pixelPerMillimeter * self.widthInMillimeters)
      height = int(self.pixelPerMillimeter * self.heightInMillimeters)
    
    kwargs["width"]            = width
    kwargs["height"]           = height
    kwargs["regexp"]           = regexp
    kwargs["stopwords"]        = stopwords
    kwargs["background_color"] = background_color
    
    if kwargs.get("max_font_size", None) is not None:
      kwargs["max_font_size"] = (
          int(self.pixelPerMillimeter * kwargs["max_font_size"]))
    
    if kwargs.get("min_font_size", None) is not None:
      kwargs["min_font_size"] = (
          int(self.pixelPerMillimeter * kwargs["min_font_size"]))
    
    super().__init__(**kwargs)
  
  def load_text_from_pdf(self, pdfPath, pdfFirstPage, pdfCropArea):
    text = run(["pdftotext", "-layout", "-nopgbrk", "-f", str(pdfFirstPage),
                "-x", str(pdfCropArea[0]), "-y", str(pdfCropArea[1]),
                "-W", str(pdfCropArea[2]), "-H", str(pdfCropArea[3]),
                pdfPath, "-"],
               pipe=True)
    return text
  
  def process_text(self, text):
    text = text.replace("\u2013", "-")
    text = text.replace("\n", " ")
    words = re.findall(r"(?:(?=[^0-9])[\w\-])+", text)
    text = " ".join(words)
    
    for textToRemove in self.textsToRemove:
      text = text.replace(textToRemove, "")
    
    oldWordCounts = super().process_text(text)
    wordCounts = {}
    
    for nGram, count in oldWordCounts.items():
      skipNGram = False
      words = []
      
      for word in nGram.split(" "):
        if word.lower() in wordcloud.STOPWORDS:
          pass
        elif (len(word) < 3) or (word[0] == "-"):
          skipNGram = True
        else:
          word = self.wordsToReplace.get(word, word)
          if word is None: skipNGram = True
          words.append(word)
      
      if (not skipNGram) and (len(words) > 0):
        nGram = " ".join(words)
        wordCounts[nGram] = count + wordCounts.get(nGram, 0)
    
    if self.normalize_plurals:
      for nGram, count in list(wordCounts.items()):
        nGramPlural = "{}s".format(nGram)
        
        if (not nGram.endswith("s")) and (nGramPlural in wordCounts):
          wordCounts[nGram] = count + wordCounts[nGramPlural]
          del wordCounts[nGramPlural]
    
    #import pprint
    #pprint.pprint(sorted(wordCounts.items(), key=lambda x: x[1]))
    print(len(wordCounts))
    
    return wordCounts
  
  def plot(self, ax):
    if self.mask is not None:
      width = self.mask.shape[1]
      height = self.mask.shape[0]
    else:
      width, height = self.width, self.height
    
    for (word, count), fontSize, position, orientation, color in \
        self.layout_:
      x = int(position[1] * self.scale)
      y = int((height - position[0]) * self.scale)
      fontSize *= 72 / self.dpi
      
      if (orientation is not None) and (orientation == 2):
        rotation, ha, va = 90, "right", "top"
      else:
        rotation, ha, va = 0, "left", "top"
        if word.startswith("f"): x += (0.18 * fontSize) * (72 / self.dpi)
      
      color = np.array(PIL.ImageColor.getrgb(color)) / 255
      ax.text(x, y, word, size=fontSize, color=color,
              rotation=rotation,rotation_mode="anchor", ha=ha, va=va,
              **self.font_properties)
  
  def to_file(self, filename):
    if os.path.splitext(filename)[1].lower() == ".pdf":
      fig, ax = self.create_figure()
      self.plot(ax)
      plt.savefig(filename, facecolor="none", transparent=True)
      return self
    else:
      return super().to_file(filename)
  
  def create_figure(self):
    fig = plt.figure(figsize=(
        self.widthInMillimeters  / self.millimeterPerInch,
        self.heightInMillimeters / self.millimeterPerInch))
    ax = fig.gca()
    ax.set_xlim(0, self.width * self.scale)
    ax.set_ylim(0, self.height * self.scale)
    ax.set_axis_off()
    ax.set_position([0, 0, 1, 1])
    return fig, ax
  
  def load_mask_figure(self, fig):
    plt.figure(fig.number)
    
    with tempfile.NamedTemporaryFile(suffix=".png") as f:
      plt.savefig(f.name, facecolor="none", transparent=True, dpi=self.dpi)
      self.mask = scipy.ndimage.imread(f.name, flatten=True)
    
    self.mask = self.mask.astype("B")
    self.mask = 255 - self.mask
    return self



#fontPath = "/usr/share/fonts/X11/Type1/c0633bt_.pfb"
#fontProperties = {
#  "family" : "Charter",
#  "weight" : "bold",
#  "style" : "italic",
#}
fontPath = "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf"
fontProperties = {"family": "Impact"}
size = [230, 155]
#pdfPath = os.path.join(os.path.dirname(__file__), "..", "out",
#                       "thesisManuscriptScreen.pdf")
pdfPath = os.path.join("/", "tmp", "thesis", "thesisManuscriptScreen.pdf")
pdfCropArea = [70, 85, 455, 700]
pdfFirstPage = 27



def plotMask(ax):
  width, height = ax.get_xlim()[1], ax.get_ylim()[1]
  
  bSplineMarginTop = 0.0 * height
  bSplineWidth = 1.15 * width
  bSplineHeight = 1.0 * height
  bSplineDegree = 3
  
  gridSize = 0.3 * width
  gridMarginBottom = 0.1 * height
  gridPointRadius = 0.01 * width
  gridLevel = 4
  gridBoundaryParameter = 2
  
  bSplineMarginLeft = (width - bSplineWidth) / 2
  bSplineMarginBottom = height - bSplineMarginTop - bSplineHeight
  
  ax.add_artist(mpl.patches.Rectangle((0, 0), width, height, color="k"))
  
  bSpline = helper.basis.CardinalBSpline(bSplineDegree)
  xx = np.linspace(0, bSplineDegree+1, 101)
  yy = bSpline.evaluate(xx)
  
  s = (lambda x, y: (
      bSplineMarginLeft   + bSplineWidth * x / (bSplineDegree+1),
      bSplineMarginBottom + bSplineHeight * y / np.max(yy)))
  xy = np.column_stack(s(xx, yy))
  ax.add_artist(mpl.patches.Polygon(xy, color="w"))
  
  gridMarginLeft = (width - gridSize) / 2
  grid = helper.grid.RegularSparseBoundary(
      gridLevel, 2, gridBoundaryParameter)
  X = grid.generate()[0]
  
  s = (lambda x, y: (gridMarginLeft   + gridSize * x,
                     gridMarginBottom + gridSize * y))
  
  for x, y in X:
    ax.add_artist(mpl.patches.Circle(s(x, y), gridPointRadius, color="k"))
  
  return
  
  for x, y in X:
    ax.add_artist(mpl.patches.Circle(s(x, y), gridPointRadius, color="w"))
  
  ax.add_artist(mpl.patches.Rectangle(s(0, 0), gridSize, gridSize, color="w"))
  
  for x, y in X:
    if x == 0:
      if y == 0: theta = (0, 90)
      elif y == 1: theta = (-90, 0)
      else: theta = (-90, 90)
    elif x == 1:
      if y == 0: theta = (90, 180)
      elif y == 1: theta = (180, 270)
      else: theta = (90, 270)
    else:
      if y == 0: theta = (0, 180)
      elif y == 1: theta = (180, 360)
      else: theta = (0, 360)
    ax.add_artist(mpl.patches.Wedge(s(x, y), gridPointRadius, *theta, color="k"))



def main():
  wordCloudProperties = {
    "font_path" : fontPath,
    "font_properties" : fontProperties,
    "width" : size[0],
    "height" : size[1],
    "scale" : 2,
    #"prefer_horizontal" : 0.5,
    #"prefer_horizontal" : 1.0,
    "prefer_horizontal" : 0.9,
    "max_words" : 1000000,
    "max_font_size" : 10,
    "min_font_size" : 0.5,
    "random_state" : 342,
    #"relative_scaling" : 0.5,
    "relative_scaling" : 0,
    "collocations" : False,
    "margin" : 0,
    "color_func" : (lambda word, font_size, position, orientation,
                    font_path, random_state: "black"),
    #"dpi" : 300,
    "dpi" : 150,
  }
  
  wordCloud = MyWordCloud(**wordCloudProperties)
  
  fig, ax = wordCloud.create_figure()
  plotMask(ax)
  wordCloud.load_mask_figure(fig)
  print(wordCloud.mask.shape)
  
  text = wordCloud.load_text_from_pdf(pdfPath, pdfFirstPage, pdfCropArea)
  text = text.upper()
  wordCloud.generate_from_text(text)
  print(len(wordCloud.layout_))
  wordCloud.to_file("blubb.png")
  wordCloud.to_file("blubb.pdf")
  
  #import PIL
  #img = wordCloud.to_image()
  #draw = PIL.ImageDraw.Draw(img)
  #for (word, count), font_size, position, orientation, color in wordCloud.layout_:
  #  x = int(position[1] * wordCloud.scale)
  #  y = int(position[0] * wordCloud.scale)
  #  draw.line((x, 0, x, wordCloud.height * wordCloud.scale), fill=128)
  #  draw.line((0, y, wordCloud.width * wordCloud.scale, y), fill=128)
  #img.save("blubb.png", optimize=True)



if __name__ == "__main__":
  main()
