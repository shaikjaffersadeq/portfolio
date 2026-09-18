import os
import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms


class GradCAMExplainer:
    def __init__(self, model, target_layer=None):
        self.model = model
        self.model.eval()
        self.device = next(model.parameters()).device
        
        # Target the final convolutional block in EfficientNet-B0
        self.target_layer = target_layer or self.model.backbone.features[-1]
        
        self.gradients = None
        self.activations = None
        
        # Register PyTorch hooks for forward activations and backward gradients
        self.target_layer.register_forward_hook(self._save_activation)
        self.target_layer.register_full_backward_hook(self._save_gradient)

    def _save_activation(self, module, input, output):
        self.activations = output

    def _save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0]

    def generate_heatmap(self, image_path: str, target_class: int = 1) -> np.ndarray:
        """
        Calculates Grad-CAM activation heatmap for the given target class (1 = Fake/Manipulated).
        """
        raw_image = Image.open(image_path).convert("RGB")
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        tensor = transform(raw_image).unsqueeze(0).to(self.device)
        tensor.requires_grad = True

        # Forward pass
        logits = self.model.backbone(tensor)
        
        # Backward pass on the manipulation class score
        self.model.zero_grad()
        score = logits[0, target_class]
        score.backward()

        # Global Average Pooling of gradients
        pooled_gradients = torch.mean(self.gradients, dim=[0, 2, 3])
        activations = self.activations[0]

        # Weight activation channels by gradients
        for i in range(activations.shape[0]):
            activations[i, :, :] *= pooled_gradients[i]

        heatmap = torch.mean(activations, dim=0).squeeze().detach().cpu()
        heatmap = F.relu(heatmap)
        
        # Normalize between 0 and 1
        if torch.max(heatmap) > 0:
            heatmap /= torch.max(heatmap)
        
        heatmap_np = heatmap.numpy()

        # Resize heatmap back to image dimensions and overlay
        orig_img_cv = cv2.imread(image_path)
        h, w, _ = orig_img_cv.shape
        heatmap_resized = cv2.resize(heatmap_np, (w, h))
        heatmap_uint8 = np.uint8(255 * heatmap_resized)

        # Apply JET colormap (red = manipulated region, blue = authentic)
        colormap = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
        cam_overlay = cv2.addWeighted(orig_img_cv, 0.6, colormap, 0.4, 0)

        return cam_overlay

    def generate_batch_heatmaps(self, faces_dir: str, output_dir: str, max_frames: int = 5):
        """
        Processes suspicious facial crops and exports annotated heatmap frames.
        """
        os.makedirs(output_dir, exist_ok=True)
        valid_exts = (".jpg", ".jpeg", ".png")
        image_files = sorted([
            os.path.join(faces_dir, f) for f in os.listdir(faces_dir) 
            if f.lower().endswith(valid_exts)
        ])[:max_frames]

        saved_heatmaps = []
        for img_path in image_files:
            overlay = self.generate_heatmap(img_path, target_class=1)
            filename = "heatmap_" + os.path.basename(img_path)
            save_path = os.path.join(output_dir, filename)
            cv2.imwrite(save_path, overlay)
            saved_heatmaps.append(save_path)

        return saved_heatmaps