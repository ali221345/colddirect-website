import os
phone = "07983 759320"
areas = ["Enfield", "Barnet", "Camden", "Islington", "Hackney", "Tottenham", "Wood Green", "Edmonton", "Chingford", "Walthamstow"]

for area in areas:
    filename = f"cold-room-repair-{area.lower().replace(' ', '-')}.html"
    content = f"""<html><head><title>Cold Room Repair {area} - 24/7 | Cold Direct</title></head><body><h1>Cold Room Repair {area}</h1><p>Emergency cold room repair in {area}. Call {phone} 24/7</p><h2>Call {phone}</h2></body></html>"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"{filename} ok")

print("Done!")
