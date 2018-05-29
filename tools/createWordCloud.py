#!/usr/bin/python3

import os
import shlex
import subprocess

import matplotlib as mpl
import matplotlib.pyplot as plt
plt.switch_backend("pgf")
import matplotlib.type1font
import wordcloud



def run(args, pipe=False, **kwargs):
  print("Running \"{}\"...".format(" ".join([shlex.quote(arg)
                                             for arg in args])))
  if pipe: kwargs["stdout"] = subprocess.PIPE
  process = subprocess.run(args, check=True, **kwargs)
  if pipe: return process.stdout.decode()

class MyWordCloud(wordcloud.WordCloud):
  def plot(self, ax, fontProperties):
    """self._check_generated()
    if self.mask is not None:
        width = self.mask.shape[1]
        height = self.mask.shape[0]
    else:
        height, width = self.height, self.width

    img = Image.new(self.mode, (int(width * self.scale),
                                int(height * self.scale)),
                    self.background_color)
    draw = ImageDraw.Draw(img)
    for (word, count), font_size, position, orientation, color in self.layout_:
        font = ImageFont.truetype(self.font_path,
                                  int(font_size * self.scale))
        transposed_font = ImageFont.TransposedFont(
            font, orientation=orientation)
        pos = (int(position[1] * self.scale),
                int(position[0] * self.scale))
        draw.text(pos, word, fill=color, font=transposed_font)
    return img"""
    if self.mask is not None:
      width = self.mask.shape[1]
      height = self.mask.shape[0]
    else:
      width, height = self.width, self.height
    
    for (word, count), fontSize, position, orientation, color in \
        self.layout_:
      #fontProperties = mpl.font_manager.FontProperties(fname=os.path.abspath(self.font_path))
      #print(fontProperties)
      x = int(position[1] * self.scale)
      y = int((height - position[0]) * self.scale)
      if (orientation is not None) and (orientation == 2):
        rotation = 90
        #x -= 0.05 * fontSize * self.scale
        #y -= 0.05 * fontSize * self.scale
        #word = r"\vphantom{Bg}" + word
      else:
        rotation = 0
      assert color.startswith("rgb(")
      assert color.endswith(")")
      color = [float(x.strip()) / 255 for x in color[4:-1].split(",")]
      ax.text(x, y, word, size=fontSize,
              rotation=rotation, color=color,
              ha="left", va="top", **fontProperties)
    
    ax.set_xlim(0, width * self.scale)
    ax.set_ylim(0, height * self.scale)



fontPath = "/usr/share/fonts/X11/Type1/c0633bt_.pfb"
fontProperties = {
  "family" : "Charter",
  "weight" : "bold",
  "style" : "italic",
}
size = [160, 250]
pdfPath = os.path.join(os.path.dirname(__file__), "..", "out",
                       "thesisManuscriptScreen.pdf")
pdfCropArea = [70, 85, 455, 700]
pdfFirstPage = 27



if __name__ == "__main__":
  text = run(["pdftotext", "-layout", "-nopgbrk", "-f", str(pdfFirstPage),
              "-x", str(pdfCropArea[0]), "-y", str(pdfCropArea[1]),
              "-W", str(pdfCropArea[2]), "-H", str(pdfCropArea[3]),
              pdfPath, "-"],
             pipe=True)
  
  linesToIgnore = """
TODO: write Hello, here is some text without a meaning. This text should show what a
printed text will look like at this place. sin2 (α) + cos2 (β) = 1. If you read this text, you
will get no information E = mc 2 . Really? Is there no information? Is there a difference
between this text and some nonsense like “Huardest gefburn”? Kjift – not at all! A blind
text like this gives you information about the selected font, how the letters are written
                                 p p  n     p
                                            n
and an impression of the look. n a · b = ab. This text should contain all letters of the
                                                               pn
alphabet and it should be written in of the original language. pn ab = n ab . There is no need
                                                                      Æ
                                                                                p
                                                                                n      pn
for special contents, but the length of words should match the language. a b = a n b.""".splitlines()
  #text = "\n".join([x for x in text.splitlines() if x not in linesToIgnore])
  
  text = text.replace("\n", " ")
  for line in linesToIgnore: text = text.replace(line, "")
  
  text = text.lower()
  text = text.replace("b-spline", "B-spline")
  
  wordsToIgnore = [
    "nak",
    "mod",
    "vvv",
    "wfs",
    "fig",
  ]
  
  for word in wordsToIgnore: text = text.replace(" {} ".format(word), "")
  
  print(text)
  pixelPerMillimeter = 72 / 25.4
  
  wordCloudProperties = {
    "font_path" : fontPath,
    "width" : int(pixelPerMillimeter * size[0]),
    "height" : int(pixelPerMillimeter * size[1]),
    "prefer_horizontal" : 0.5,
    "regexp" : r"\w[\w'\-]{2,}",
    "max_words" : 1000,
    "max_font_size" : int(pixelPerMillimeter * 20),
    "min_font_size" : int(pixelPerMillimeter * 1),
    "random_state" : 342,
    "relative_scaling" : 0.5,
  }
  
  wordCloud = MyWordCloud(**wordCloudProperties)
  wordCloud.generate_from_text(text)
  wordCloud.to_file("blubb.png")
  
  fig = plt.figure(figsize=(size[0] / 25.4, size[1] / 25.4))
  ax = fig.gca()
  wordCloud.plot(ax, fontProperties)
  ax.set_axis_off()
  ax.set_position([0, 0, 1, 1])
  plt.savefig("blubb.pdf", facecolor="none", transparent=True)
