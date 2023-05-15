import os
import streamlit as st

st.set_option('deprecation.showfileUploaderEncoding', False)

import cv2
import numpy as np
import pytesseract
import imageio
from PIL import Image, ImageOps

# Set up Tesseract configuration
pytesseract.pytesseract.tesseract_cmd = '/usr/local/Cellar/tesseract/5.3.1/bin/tesseract'  # Update the path to your tesseract executable
config = '-l eng --oem 1 --psm 3'

# Function to resize and optimize images
def process_image(image_path: str, border_thickness: float = 0, border_color: str = '#000000'):
    # Load the image using OpenCV
    if ".webp" in image_path:
        data = imageio.imread(image_path)
        image = np.array(data)
        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    else:
        image = cv2.imread(image_path)
        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

    # Resize the image
    max_dimension = 2500
    height, width = image.shape[:2]
    print("Height:" + str(height))
    print("Width:" + str(width))
    existing_aspect_ratio = int(width) / int(height)

    if width > height:
        new_width = max_dimension
        new_height = int(new_width / existing_aspect_ratio)
    else:
        new_height = max_dimension
        new_width = int(new_height * existing_aspect_ratio)

    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # Convert the image to Pillow format
    pil_image = Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))
    
    # Extract text and save as image attribute (alt text)
    print("Extracting text from image...")
    extracted_text = pytesseract.image_to_string(pil_image, config=config)
    pil_image.info['alt'] = extracted_text

    # Add a border if specified
    if border_thickness > 0.00:
        print("Applying border to image...")
        pil_image = ImageOps.expand(pil_image, border=border_thickness, fill=border_color)

    # Save the processed image
    print(image_path)
    output_path = 'output/' + image_path.replace("crop/","")
    
    pil_image.save(output_path, quality=95, optimize=True)

    print(f"Processed image saved as: {output_path}")

# Main function
if __name__ == '__main__':
    input_directory = 'input_images'  # Update with your input directory
    border_thickness = 10  # Update with your desired border thickness
    border_color = '#FF0000'  # Update with your desired border color (hex)

    if not os.path.exists('output'):
        os.makedirs('output')

    for filename in os.listdir(input_directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_directory, filename)
            process_image(image_path, border_thickness, border_color)

