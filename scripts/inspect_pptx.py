import pptx

pptx_path = r"c:\Users\daipa\Desktop\WIMS 2022 - Dissertation Documents\Evidence-Grounded Generative AI.pptx"
prs = pptx.Presentation(pptx_path)

print(f"Total slides: {len(prs.slides)}")
print(f"Slide width: {prs.slide_width / 914400} inches, height: {prs.slide_height / 914400} inches")

for idx, slide in enumerate(prs.slides):
    print(f"\n--- Slide {idx+1} ---")
    for shape in slide.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                t = p.text.strip()
                if t:
                    print(f"  [Text] {t[:80]}")
        elif shape.has_table:
            print(f"  [Table] {len(shape.table.rows)} rows x {len(shape.table.columns)} cols")
        elif shape.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.PICTURE:
            print(f"  [Picture] size={shape.width/914400:.1f}x{shape.height/914400:.1f} in")
