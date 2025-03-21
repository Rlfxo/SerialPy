import hashlib
import binascii
from typing import Dict, Any

class HeaderManager:
    def __init__(self):
        self.HEADER_SIZE = 1024
        self.header_fields = {
            'sha256': {'size': 32, 'editable': False},
            'length': {'size': 4, 'editable': False},
            'model_name': {'size': 64, 'editable': True},
            'cpo_id': {'size': 32, 'editable': True},
            'version': {'size': 3, 'editable': True},
            'image_type': {'size': 1, 'editable': True},
            'dev_version': {'size': 16, 'editable': False},
            'debug_level': {'size': 1, 'editable': True}
        }

    def read_header(self, file_path: str) -> Dict[str, Any]:
        """파일에서 헤더 정보 읽기"""
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
                if len(file_data) < self.HEADER_SIZE:
                    raise Exception(f"파일이 너무 작습니다. (최소 {self.HEADER_SIZE} 바이트 필요)")

                header_info = {}
                offset = 0

                for field, config in self.header_fields.items():
                    size = config['size']
                    value = file_data[offset:offset + size]

                    if field == 'sha256':
                        header_info[field] = value.hex()
                    elif field == 'length':
                        header_info[field] = int.from_bytes(value, 'little')
                    elif field in ['model_name', 'cpo_id', 'dev_version']:
                        try:
                            header_info[field] = value.split(b'\x00')[0].decode('utf-8')
                        except:
                            header_info[field] = "N/A"
                    else:
                        header_info[field] = value.hex()

                    offset += size

                return header_info

        except Exception as e:
            raise Exception(f"헤더 읽기 실패: {str(e)}")
