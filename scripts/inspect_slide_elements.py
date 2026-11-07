import pptx

prs = pptx.Presentation(r"c:\Users\daipa\Desktop\WIMS 2022 - Dissertation Documents\Evidence-Grounded Generative AI.pptx")
slide2 = prs.slides[1]

print("=== SLIDE 2 ELEMENTS ===")
for s in slide2.shapes:
    print(f"Shape: name={s.name}, type={s.shape_type}, left={s.left/914400:.2f}, top={s.top/914400:.2f}, width={s.width/914400:.2f}, height={s.height/914400:.2f}")
    if s.has_text_frame:
        print(f"   Text: {s.text_frame.text[:60]!r}")
        for p in s.text_frame.paragraphs[:2]:
            if p.font.name:
                print(f"      Font: {p.font.name}, size={p.font.size.pt if p.font.size else 'None'}, color={p.font.color.rgb if p.font.color else 'None'}")
