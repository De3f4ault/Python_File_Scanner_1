# output_handlers/compressed_handler.py
import gzip
import bz2
import lzma
import json
import csv
from pathlib import Path
from datetime import datetime

class CompressedOutputMixin:
    """Mixin to add compression support to any output handler"""

    COMPRESSION_HANDLERS = {
        'gzip': {'module': gzip, 'ext': '.gz', 'mode': 'wt', 'level_param': 'compresslevel'},
        'bz2': {'module': bz2, 'ext': '.bz2', 'mode': 'wt', 'level_param': 'compresslevel'},
        'lzma': {'module': lzma, 'ext': '.xz', 'mode': 'wt', 'level_param': 'preset'},
        'none': {'module': None, 'ext': '', 'mode': 'w', 'level_param': None}
    }

    @classmethod
    def get_compressed_path(cls, output_path, compression='gzip'):
        """Get the output path with appropriate compression extension"""
        path = Path(output_path)
        comp_info = cls.COMPRESSION_HANDLERS.get(compression, cls.COMPRESSION_HANDLERS['none'])

        if comp_info['ext'] and not str(path).endswith(comp_info['ext']):
            return str(path) + comp_info['ext']
        return str(path)

    @classmethod
    def open_compressed(cls, output_path, compression='gzip', compression_level=6):
        """Open file with appropriate compression"""
        comp_info = cls.COMPRESSION_HANDLERS.get(compression, cls.COMPRESSION_HANDLERS['none'])

        if comp_info['module']:
            kwargs = {comp_info['level_param']: compression_level} if comp_info['level_param'] else {}
            return comp_info['module'].open(output_path, comp_info['mode'], encoding='utf-8', **kwargs)
        else:
            return open(output_path, comp_info['mode'], encoding='utf-8')

    @classmethod
    def get_compression_info(cls, data, compression='gzip'):
        """Get estimated compression statistics"""
        if compression == 'none':
            return {'original_size': 0, 'compressed_size': 0, 'ratio': 1.0}

        # Estimate based on typical text compression ratios
        estimated_text_size = sum(len(str(item.get('content', ''))) + len(str(item.get('path', ''))) for item in data)

        compression_ratios = {
            'gzip': 0.25,  # ~75% compression for text
            'bz2': 0.20,   # ~80% compression for text
            'lzma': 0.15   # ~85% compression for text
        }

        ratio = compression_ratios.get(compression, 0.25)

        return {
            'original_size': estimated_text_size,
            'compressed_size': int(estimated_text_size * ratio),
            'ratio': ratio,
            'savings_percent': (1 - ratio) * 100
        }


