import pydicom
import numpy as np
import cv2
import os
import datetime
import zipfile

class DICOMConverter:

    def __init__(self):
        # Create the output directory if it doesn't exist
        if not os.path.exists('output'):
            os.makedirs('output')

    def dicom_to_png(self, dicom_path):
        output_files = []
        if os.path.isdir(dicom_path):
            for file_name in os.listdir(dicom_path):
                file_path = os.path.join(dicom_path, file_name)
                if os.path.isfile(file_path):
                    output_file = self._convert_dicom_to_png(file_path)
                    output_files.append(output_file)
        else:
            output_file = self._convert_dicom_to_png(dicom_path)
            output_files.append(output_file)

        return self._create_zip_or_return_single(output_files)

    def dicom_to_jpeg(self, dicom_path):
        output_files = []
        if os.path.isdir(dicom_path):
            for file_name in os.listdir(dicom_path):
                file_path = os.path.join(dicom_path, file_name)
                if os.path.isfile(file_path):
                    output_file = self._convert_dicom_to_jpeg(file_path)
                    output_files.append(output_file)
        else:
            output_file = self._convert_dicom_to_jpeg(dicom_path)
            output_files.append(output_file)

        return self._create_zip_or_return_single(output_files)

    def png_to_dicom(self, png_path):
        output_files = []
        if os.path.isdir(png_path):
            for file_name in os.listdir(png_path):
                file_path = os.path.join(png_path, file_name)
                if os.path.isfile(file_path):
                    output_file = self._convert_png_to_dicom(file_path)
                    output_files.append(output_file)
        else:
            output_file = self._convert_png_to_dicom(png_path)
            output_files.append(output_file)

        return self._create_zip_or_return_single(output_files)

    def jpg_to_dicom(self, image_path):
        output_files = []
        if os.path.isdir(image_path):
            for file_name in os.listdir(image_path):
                file_path = os.path.join(image_path, file_name)
                if os.path.isfile(file_path):
                    output_file = self._convert_jpg_to_dicom(file_path)
                    output_files.append(output_file)
        else:
            output_file = self._convert_jpg_to_dicom(image_path)
            output_files.append(output_file)

        return self._create_zip_or_return_single(output_files)

    def _convert_dicom_to_png(self, dicom_path):
        dicom = self._load_dicom(dicom_path)
        pixel_array = dicom.pixel_array
        pixel_array = cv2.normalize(pixel_array, None, 0, 255, cv2.NORM_MINMAX)
        pixel_array = np.uint8(pixel_array)
        output_path = os.path.join('output', self._change_extension(dicom_path, '.png'))
        cv2.imwrite(output_path, pixel_array)
        return output_path

    def _convert_dicom_to_jpeg(self, dicom_path):
        dicom = self._load_dicom(dicom_path)
        pixel_array = dicom.pixel_array
        pixel_array = cv2.normalize(pixel_array, None, 0, 255, cv2.NORM_MINMAX)
        pixel_array = np.uint8(pixel_array)
        output_path = os.path.join('output', self._change_extension(dicom_path, '.jpeg'))
        cv2.imwrite(output_path, pixel_array, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        return output_path

    def _convert_png_to_dicom(self, png_path):
        image = cv2.imread(png_path, cv2.IMREAD_GRAYSCALE)
        image = np.uint16(image)
        dicom = self._create_minimal_dicom(image.shape)
        dicom.PixelData = image.tobytes()
        output_path = os.path.join('output', self._change_extension(png_path, '.dicom'))
        dicom.save_as(output_path)
        return output_path

    def _convert_jpg_to_dicom(self, image_path):
        _, ext = os.path.splitext(image_path)
        if ext.lower() not in ['.jpg', '.jpeg']:
            raise ValueError("Unsupported file extension. Please provide a .jpg or .jpeg file.")
        
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        image = np.uint16(image)
        dicom = self._create_minimal_dicom(image.shape)
        dicom.PixelData = image.tobytes()
        output_path = os.path.join('output', self._change_extension(image_path, '.dicom'))
        dicom.save_as(output_path)
        return output_path

    def _load_dicom(self, dicom_path):
        _, ext = os.path.splitext(dicom_path)
        if ext.lower() in ['.dcm', '.dicom']:
            dicom = pydicom.dcmread(dicom_path)
            if not hasattr(dicom.file_meta, 'TransferSyntaxUID'):
                dicom.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
            return dicom
        else:
            raise ValueError("Unsupported file extension. Please provide a file with .dcm or .dicom extension.")

    def _create_minimal_dicom(self, image_shape):
        dicom = pydicom.dataset.FileDataset(None, {}, file_meta=pydicom.dataset.FileMetaDataset(), preamble=b"\0" * 128)
        dicom.SOPClassUID = pydicom.uid.generate_uid()
        dicom.SOPInstanceUID = pydicom.uid.generate_uid()
        dicom.PatientName = "Test^Patient"
        dicom.PatientID = "123456"
        dicom.StudyInstanceUID = pydicom.uid.generate_uid()
        dicom.SeriesInstanceUID = pydicom.uid.generate_uid()
        dicom.Modality = "OT"
        dicom.StudyID = "1"
        dicom.SeriesNumber = "1"
        dicom.InstanceNumber = "1"
        dicom.Rows = image_shape[0]
        dicom.Columns = image_shape[1]
        dicom.BitsAllocated = 16
        dicom.BitsStored = 16
        dicom.HighBit = 15
        dicom.PixelRepresentation = 0
        dicom.SamplesPerPixel = 1
        dicom.PhotometricInterpretation = "MONOCHROME2"
        dt = datetime.datetime.now()
        dicom.StudyDate = dt.strftime('%Y%m%d')
        dicom.StudyTime = dt.strftime('%H%M%S')
        dicom.ContentDate = dt.strftime('%Y%m%d')
        dicom.ContentTime = dt.strftime('%H%M%S')

        return dicom

    def _change_extension(self, path, new_ext):
        return os.path.splitext(os.path.basename(path))[0] + new_ext

    def _create_zip_or_return_single(self, output_files):
        if len(output_files) > 1:
            zip_file_path = 'output/output_files.zip'
            with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                for file in output_files:
                    zipf.write(file, os.path.basename(file))
                    os.remove(file)  # Remove the individual file after adding to the zip
            return zip_file_path
        else:
            return output_files[0]

# Example usage
# converter = DICOMConverter()
# converter.dicom_to_png('dicom')  # Can be a file or a folder
# converter.dicom_to_jpeg('normal')  # Can be a file or a folder
# converter.png_to_dicom('png')  # Can be a file or a folder
# converter.jpg_to_dicom('jpeg')  # Can be a file or a folder