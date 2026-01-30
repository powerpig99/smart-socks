#!/usr/bin/env python3
"""
Smart Socks - Create Demo Video from Recorded Frames
ELEC-E7840 Smart Wearables (Aalto University)

Converts recorded PNG frames from calibration_visualizer.py into a video file.

Usage:
    # Create video from frames (auto-detects frame sequence)
    python create_demo_video.py --input demo_recording_20260130_120000_frame_*.png --output demo.mp4
    
    # Specify frame rate (default: 20 fps)
    python create_demo_video.py --input frames/*.png --output demo.mp4 --fps 20
    
    # Create from directory containing frames
    python create_demo_video.py --input ./recording_session/ --output demo.mp4

Requirements:
    pip install imageio imageio-ffmpeg
    
    Or use ffmpeg directly:
    ffmpeg -framerate 20 -i demo_frame_%05d.png -c:v libx264 -pix_fmt yuv420p demo.mp4
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime


def create_video_from_frames(input_pattern, output_file, fps=20):
    """Create video from PNG frames using imageio."""
    try:
        import imageio
        import imageio_ffmpeg
    except ImportError:
        print("ERROR: imageio and imageio-ffmpeg required.")
        print("Install with: pip install imageio imageio-ffmpeg")
        print("\nAlternatively, use ffmpeg directly:")
        print(f"  ffmpeg -framerate {fps} -i {input_pattern} -c:v libx264 -pix_fmt yuv420p {output_file}")
        return False
    
    # Find all matching frames
    input_path = Path(input_pattern)
    if '*' in input_pattern:
        # Glob pattern
        frames = sorted(Path('.').glob(input_pattern))
    elif input_path.is_dir():
        # Directory - find all PNG files
        frames = sorted(input_path.glob('*.png'))
    else:
        # Single file or pattern
        frames = [input_path]
    
    if not frames:
        print(f"ERROR: No frames found matching: {input_pattern}")
        return False
    
    print(f"Found {len(frames)} frames")
    print(f"Creating video: {output_file}")
    print(f"Frame rate: {fps} fps")
    print(f"Duration: {len(frames) / fps:.1f} seconds")
    
    # Read first frame to get dimensions
    first_frame = imageio.imread(frames[0])
    height, width = first_frame.shape[:2]
    print(f"Resolution: {width}x{height}")
    
    # Create video writer
    writer = imageio.get_writer(output_file, fps=fps, quality=8)
    
    # Write frames
    for i, frame_path in enumerate(frames):
        if i % 50 == 0:
            print(f"  Processing frame {i+1}/{len(frames)}...")
        frame = imageio.imread(frame_path)
        writer.append_data(frame)
    
    writer.close()
    print(f"\n✓ Video saved: {output_file}")
    print(f"  Frames: {len(frames)}")
    print(f"  Duration: {len(frames) / fps:.1f}s")
    print(f"  Size: {Path(output_file).stat().st_size / 1024 / 1024:.1f} MB")
    
    return True


def create_ffmpeg_command(input_pattern, output_file, fps=20):
    """Print ffmpeg command for creating video."""
    cmd = f"ffmpeg -framerate {fps} -i '{input_pattern}' -c:v libx264 -pix_fmt yuv420p -crf 23 '{output_file}'"
    print("FFmpeg command:")
    print(cmd)
    print("\nRun this command to create the video using ffmpeg (if installed).")
    return cmd


def main():
    parser = argparse.ArgumentParser(
        description='Create demo video from recorded frames',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # From frame sequence
    python create_demo_video.py --input "demo_*_frame_*.png" --output demo.mp4
    
    # From directory
    python create_demo_video.py --input ./my_recording/ --output demo.mp4
    
    # Custom frame rate
    python create_demo_video.py --input frames/*.png --output demo.mp4 --fps 30
        """
    )
    
    parser.add_argument('--input', '-i', required=True,
                        help='Input frames (glob pattern, directory, or file)')
    parser.add_argument('--output', '-o', required=True,
                        help='Output video file (e.g., demo.mp4)')
    parser.add_argument('--fps', type=int, default=20,
                        help='Frame rate (default: 20)')
    parser.add_argument('--ffmpeg-only', action='store_true',
                        help='Only print ffmpeg command, do not create video')
    
    args = parser.parse_args()
    
    if args.ffmpeg_only:
        create_ffmpeg_command(args.input, args.output, args.fps)
        return 0
    
    success = create_video_from_frames(args.input, args.output, args.fps)
    
    if not success:
        # Fall back to ffmpeg command
        print("\n" + "="*60)
        print("Falling back to ffmpeg command:")
        print("="*60)
        create_ffmpeg_command(args.input, args.output, args.fps)
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
