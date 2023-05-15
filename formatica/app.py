import os
import streamlit as st
from pathlib import Path
from image_processing import process_image
from streamlit_cropper import st_cropper

import PIL
from PIL import Image, ImageOps
import shutil
import zipfile

def files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

st.set_page_config(page_title="Image Standardizer", layout="centered")

st.title("Image Standardizer")

st.sidebar.header("Crop Settings")
#realtime_update = st.sidebar.checkbox(label="Update in Real Time", value=True)
box_color = st.sidebar.color_picker(label="Cropping Box Color", value='#0000FF')
aspect_choice = st.sidebar.radio(label="Aspect Ratio", options=["1:1", "16:9", "4:3", "2:3", "Free"])

aspect_dict = {
    "1:1": (1, 1),
    "16:9": (16, 9),
    "4:3": (4, 3),
    "2:3": (2, 3),
    "Free": None
}
aspect_ratio = aspect_dict[aspect_choice]

st.sidebar.header("Border Settings")
border_color = st.sidebar.color_picker(label="Border Color", value="#6ea84e")
border_thickness = st.sidebar.number_input(label="Border Thickness", min_value=0.00)

uploaded_files = st.file_uploader("Upload a folder of images (.zip)", type=["zip"], accept_multiple_files=False)

if uploaded_files is not None:
    output_path = "output"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    crop_path = "crop"
    if not os.path.exists(crop_path):
        os.mkdir(crop_path)

    with zipfile.ZipFile(uploaded_files, "r") as zip_ref:
        zip_ref.extractall("temp_input")

    input_path = "temp_input"
    
    with st.spinner("Please crop all of your photos to the desired aspect ratio..."):
        # Get a cropped image from the frontend
        i = 1
        for file in files(input_path):
            print(file)
            input_filepath = input_path + "/" + str(file)
            crop_filepath = crop_path + "/" + str(file)
            image = Image.open(input_filepath)
            st.header("Photo # " + str(i))
            col1, col2 = st.columns(2)
            col1.info("Drag the crop box over the area to keep, double click the image to save, hit the button to finalize ->")
            save_button = col2.button("I'm done with this image", key = "button_" + file) 
            
            cropped_img = st_cropper(image, realtime_update=False, box_color = box_color,
                                    aspect_ratio = aspect_ratio, key = "cropper_" + file)
            
            if save_button:
                cropped_img.save(crop_filepath, "PNG")
                col2.success("Successfully cropped photo. Remember to finish all remaining crops before proceeding with the next step!")

            i = i+1

        st.write("")
        if st.button("*Click here when finished cropping photos!*"):
            with st.spinner("Thank you for cropping your photos. Finishing up the processing now..."):
                #Resizing and applying border
                for file in files(crop_path):
                    if any((extension in file) for extension in [".png", ".jpg", ".jpeg", ".webp"]):
                        filepath = crop_path + "/" +str(file)
                        print(filepath)
                        process_image(filepath, border_thickness=int(border_thickness), border_color=border_color)

                shutil.make_archive("processed_images", "zip", output_path)

                shutil.rmtree(input_path)
                shutil.rmtree(output_path)
                shutil.rmtree(crop_path)

                st.success("Images processed successfully!")
                with open("processed_images.zip", "rb") as file:
                    st.download_button(label="Download Images", data=file, file_name="processed_images.zip", mime="application/zip")

