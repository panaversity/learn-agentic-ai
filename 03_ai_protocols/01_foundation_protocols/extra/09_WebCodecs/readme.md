# WebCodecs: Low-Level Media Encoding and Decoding in the Browser

WebCodecs is a modern web API that provides **low-level access to built-in (often hardware-accelerated) media encoders and decoders** directly within web applications. It allows for fine-grained control over the processing of audio and video, enabling high-performance, real-time media manipulation without relying on bulky JavaScript libraries or WebAssembly for codecs.

Unlike higher-level APIs like HTML `<video>` or the MediaStream API (which are about playing or capturing media), WebCodecs is about direct interaction with the raw compressed or uncompressed media data. It empowers developers to build sophisticated applications like in-browser video editors, custom streaming clients, and real-time video effects.

---

## Core WebCodecs API Concepts (Browser-Side)

WebCodecs operates on the client-side (in the browser) and includes the following key components:

1.  **Encoders and Decoders**:

    - `VideoEncoder`: Encodes raw video frames (`VideoFrame` objects) into compressed chunks (`EncodedVideoChunk`).
    - `VideoDecoder`: Decodes compressed video chunks (`EncodedVideoChunk`) back into raw video frames (`VideoFrame`).
    - `AudioEncoder`: Encodes raw audio data (`AudioData` objects) into compressed chunks (`EncodedAudioChunk`).
    - `AudioDecoder`: Decodes compressed audio chunks (`EncodedAudioChunk`) back into raw audio data (`AudioData`).

2.  **Configuration Objects**:

    - Each encoder/decoder is configured with an object specifying the codec (e.g., `'vp8'`, `'avc1.42E01E'`, `'opus'`), dimensions, bitrate, framerate, latency mode, etc.
    - `VideoEncoder.isConfigSupported()` and `VideoDecoder.isConfigSupported()` allow checking if a configuration is likely to work before attempting to create the codec instance.

3.  **Data Objects**:

    - `VideoFrame`: Represents an uncompressed frame of video. Can be created from sources like `<canvas>`, `HTMLVideoElement`, `ImageBitmap`, or raw pixel data in an `ArrayBuffer`.
    - `AudioData`: Represents a block of uncompressed audio samples. Can be created from raw PCM data in an `ArrayBuffer`.
    - `EncodedVideoChunk`: Represents a chunk of compressed video data, along with its type (e.g., key frame, delta frame) and timestamp.
    - `EncodedAudioChunk`: Represents a chunk of compressed audio data.

4.  **Callback-Based Processing**:

    - Encoders and decoders operate asynchronously. You provide an `output` callback to receive encoded chunks (from encoders) or decoded frames/audio (from decoders).
    - An `error` callback is used for handling errors during processing.

5.  **Codec Support**: WebCodecs itself doesn't define which codecs must be supported; this depends on the browser and underlying operating system. Common codecs like H.264 (AVC), VP8, VP9, AV1 for video, and Opus, AAC for audio are often available.

6.  **Composability**: WebCodecs is designed to work with other web APIs:
    - **MediaStreamTrack API**: Get raw frames from a camera/microphone to feed into an encoder.
    - **WebRTC**: `RTCPeerConnection` can be configured to provide encoded frames that can be decoded with `VideoDecoder` (and vice-versa for sending), allowing for custom processing pipelines.
    - **WebTransport/WebSockets**: Send encoded chunks produced by `VideoEncoder` over the network, or receive chunks to feed into `VideoDecoder`.
    - **WebGL/WebGPU**: Render decoded frames or use canvas content as input for encoders.

---

## Python for Server-Side Media Processing (Interfacing with WebCodecs Clients)

WebCodecs is a **browser API**. There isn't a direct Python library that _is_ WebCodecs. However, Python is extensively used on the server-side to process, generate, or store media that WebCodecs-enabled clients might interact with.

Libraries like **PyAV** (FFmpeg bindings) allow Python applications to perform sophisticated audio/video encoding, decoding, and manipulation.

