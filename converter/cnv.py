import streamlit as st
import os
import shutil
import zipfile
from converter.scriptt import DICOMConverter  # Assuming your DICOMConverter class is in DICOMConverter.py

def main():
    # Initialize the converter
    converter = DICOMConverter()

    # Streamlit frontend
    st.title("DICOM Conversion Tool")

    # File upload option
    uploaded_files = st.file_uploader("Upload DICOM files or images", type=["dcm", "dicom", "jpg", "jpeg", "png"], accept_multiple_files=True)
    conversion_type = st.selectbox("Choose Conversion Type", ("DICOM to PNG", "DICOM to JPEG", "PNG to DICOM", "JPEG to DICOM"))

    # Temporary directory to store uploaded files
    temp_dir = "temp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    if uploaded_files:
        st.write(f"{len(uploaded_files)} files uploaded.")

        # Save uploaded files to temporary directory
        file_paths = []
        for uploaded_file in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            file_paths.append(file_path)

        # Perform conversion
        if st.button("Convert"):
            output_files = []
            for file_path in file_paths:
                if conversion_type == "DICOM to PNG":
                    output_files.append(converter.dicom_to_png(file_path))
                elif conversion_type == "DICOM to JPEG":
                    output_files.append(converter.dicom_to_jpeg(file_path))
                elif conversion_type == "PNG to DICOM":
                    output_files.append(converter.png_to_dicom(file_path))
                elif conversion_type == "JPEG to DICOM":
                    output_files.append(converter.jpg_to_dicom(file_path))

            # If multiple files were converted, create a zip file
            if len(output_files) > 1:
                zip_path = os.path.join(temp_dir, "converted_files.zip")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for output_file in output_files:
                        zipf.write(output_file, os.path.basename(output_file))
                st.success("Conversion successful!")
                with open(zip_path, "rb") as f:
                    st.download_button(label="Download Result", data=f, file_name="converted_files.zip")
            else:
                # Single file conversion
                st.success("Conversion successful!")
                with open(output_files[0], "rb") as f:
                    st.download_button(label="Download Result", data=f, file_name=os.path.basename(output_files[0]))

            # Clean up temporary files
            shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)  # Recreate the temp directory for the next use

    # Final cleanup when the app stops
    if st.button("Clean Up"):
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            st.write("Temporary files cleaned up.")

# Call the main function when this script is run
if __name__ == "__main__":
    main()
