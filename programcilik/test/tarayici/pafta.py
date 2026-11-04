import sys, glob
from PIL import Image
desen, cikti = sys.argv[1], sys.argv[2]
yollar = sorted(glob.glob(desen))
ims = [Image.open(y) for y in yollar]
olc = 0.55
w, h = int(ims[0].width*olc), int(ims[0].height*olc)
sut = 4; sat = (len(ims)+sut-1)//sut
p = Image.new("RGB", (sut*w+(sut-1)*8, sat*h+(sat-1)*8), (128,128,128))
for i, im in enumerate(ims):
    p.paste(im.resize((w,h)), ((i%sut)*(w+8), (i//sut)*(h+8)))
p.save(cikti)
print(len(ims), p.size)