### Installation for Python (PyAV)

```bash
# Using pip
pip install av numpy

# Or using uv
# uv pip install av numpy
```

### Example: Python Backend Media Processor (`python_media_processor.py`)

This Python script demonstrates how a server-side application using `PyAV` could:

1.  Generate raw video frames (e.g., from a simulation, AI model output, or procedural generation). These frames could be sent to a browser client, which would then use `VideoEncoder` (from WebCodecs) to compress them before transmission or display.
2.  Encode these raw frames into a standard video file (e.g., MP4 with H.264). This encoded file could be served to clients for playback or as a source for WebCodecs decoding.
3.  Simulate receiving encoded video (as if from a client that used `VideoEncoder`) and decode it using `PyAV` for further server-side processing or storage.

**File:** `15_WebCodecs/python_media_processor.py`

```python
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
```

**To run this Python script:**

1. Save the code as `15_WebCodecs/python_media_processor.py`.
2. Install dependencies: `pip install av numpy` (or `uv pip install ...`).
3. Run from your terminal: `python 15_WebCodecs/python_media_processor.py`.
   This will generate a sample video file and then simulate decoding it.

---

## Strengths of WebCodecs (Browser API)

- **Fine-Grained Control**: Offers precise, low-level control over the encoding and decoding process, frame by frame or chunk by chunk.
- **Performance**: Leverages browser-internal, often hardware-accelerated codecs, leading to better performance and lower CPU usage compared to JavaScript or WebAssembly-based codecs.
- **Reduced Bundle Size**: No need to ship large codec libraries (like a JS H.264 decoder) to the client.
- **Flexibility**: Can handle a wide range of use cases, from simple decoding for display to complex processing pipelines (e.g., real-time effects, transcoding snippets).
- **Supports Various Frame Sources/Sinks**: Can work with `HTMLCanvasElement`, `HTMLVideoElement`, `ImageBitmap`, `OffscreenCanvas`, and raw `ArrayBuffer` data.
- **Complements Other Media APIs**: Designed to integrate smoothly with MediaStreamTrack, WebRTC, WebAudio, and WebAssembly.

## Weaknesses and Considerations (WebCodecs)

- **Low-Level API**: More complex to use than higher-level APIs like `<video>`. Requires understanding of media concepts (frames, chunks, timestamps, codec configurations).
- **Browser-Specific**: It's a browser API, so it's primarily for client-side JavaScript. Server-side processing requires different tools (like PyAV in Python).
- **Codec Availability**: Relies on codecs built into the browser/OS. While common ones are usually available, specific or newer codecs might not be universally supported.
- **No Container Handling**: WebCodecs deals with raw frames and encoded chunks. It does not handle media container formats (like MP4, MKV). Demuxing/muxing container formats must be done separately (e.g., using JavaScript libraries like `mp4box.js` or on the server).
- **Still Evolving**: While widely supported in modern browsers, some aspects or specific codec parameters might have subtle differences or ongoing standardization.

## Common Use Cases for WebCodecs (Browser-Side)

- **In-Browser Video/Audio Editing**: Non-linear editing, trimming, effects application.
- **Custom Real-Time Communication Clients**: Building specialized video/audio conferencing clients with custom processing or rendering, often alongside WebRTC for transport.
- **Cloud Gaming/Remote Desktop Clients**: Efficiently decoding video streams from a server.
- **Live Streaming Applications**: Encoding camera input for sending to a server, or decoding streams from a server for low-latency playback.
- **Media Analysis and Effects**: Applying real-time filters, object detection, or other AI-driven modifications to video frames in the browser.
- **Integration with WebAssembly**: Using WebAssembly for complex media algorithms and interfacing with WebCodecs for hardware-accelerated I/O.
- **Transcoding or Re-encoding Snippets**: For example, preparing a short clip from a longer video for sharing, directly in the browser.

## WebCodecs in DACA and A2A Communication

