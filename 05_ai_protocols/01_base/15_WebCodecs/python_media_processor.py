import av
import numpy as np
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - MEDIA_PROCESSOR - %(levelname)s - %(message)s')

class PythonMediaProcessor:
    """
    Simulates a Python backend that processes or generates media frames/chunks
    that could be used in conjunction with a client application using WebCodecs.
    """

    def __init__(self, width=640, height=480, fps=30):
        self.width = width
        self.height = height
        self.fps = fps
        logging.info(f"Initialized MediaProcessor: {width}x{height} @ {fps}fps")

    def generate_raw_video_frames(self, count=10, format='rgb24'):
        """
        Generates a sequence of raw video frames (as NumPy arrays).
        A browser client could receive these (e.g., over WebTransport or WebSockets)
        and then use WebCodecs VideoEncoder to encode them.

        Args:
            count (int): Number of frames to generate.
            format (str): The pixel format of the generated frames (e.g., 'rgb24', 'yuv420p').

        Yields:
            np.ndarray: A raw video frame.
        """
        logging.info(f"Generating {count} raw video frames with format {format}...")
        for i in range(count):
            # Create a simple synthetic image (e.g., color changing with frame number)
            frame_data = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            # Red channel increases, Green stays mid, Blue decreases
            frame_data[:, :, 0] = min(255, (i * (255 // count)) % 256)  # Red
            frame_data[:, :, 1] = 128  # Green
            frame_data[:, :, 2] = max(0, 255 - (i * (255 // count)) % 256) # Blue
            
            # If a different format like yuv420p is needed by the client's WebCodecs encoder,
            # conversion would be necessary here using PyAV or similar before sending.
            # For this example, we yield RGB24.
            # If format is yuv420p, conversion is more complex and would change array shape.
            if format != 'rgb24':
                 # This is a placeholder. Actual conversion for YUV formats is more involved.
                 # For simplicity, if not rgb24, we just yield a grayscale version.
                 gray_value = (frame_data[:,:,0] * 0.299 + frame_data[:,:,1] * 0.587 + frame_data[:,:,2] * 0.114).astype(np.uint8)
                 # For a true YUV420p, you'd need Y, U, V planes with specific subsampling.
                 # This is a simplification for the example.
                 # We'll just make it a single channel image for demonstration if not rgb24.
                 # A real yuv420p frame from PyAV VideoFrame.to_ndarray(format='yuv420p') would be a flat 1D array.
                 yield np.dstack([gray_value]*3) # Keep it 3-channel for consistent VideoFrame creation later
            else:
                yield frame_data
            logging.debug(f"Generated raw frame {i+1}/{count}")

    def encode_frames_to_file(self, frames_iterable, output_filename="output_pyav.mp4", codec_name='libx264', pix_fmt='yuv420p'):
        """
        Encodes an iterable of raw video frames (NumPy arrays in RGB24 format)
        into a video file using PyAV. This simulates what a server might do if it
        were to save processed frames, or prepare an encoded video for a client.

        Args:
            frames_iterable: An iterable yielding NumPy arrays (H, W, C) in RGB24 format.
            output_filename (str): Name of the output video file.
            codec_name (str): The video codec to use (e.g., 'libx264', 'mpeg4').
            pix_fmt (str): The pixel format required by the encoder (e.g., 'yuv420p').
        """
        logging.info(f"Encoding frames to '{output_filename}' using codec '{codec_name}' and pix_fmt '{pix_fmt}'")
        try:
            container = av.open(output_filename, mode='w')
        except Exception as e:
            logging.error(f"Failed to open output container '{output_filename}': {e}")
            return

        stream = container.add_stream(codec_name, rate=self.fps)
        stream.width = self.width
        stream.height = self.height
        stream.pix_fmt = pix_fmt

        try:
            for i, frame_rgb in enumerate(frames_iterable):
                try:
                    # Convert NumPy array (assumed RGB24) to PyAV VideoFrame
                    video_frame = av.VideoFrame.from_ndarray(frame_rgb, format='rgb24')
                    
                    # Encode the frame
                    for packet in stream.encode(video_frame):
                        container.mux(packet)
                    logging.debug(f"Encoded frame {i}")
                except Exception as e:
                    logging.error(f"Error encoding frame {i}: {e}", exc_info=True)
                    # Continue to next frame if one fails?
            
            # Flush stream
            for packet in stream.encode():
                container.mux(packet)
            logging.info("Stream flushed.")

        except Exception as e:
            logging.error(f"Error during encoding loop: {e}", exc_info=True)
        finally:
            container.close()
            logging.info(f"Output file '{output_filename}' closed.")

    def simulate_receiving_encoded_chunks(self, input_filename="output_pyav.mp4"):
        """
        Simulates a Python backend receiving encoded video chunks (e.g., from a client
        that used WebCodecs VideoEncoder and sent them over the network).
        This function decodes them using PyAV and could, for example, save the frames.

        Args:
            input_filename (str): The video file to treat as a source of encoded chunks.
        """
        if not os.path.exists(input_filename):
            logging.error(f"Input file '{input_filename}' not found for simulating chunk reception.")
            return

        logging.info(f"Simulating reception of encoded chunks from '{input_filename}' and decoding...")
        try:
            container = av.open(input_filename)
            frame_count = 0
            for frame in container.decode(video=0): # Assuming first video stream
                # In a real scenario, `frame` is an `av.VideoFrame` (raw decoded frame).
                # If we received actual EncodedVideoChunk objects, we'd need to adapt.
                # Here, we are just demonstrating decoding from a container.
                logging.info(f"Decoded frame {frame.index} (PTS: {frame.pts}, DTS: {frame.dts}, Keyframe: {frame.key_frame})")
                # For example, save to an image or process further
                # frame.to_image().save(f"decoded_frame_{frame.index:04d}.png")
                frame_count += 1
            logging.info(f"Successfully decoded {frame_count} frames from '{input_filename}'.")
        except Exception as e:
            logging.error(f"Error decoding '{input_filename}': {e}", exc_info=True)


if __name__ == '__main__':
    processor = PythonMediaProcessor(width=320, height=240, fps=15)

    # 1. Generate raw frames (like a Python app might do)
    raw_frames_generator = processor.generate_raw_video_frames(count=45) # 3 seconds of video

    # 2. Encode these raw frames to a file (simulating server-side encoding or prep for client)
    # Make sure the generator is not consumed before this step if needed again.
    # For simplicity, we'll pass the generator directly.
    output_video_file = "generated_video_for_webcodecs.mp4"
    processor.encode_frames_to_file(raw_frames_generator, output_filename=output_video_file, codec_name='libx264')
    logging.info(f"Video '{output_video_file}' created. This could be sent to a client using WebCodecs for decoding.")

    print("-" * 50)

    # 3. Simulate receiving encoded video (e.g., from a client) and decoding it on the server.
    # We use the file we just created as a stand-in for network-received chunks.
    processor.simulate_receiving_encoded_chunks(input_filename=output_video_file)

    # --- Further notes for actual client-server interaction with WebCodecs ---
    # - Raw frames generated by `generate_raw_video_frames` could be serialized and sent
    #   (e.g., via WebSockets or WebTransport) to a browser client.
    # - The browser client would then use `VideoEncoder.encode(videoFrame)`.
    # - Encoded chunks from the client (`EncodedVideoChunk`) would be sent back to the server.
    # - The server (Python) would need a mechanism to reconstruct a decodable stream from these
    #   chunks if it doesn't already have a container format. PyAV can often work with raw
    #   elementary streams if the codec and parameters are known, or one might assemble them into a simple container.
    logging.info("PythonMediaProcessor demo finished.") 