import streamlit as st
import json
import os
from PIL import Image, ImageDraw, ImageFont
import zipfile
import io
import shutil

def annotation_main():
    # Set up directories
    IMAGE_FOLDER = 'data'
    OUTPUT_FOLDER = 'annotated_images'
    EXTRACTED_JSON_FILE = 'extracted_data_with_labels.json'

    # Create output folder if it doesn't exist
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    

    # Font for annotation text
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except IOError:
        font = ImageFont.load_default()

    st.title('DICOM Image Annotation Tool')

    # Upload JSON file
    st.subheader('Upload JSON file with annotations')
    uploaded_json = st.file_uploader('Choose a JSON file', type='json')

    if uploaded_json:
        try:
            data = json.load(uploaded_json)
            st.write('JSON file loaded successfully.')
            st.write('Data preview:', data)
            st.session_state['json_data'] = data
        except (json.JSONDecodeError, TypeError):
            st.error("Invalid JSON file. Please upload a valid JSON file.")

    # Upload images
    upload_option = st.selectbox(
        'Choose how to upload images:',
        ['Upload Single Image', 'Upload Multiple Images', 'Upload Folder of Images (ZIP)']
    )

    if upload_option == 'Upload Single Image':
        uploaded_image = st.file_uploader('Choose a single image file', type=['jpg', 'jpeg', 'png'])
        if uploaded_image:
            os.makedirs(IMAGE_FOLDER, exist_ok=True)
            image = Image.open(uploaded_image)
            image_path = os.path.join(IMAGE_FOLDER, uploaded_image.name)
            image.save(image_path)
            st.write(f'Image saved to {image_path}')

    elif upload_option == 'Upload Multiple Images':
        uploaded_images = st.file_uploader('Choose multiple image files', type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
        if uploaded_images:
            os.makedirs(IMAGE_FOLDER, exist_ok=True)
            for image_file in uploaded_images:
                image = Image.open(image_file)
                image_path = os.path.join(IMAGE_FOLDER, image_file.name)
                image.save(image_path)
            st.write('Images uploaded and saved.')

    elif upload_option == 'Upload Folder of Images (ZIP)':
        uploaded_zip = st.file_uploader('Choose a ZIP file containing images', type='zip')
        if uploaded_zip:
            with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
                zip_ref.extractall(IMAGE_FOLDER)
            st.write('Images extracted from ZIP file and saved.')

    # Extract relevant JSON
    if st.button('Extract Relevant JSON'):
        if 'json_data' in st.session_state:
            data = st.session_state['json_data']
            if 'categories' in data and 'annotations' in data:
                category_mapping = {category['id']: category['name'] for category in data.get('categories', [])}

                extracted_data = []
                for image in data.get('images', []):
                    image_id = image.get('id')
                    file_name = image.get('file_name')

                    annotations = []
                    for ann in data.get('annotations', []):
                        if ann.get('image_id') == image_id:
                            category_id = ann.get('category_id')
                            annotations.append({
                                'bbox': ann.get('bbox'),
                                'label': category_id,
                                'category_name': category_mapping.get(category_id)
                            })

                    extracted_data.append({
                        'image_id': image_id,
                        'name': file_name,
                        'annotations': annotations
                    })

                with open(EXTRACTED_JSON_FILE, 'w') as outfile:
                    json.dump(extracted_data, outfile, indent=4)

                st.write(f'Extracted data saved to {EXTRACTED_JSON_FILE}')
                st.session_state['extracted_json'] = EXTRACTED_JSON_FILE
            else:
                st.error("The provided JSON file is not correctly structured for extraction. Please upload a valid JSON file.")
        else:
            st.error('No JSON data to extract from. Please upload a JSON file.')

    # Download relevant JSON
    if 'extracted_json' in st.session_state:
        st.subheader('Download Extracted JSON')
        with open(st.session_state['extracted_json'], 'rb') as file:
            st.download_button('Download Extracted JSON', file, file_name='extracted_data_with_labels.json')

    # Annotate images
    if st.button('Annotate Images'):
        if 'json_data' in st.session_state:
            data = st.session_state['json_data']
            if 'annotations' not in data[0]:
                st.error("Please first extract the relevant JSON file using the button provided, then upload it for annotating the images.")
            else:
                annotated_files = []
                for item in data:
                    image_id = item['image_id']
                    image_name = item['name']
                    annotations = item['annotations']

                    image_path = os.path.join(IMAGE_FOLDER, image_name)
                    if os.path.exists(image_path):
                        image = Image.open(image_path)
                        draw = ImageDraw.Draw(image)

                        for ann in annotations:
                            bbox = ann['bbox']
                            category_name = ann['category_name']

                            x1, y1, width, height = bbox
                            x2 = x1 + width
                            y2 = y1 + height

                            draw.rectangle([x1, y1, x2, y2], outline="red", width=8)

                            text_width, text_height = draw.textsize(category_name, font=font)
                            text_x = x1
                            text_y = y1 - text_height if y1 - text_height > 0 else y1 + 10

                            draw.rectangle([text_x, text_y, text_x + text_width + 20, text_y + text_height + 10], fill="white")
                            draw.text((text_x + 10, text_y + 5), category_name, fill="black", font=font)

                        output_path = os.path.join(OUTPUT_FOLDER, image_name)
                        image.save(output_path)
                        annotated_files.append(output_path)

                if len(annotated_files) == 1:
                    with open(annotated_files[0], "rb") as file:
                        a=st.download_button("Download Annotated Image", file, file_name=os.path.basename(annotated_files[0]))
                        print(a,"hfghdgfhd")
                        
                else:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                        for file_path in annotated_files:
                            zip_file.write(file_path, os.path.basename(file_path))
                    zip_buffer.seek(0)
                    st.download_button("Download Annotated Images (ZIP)", zip_buffer, file_name="annotated_images.zip")
                  

                st.write('All images have been annotated.')
        else:
            st.error('No JSON data to annotate images with. Please upload a JSON file.')

def cleanup():
    """Delete the folders and their contents."""
    try:
        shutil.rmtree('data')
        shutil.rmtree('annotated_images')
        st.success("All temporary files and folders have been cleaned up.")
    except Exception as e:
        st.error(f"An error occurred while cleaning up: {e}")