class CompressedTXTHandler(CompressedOutputMixin):
    @classmethod
    def write(cls, data, output_path, compression='gzip', compression_level=6):
        """Write TXT with compression support and enhanced formatting"""
        final_path = cls.get_compressed_path(output_path, compression)
        comp_info = cls.get_compression_info(data, compression)

        with cls.open_compressed(final_path, compression, compression_level) as f:
            # Enhanced header with metadata
            f.write("╔" + "═" * 58 + "╗\n")
            f.write("║" + " FILE SCANNER REPORT ".center(58) + "║\n")
            f.write("╠" + "═" * 58 + "╣\n")
            f.write(f"║ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<44} ║\n")
            f.write(f"║ Compression: {compression.upper():<42} ║\n")
            f.write(f"║ Total Files: {len(data):<42} ║\n")

            if compression != 'none':
                f.write(f"║ Est. Compression: {comp_info['savings_percent']:.1f}% savings{'':<25} ║\n")

            f.write("╚" + "═" * 58 + "╝\n\n")

            # Table of contents
            if len(data) > 5:
                f.write("📁 TABLE OF CONTENTS\n")
                f.write("=" * 50 + "\n")
                for i, item in enumerate(data[:20], 1):  # Show first 20
                    path = item['path']
                    if len(path) > 45:
                        path = "..." + path[-42:]
                    f.write(f"{i:3d}. {path}\n")

                if len(data) > 20:
                    f.write(f"    ... and {len(data) - 20} more files\n")
                f.write("\n" + "=" * 50 + "\n\n")

            # File contents
            for i, item in enumerate(data, 1):
                f.write(f"📄 [{i:04d}] {item['path']}\n")
                f.write("─" * 60 + "\n")

                # File metadata
                size = item.get('size', 'Unknown')
                if isinstance(size, int):
                    if size < 1024:
                        size_str = f"{size} bytes"
                    elif size < 1024 * 1024:
                        size_str = f"{size/1024:.1f} KB"
                    else:
                        size_str = f"{size/(1024*1024):.1f} MB"
                else:
                    size_str = str(size)

                f.write(f"📊 Size: {size_str}")

                if 'extension' in item and item['extension']:
                    f.write(f" | Type: {item['extension']}")

                if item.get('is_hidden', False):
                    f.write(" | 🔒 Hidden")

                f.write("\n")

                # Modified date
                if 'modified' in item:
                    try:
                        mod_time = datetime.fromtimestamp(item['modified'])
                        f.write(f"📅 Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    except:
                        pass

                f.write("\n📝 Content:\n")

                # Add line numbers to content
                content = item.get('content', '[No content]')
                if content and content != '[No content]':
                    lines = content.split('\n')
                    for line_num, line in enumerate(lines, 1):
                        f.write(f"{line_num:4d} | {line}\n")
                else:
                    f.write("     | [Empty or binary file]\n")

                f.write("\n" + "═" * 60 + "\n\n")

        return final_path


class CompressedJSONHandler(CompressedOutputMixin):
    @classmethod
    def write(cls, data, output_path, compression='gzip', compression_level=6):
        """Write JSON with compression support and enhanced metadata"""
        final_path = cls.get_compressed_path(output_path, compression)
        comp_info = cls.get_compression_info(data, compression)

        with cls.open_compressed(final_path, compression, compression_level) as f:
            enhanced_data = {
                'metadata': {
                    'generated': datetime.now().isoformat(),
                    'version': '2.0',
                    'total_files': len(data),
                    'compression': {
                        'algorithm': compression,
                        'level': compression_level if compression != 'none' else None,
                        'estimated_savings': f"{comp_info['savings_percent']:.1f}%" if compression != 'none' else "0%"
                    },
                    'file_types': cls._get_file_type_stats(data),
                    'size_distribution': cls._get_size_stats(data)
                },
                'files': data
            }
            json.dump(enhanced_data, f, indent=2, ensure_ascii=False)

        return final_path

    @classmethod
    def _get_file_type_stats(cls, data):
        """Get statistics about file types in the data"""
        type_counts = {}
        for item in data:
            ext = item.get('extension', 'no_extension')
            type_counts[ext] = type_counts.get(ext, 0) + 1
        return dict(sorted(type_counts.items(), key=lambda x: x[1], reverse=True))

    @classmethod
    def _get_size_stats(cls, data):
        """Get statistics about file sizes"""
        sizes = [item.get('size', 0) for item in data if isinstance(item.get('size'), int)]
        if not sizes:
            return {'min': 0, 'max': 0, 'avg': 0, 'total': 0}

        return {
            'min': min(sizes),
            'max': max(sizes),
            'avg': sum(sizes) // len(sizes),
            'total': sum(sizes)
        }


class CompressedCSVHandler(CompressedOutputMixin):
    @classmethod
    def write(cls, data, output_path, compression='gzip', compression_level=6):
        """Write CSV with compression support and enhanced columns"""
        final_path = cls.get_compressed_path(output_path, compression)

        with cls.open_compressed(final_path, compression, compression_level) as f:
            fieldnames = [
                'path', 'content', 'size', 'extension', 'is_hidden',
                'modified', 'line_count', 'char_count'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\n')

            # Write header with metadata
            writer.writeheader()

            # Write metadata row (optional, can be filtered out)
            writer.writerow({
                'path': f'# Generated: {datetime.now().isoformat()}',
                'content': f'# Compression: {compression}',
                'size': f'# Total Files: {len(data)}',
                'extension': '# METADATA_ROW',
                'is_hidden': '',
                'modified': '',
                'line_count': '',
                'char_count': ''
            })

            # Write data rows with enhanced information
            for item in data:
                content = item.get('content', '')

                # Calculate additional metrics
                line_count = len(content.split('\n')) if content else 0
                char_count = len(content) if content else 0

                # Format modification time
                modified_str = ''
                if 'modified' in item:
                    try:
                        modified_str = datetime.fromtimestamp(item['modified']).isoformat()
                    except:
                        modified_str = str(item.get('modified', ''))

                writer.writerow({
                    'path': item.get('path', ''),
                    'content': content,
                    'size': item.get('size', ''),
                    'extension': item.get('extension', ''),
                    'is_hidden': item.get('is_hidden', False),
                    'modified': modified_str,
                    'line_count': line_count,
                    'char_count': char_count
                })

        return final_path


# Updated original handlers to maintain compatibility
class TXTHandler(CompressedTXTHandler):
    @staticmethod
    def write(data, output_path):
        return CompressedTXTHandler.write(data, output_path, compression='none')


class JSONHandler(CompressedJSONHandler):
    @staticmethod
    def write(data, output_path):
        return CompressedJSONHandler.write(data, output_path, compression='none')


class CSVHandler(CompressedCSVHandler):
    @staticmethod
    def write(data, output_path):
        return CompressedCSVHandler.write(data, output_path, compression='none')