WebCodecs primarily impacts the **client-side** aspects of DACA, especially when agents have browser-based user interfaces or when agents interact with browser-based applications that perform media processing. It's less about direct Agent-to-Agent (A2A) communication protocol and more about how agents _handle media data at the edges_.

**Relevance to DACA:**

1.  **Efficient Client-Side Media Processing for Agent UIs**: If a DACA agent exposes a web UI (e.g., built with Next.js, Streamlit) that needs to display or manipulate video/audio, WebCodecs can be used in that UI for:

    - **Decoding**: Efficiently decoding video/audio streams sent from a backend DACA agent (e.g., a Python agent using PyAV to serve encoded data over WebTransport or WebSockets).
    - **Encoding**: Capturing user media (camera, microphone via `getUserMedia`), encoding it with WebCodecs, and then sending the encoded chunks to a backend DACA agent for processing, storage, or forwarding.

2.  **Interfacing Python Backend Agents with WebCodecs Clients**: A Python DACA agent (server-side) would not use the WebCodecs API directly. Instead, it would:

    - **Serve Media**: Generate or retrieve media (raw frames or encoded chunks) and send it to the browser client via a suitable transport protocol (WebRTC, WebTransport, WebSockets).
    - **Receive Media**: Accept encoded chunks from a browser client (that used `VideoEncoder`) and then use libraries like `PyAV` to decode, process, or store these chunks.
      The `python_media_processor.py` example illustrates this server-side role.

3.  **Enabling Advanced Multi-Modal Interactions**: For DACA systems where agents interact with users through rich media, WebCodecs allows the browser to handle more of the media processing load, potentially reducing server costs and latency. For instance, an agent guiding a user through a physical task via video might receive a camera feed encoded by the user's browser using WebCodecs.

4.  **Composability with Transport Protocols**: WebCodecs is transport-agnostic. The encoded chunks it produces/consumes can be sent/received over any A2A communication channel DACA might employ, such as:
    - **WebTransport**: Ideal for sending streams of `EncodedVideoChunk` or `EncodedAudioChunk`, leveraging WebTransport's multiple streams and datagram capabilities.
    - **WebSockets**: Can also be used to transfer these chunks.
    - **WebRTC Data Channels**: For P2P transfer of encoded media chunks between a browser client and another peer (which could be a Python agent using `aiortc`).

**Considerations for DACA:**

- **Focus on the Edge**: WebCodecs is most relevant where DACA agents interact with browser environments. For pure backend A2A communication (Python-to-Python), direct use of libraries like `PyAV` or GStreamer would be more common for media processing.
- **Payload Negotiation**: If a DACA agent serves media to a WebCodecs client, they need to agree on codecs, formats, and how encoded chunks are framed/transmitted over the chosen transport.

**Conclusion for DACA:**
WebCodecs empowers the browser-based components of a DACA system to handle media processing with high performance and fine-grained control. While Python agents on the backend use libraries like PyAV, they can be designed to seamlessly produce or consume media streams compatible with WebCodecs-powered clients, enabling sophisticated real-time multi-modal agentic applications.

---

## Place in the Protocol Stack

- **Layer**: Application Layer (API within the browser for media processing).
- **Relationship**: It is an API that provides access to codecs. It is not a protocol itself but interacts with data that might be transported by protocols like WebRTC, WebTransport, or WebSockets.
- **Environment**: Primarily JavaScript in web browsers.

---

## Further Reading

- [WebCodecs API (MDN Web Docs)](https://developer.mozilla.org/en-US/docs/Web/API/WebCodecs_API) (The primary resource for the WebCodecs API)
- [WebCodecs Explainer (W3C)](https://www.w3.org/TR/webcodecs-codec-registry/) (Detailed specification and use cases)
- [Samples for WebCodecs (GitHub)](https://github.com/GoogleChromeLabs/webcodecs-samples) (Practical examples from Google Chrome Labs)
- [PyAV Documentation](https://pyav.org/docs/stable/) (For Python-based server-side media processing)
