import os

class FileUtils:
    @staticmethod
    def get_file_extension(file_path):
        return os.path.splitext(file_path)[1].lower()

    @staticmethod
    def is_valid_firmware_file(file_path):
        valid_extensions = ['.hex', '.bin']
        return FileUtils.get_file_extension(file_path) in valid_extensions

    @staticmethod
    def get_project_root():
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
