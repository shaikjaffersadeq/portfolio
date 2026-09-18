import os
import subprocess
import cv2
import torch
from PIL import Image
from facenet_pytorch import MTCNN
import imageio_ffmpeg


class MediaProcessor:
    def __init__(self, device: str = None, face_crop_size: int = 224):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.face_crop_size = face_crop_size
        # Fetches the absolute path of the bundled FFmpeg binary
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        
        # Initialize MTCNN for face detection and alignment
        self.detector = MTCNN(
            image_size=face_crop_size,
            margin=20,
            keep_all=False,
            select_largest=True,
            post_process=False,
            device=self.device
        )

    def extract_audio(self, video_path: str, output_audio_path: str) -> bool:
        """
        Extracts mono audio downsampled to 16kHz PCM WAV using FFmpeg.
        """
        os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)
        command = [
            self.ffmpeg_exe,
            "-y",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            output_audio_path
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0 and os.path.exists(output_audio_path)

    def extract_face_crops(self, video_path: str, output_dir: str, frame_interval: int = 5) -> int:
        """
        Samples video frames at frame_interval, detects the face, 
        and writes cropped 224x224 images.
        """
        os.makedirs(output_dir, exist_ok=True)
        cap = cv2.VideoCapture(video_path)
        frame_idx = 0
        saved_crops = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % frame_interval == 0:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_frame)

                face_tensor = self.detector(pil_img)
                if face_tensor is not None:
                    face_np = face_tensor.permute(1, 2, 0).cpu().numpy().astype("uint8")
                    face_bgr = cv2.cvtColor(face_np, cv2.COLOR_RGB2BGR)

                    crop_filename = os.path.join(output_dir, f"face_frame_{frame_idx:05d}.jpg")
                    cv2.imwrite(crop_filename, face_bgr)
                    saved_crops += 1

            frame_idx += 1

        cap.release()
        return saved_crops