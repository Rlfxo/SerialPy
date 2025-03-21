from ..utils.file_utils import FileUtils

class FileController:
    @staticmethod
    def validate_firmware_file(file_path, firmware_type):
        if not file_path:
            return False
        return FileUtils.is_valid_firmware_file(file_path)

    @staticmethod
    def get_file_info(file_path):
        if not file_path:
            return "No file selected"
        return file_path
