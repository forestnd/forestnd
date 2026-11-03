import base64

# 1. Read your local logo image and convert to Base64
with open("logo.jpeg", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    image_data_uri = f"data:image/jpeg;base64,{encoded_string}"

# 2. Read your SVG template file
with open("badge-template.svg", "r", encoding="utf-8") as template_file:
    svg_content = template_file.read()

# 3. Replace the placeholder with the Base64 string
final_svg = svg_content.replace("{{BASE64_LOGO}}", image_data_uri)

# 4. Save out the final SVG file used by your README
with open("badge.svg", "w", encoding="utf-8") as output_file:
    output_file.write(final_svg)

print("Successfully generated badge.svg with embedded Base64 logo!")
