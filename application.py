#!/usr/bin/env python3
"""
Enhanced File Scanner Application
Phase 1 Implementation with Threading, Compression, and Better UI
"""

import sys
import os
import argparse
import curses
import signal
from pathlib import Path
from ui.terminal_ui import TerminalUI
from core.file_scanner import FileScanner
from config.settings import settings, save_user_config
import time

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        # Ensure curses exits cleanly
        try:
            curses.endwin()
        except:
            pass
        print("\n🛑 File Scanner interrupted by user")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Enhanced File Scanner - Scan directories for text files with threading and compression",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python application.py                           # Interactive mode
  python application.py --scan /path/to/dir      # Direct scan
  python application.py --workers 8              # Use 8 threads
  python application.py --compress gzip          # Force gzip compression
  python application.py --hidden                 # Include hidden files
  python application.py --optimize large         # Optimize for large directories
        """
    )

    # Scanning options
    parser.add_argument('--scan', '-s', type=str,
                       help='Directory to scan (skips interactive mode)')
    parser.add_argument('--output', '-o', type=str,
                       help='Output file path')
    parser.add_argument('--format', '-f', choices=['txt', 'json', 'csv'],
                       default=settings.default_output_format,
                       help='Output format')

    # Performance options
    parser.add_argument('--workers', '-w', type=int, default=settings.max_workers,
                       help='Number of worker threads')
    parser.add_argument('--max-size', type=int, default=settings.max_file_size,
                       help='Maximum file size to read (bytes)')

    # Compression options
    parser.add_argument('--compress', '-c', choices=['gzip', 'bz2', 'lzma', 'none'],
                       default=settings.default_compression,
                       help='Compression algorithm')
    parser.add_argument('--compression-level', type=int, default=settings.compression_level,
                       help='Compression level (1-9)')

    # Filtering options
    parser.add_argument('--hidden', action='store_true',
                       help='Include hidden files and directories')
    parser.add_argument('--no-hidden', action='store_true',
                       help='Explicitly exclude hidden files')

    # Optimization presets
    parser.add_argument('--optimize', choices=['large', 'small', 'code'],
                       help='Optimization preset (large dirs, small files, or code projects)')

    # Utility options
    parser.add_argument('--config', action='store_true',
                       help='Show current configuration')
    parser.add_argument('--benchmark', type=str,
                       help='Benchmark scanning performance on given directory')
    parser.add_argument('--version', action='version', version='File Scanner 2.0 (Phase 1)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')

    return parser.parse_args()

def apply_optimization_preset(preset: str):
    """Apply optimization presets"""
    if preset == 'large':
        settings.optimize_for_large_directories()
        print("🚀 Optimized for large directories")
    elif preset == 'small':
        settings.optimize_for_small_files()
        print("⚡ Optimized for small files")
    elif preset == 'code':
        settings.optimize_for_code_projects()
        print("💻 Optimized for code projects")

def show_config():
    """Display current configuration"""
    print("📋 Current Configuration:")
    print("=" * 50)

    print(f"Performance:")
    print(f"  Max workers: {settings.max_workers}")
    print(f"  Max file size: {settings.max_file_size} bytes ({settings.max_file_size/1024:.1f} KB)")
    print(f"  Chunk size: {settings.chunk_size} bytes")
    print(f"  Cache size: {settings.cache_size}")

    print(f"\nCompression:")
    print(f"  Default algorithm: {settings.default_compression}")
    print(f"  Compression level: {settings.compression_level}")
    print(f"  Auto-compress threshold: {settings.auto_compress_threshold/1024:.1f} KB")

    print(f"\nUI Settings:")
    print(f"  Show hidden files: {settings.show_hidden_files}")
    print(f"  Show hidden directories: {settings.show_hidden_directories}")
    print(f"  Use vim keys: {settings.use_vim_keys}")
    print(f"  Show file icons: {settings.show_file_icons}")

    print(f"\nExclusions:")
    print(f"  Excluded extensions: {len(settings.excluded_extensions)} types")
    print(f"  Excluded directories: {len(settings.excluded_directories)} names")
    print(f"  Text file extensions: {len(settings.text_file_extensions)} types")

def benchmark_scanning(directory: str, verbose: bool = False):
    """Benchmark scanning performance"""
    print(f"🔥 Benchmarking scan performance on: {directory}")
    print("=" * 60)

    if not Path(directory).exists():
        print(f"❌ Directory not found: {directory}")
        return

    # Test different worker counts
    worker_counts = [1, 2, 4, 8]
    results = []

    for workers in worker_counts:
        print(f"\n📊 Testing with {workers} workers...")

        scanner = FileScanner(max_workers=workers)
        scanner.set_include_hidden(False)

        start_time = time.time()
        result = scanner.scan_directory_threaded(directory)
        end_time = time.time()

        elapsed = end_time - start_time
        stats = result.get('stats', {})
        files_scanned = stats.get('files_scanned', 0)

        speed = files_scanned / elapsed if elapsed > 0 else 0

        results.append({
            'workers': workers,
            'elapsed': elapsed,
            'files': files_scanned,
            'speed': speed
        })

        print(f"   ⏱️  Time: {elapsed:.2f}s")
        print(f"   📁 Files: {files_scanned}")
        print(f"   ⚡ Speed: {speed:.1f} files/s")

    # Show best performance
    best = max(results, key=lambda x: x['speed'])
    print(f"\n🏆 Best performance: {best['workers']} workers at {best['speed']:.1f} files/s")

    # Show recommendations
    if best['workers'] != settings.max_workers:
        print(f"💡 Consider setting max_workers to {best['workers']} for this type of directory")

def run_command_line_scan(args):
    """Run a scan from command line arguments"""
    from output_handlers.compressed_handler import CompressedTXTHandler, CompressedJSONHandler, CompressedCSVHandler

    # Validate directory
    scan_path = Path(args.scan)
    if not scan_path.exists() or not scan_path.is_dir():
        print(f"❌ Invalid directory: {args.scan}")
        return 1

    # Setup output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path.cwd() / f"scan_results.{args.format}"
        if args.compress != 'none':
            output_path = Path(str(output_path) + f".{args.compress[0:2]}")  # .gz, .bz, .xz

    # Configure scanner
    scanner = FileScanner(
        max_size=args.max_size,
        max_workers=args.workers
    )
    scanner.set_include_hidden(args.hidden)

    # Progress callback for command line
    def progress_callback(current, total, scanned, skipped, current_file=""):
        if total > 0:
            percentage = (current / total) * 100
            bar_length = 40
            filled = int(percentage * bar_length / 100)
            bar = "█" * filled + "░" * (bar_length - filled)

            print(f"\r[{bar}] {percentage:.1f}% ({current}/{total}) - {scanned} scanned, {skipped} skipped",
                  end="", flush=True)

    scanner.set_progress_callback(progress_callback)

    # Start scan
    print(f"🔍 Scanning: {scan_path}")
    print(f"🧵 Workers: {args.workers}")
    print(f"💾 Output: {output_path}")
    print(f"🗜️  Compression: {args.compress}")
    print()

    start_time = time.time()
    result = scanner.scan_directory_threaded(str(scan_path))
    end_time = time.time()

    print()  # New line after progress bar

    if 'error' in result:
        print(f"❌ Scan failed: {result['error']}")
        return 1

    # Save results
    handler_map = {
        'txt': CompressedTXTHandler,
        'json': CompressedJSONHandler,
        'csv': CompressedCSVHandler
    }

    handler = handler_map[args.format]

    try:
        if args.compress != 'none':
            final_path = handler.write(result['files'], str(output_path),
                                     compression=args.compress,
                                     compression_level=args.compression_level)
        else:
            final_path = handler.write(result['files'], str(output_path), compression='none')

        # Show results
        elapsed = end_time - start_time
        stats = result.get('stats', {})

        print("✅ Scan completed successfully!")
        print(f"⏱️  Time: {elapsed:.2f} seconds")
        print(f"📁 Files scanned: {stats.get('files_scanned', 0)}")
        print(f"⏭️  Files skipped: {stats.get('files_skipped', 0)}")
        print(f"⚡ Speed: {stats.get('files_scanned', 0) / elapsed:.1f} files/second")
        print(f"💾 Output saved to: {final_path}")

        # Show file size
        try:
            file_size = Path(final_path).stat().st_size
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size/1024:.1f} KB"
            else:
                size_str = f"{file_size/(1024*1024):.1f} MB"
            print(f"📊 File size: {size_str}")
        except:
            pass

        return 0

    except Exception as e:
        print(f"❌ Error saving results: {str(e)}")
        return 1

def main():
    """Enhanced main function with command line support"""
    try:
        # Setup signal handlers
        setup_signal_handlers()

        # Parse arguments
        args = parse_arguments()

        # Apply settings from arguments
        settings.max_workers = args.workers
        settings.max_file_size = args.max_size
        settings.default_compression = args.compress
        settings.compression_level = args.compression_level

        if args.hidden:
            settings.show_hidden_files = True
            settings.show_hidden_directories = True
        elif args.no_hidden:
            settings.show_hidden_files = False
            settings.show_hidden_directories = False

        # Apply optimization preset
        if args.optimize:
            apply_optimization_preset(args.optimize)

        # Handle utility commands
        if args.config:
            show_config()
            return 0

        if args.benchmark:
            benchmark_scanning(args.benchmark, args.verbose)
            return 0

        # Handle direct scan
        if args.scan:
            return run_command_line_scan(args)

        # Interactive mode
        print("🔍 File Scanner Pro - Phase 1")
        print("Enhanced with threading, compression, and better UI")
        print("Press Ctrl+C to exit at any time")
        print()

        if args.verbose:
            show_config()
            print("\nStarting interactive mode...")
            print()

        # Start interactive UI
        ui = TerminalUI()
        curses.wrapper(ui.draw)

        return 0

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        return 130
    except Exception as e:
        # Ensure curses exits cleanly
        try:
            curses.endwin()
        except:
            pass

        print(f"💥 Fatal error: {str(e)}")
        if args.verbose if 'args' in locals() else False:
            import traceback
            traceback.print_exc()
        return 1
    finally:
        # Save any configuration changes
        try:
            save_user_config()
        except:
            pass

if __name__ == "__main__":
    sys.exit(main())
