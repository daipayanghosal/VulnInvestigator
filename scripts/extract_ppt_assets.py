import pptx
import os

prs = pptx.Presentation(r"c:\Users\daipa\Desktop\WIMS 2022 - Dissertation Documents\Evidence-Grounded Generative AI.pptx")
out_dir = r"c:\Users\daipa\Desktop\WIMS 2022 - Dissertation Documents\Project\scripts\extracted_ppt_assets"
os.makedirs(out_dir, exist_ok=True)

img_idx = 0
for s_idx, slide in enumerate(prs.slides):
    for shape in slide.shapes:
        if shape.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.PICTURE:
            img = shape.image
            filename = f"slide_{s_idx+1}_img_{img_idx+1}.{img.ext}"
            filepath = os.path.join(out_dir, filename)
            with open(filepath, "wb") as f:
                f.write(img.blob)
            print(f"Extracted: {filename} ({len(img.blob)} bytes, {shape.width/914400:.2f}x{shape.height/914400:.2f} in)")
            img_idx += 1
