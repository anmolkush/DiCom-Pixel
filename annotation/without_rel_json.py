import streamlit as st
import json
import os
from PIL import Image, ImageDraw, ImageFont
import zipfile
import io
import tempfile

def extract_relevant_json_data(json_data):
    """Extract relevant data from any provided JSON file for image annotation."""
    if 'categories' in json_data and 'annotations' in json_data:
        category_mapping = {category['id']: category['name'] for category in json_data.get('categories', [])}
        extracted_data = []

        for image in json_data.get('images', []):
            image_id = image.get('id')
            file_name = image.get('file_name')

            annotations = []
            for ann in json_data.get('annotations', []):
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

        return extracted_data
    else:
        st.error("The provided JSON file does not contain the necessary structure. Please upload a valid JSON file.")
        return None

def annotation_main():
    # Create temporary directories
    with tempfile.TemporaryDirectory() as image_folder, tempfile.TemporaryDirectory() as output_folder:
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
                json_data = json.load(uploaded_json)
                st.write('JSON file loaded successfully.')
                st.write('Data preview:', json_data)
                st.session_state['json_data'] = extract_relevant_json_data(json_data)
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
                image = Image.open(uploaded_image)
                image_path = os.path.join(image_folder, uploaded_image.name)
                image.save(image_path)
                st.write(f'Image saved to {image_path}')

        elif upload_option == 'Upload Multiple Images':
            uploaded_images = st.file_uploader('Choose multiple image files', type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
            if uploaded_images:
                for image_file in uploaded_images:
                    image = Image.open(image_file)
                    image_path = os.path.join(image_folder, image_file.name)
                    image.save(image_path)
                st.write('Images uploaded and saved.')

        elif upload_option == 'Upload Folder of Images (ZIP)':
            uploaded_zip = st.file_uploader('Choose a ZIP file containing images', type='zip')
            if uploaded_zip:
                with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
                    zip_ref.extractall(image_folder)
                st.write('Images extracted from ZIP file and saved.')

        # Annotate images
        if st.button('Annotate Images'):
            if 'json_data' in st.session_state:
                data = st.session_state['json_data']
                if data is None:
                    st.error("Please upload a valid JSON file.")
                else:
                    annotated_files = []
                    for item in data:
                        image_id = item['image_id']
                        image_name = item['name']
                        annotations = item['annotations']

                        image_path = os.path.join(image_folder, image_name)
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

                            output_path = os.path.join(output_folder, image_name)
                            image.save(output_path)
                            annotated_files.append(output_path)

                    if len(annotated_files) == 1:
                        with open(annotated_files[0], "rb") as file:
                            st.download_button("Download Annotated Image", file, file_name=os.path.basename(annotated_files[0]))
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

if __name__ == '__main__':
    annotation_main()
