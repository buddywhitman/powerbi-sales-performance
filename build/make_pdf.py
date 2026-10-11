import os, glob
from PIL import Image
D = r"D:\OneDrive\Documents\repos\powerbi\deliverables"
order = ["Sales Overview", "Product Analysis", "Customer Analysis", "Geographic Performance", "Scenario Planner", "Sales Rep Detail"]
imgs = []
for n in order:
    im = Image.open(os.path.join(D, n + ".png")).convert("RGB")
    w, h = im.size
    k = w / 2000.0
    crop = im.crop((int(16 * k), int(84 * k), int(1677 * k), int(1017 * k)))
    crop.save(os.path.join(D, "cropped_" + n.replace(" ", "_") + ".png"))
    imgs.append(crop.resize((1600, int(1600 * crop.size[1] / crop.size[0]))))
imgs[0].save(os.path.join(D, "SalesPerformance_Dashboard.pdf"), save_all=True, append_images=imgs[1:], resolution=110)
print("pdf ok", imgs[0].size)
