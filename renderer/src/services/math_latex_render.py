import asyncio
import base64
from io import BytesIO
import os

import matplotlib.pyplot as plt

from src.core.config import ConfigLoader
from src.core.utils import FileSystemTools


class LatexRenderTool:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.save_render_img = self.config.get("latex_render", "save_render_img")
        self.rendered_img_dir = self.config.get("latex_render", "rendered_img_dir")

# TODO: Render an image and encode it to base64 format to return for client.
# TODO: Also, add some additional preferences to endpoint, like custom resolution render, effects on pictore from PIL...

    def clear_saved_renders(self, dir: str) -> None:
        FileSystemTools.delete_directory(dir)


    async def save_image_localy(self, jpg_bytes: bytes) -> None:
        '''
        saves image localy in rendered images directory.
        '''
        if not self.save_render_img:
            return
        
        FileSystemTools.ensure_directory_exists(self.rendered_img_dir)
        filename = f"image{FileSystemTools.count_files_in_dir(self.rendered_img_dir)}.jpg"
        file_path = os.path.join(self.rendered_img_dir, filename)
        FileSystemTools.save_file(file_path, jpg_bytes)


    def convert_jpg_to_base64(self, jpg_bytes: bytes) -> str:
        '''
        converts jpg image from bytes to string of base64 format.
        '''
        base64_encoded = base64.b64encode(jpg_bytes).decode('utf-8')
        return f"data:image::{base64_encoded}"


    def render_latex_jpg(self, latex_expression: str, dpi: int) -> bytes:
        '''
        renders an image in with jpg format and returns it bytes.
        '''
        fig = plt.figure(figsize=(0.1, 0.1), dpi=dpi)
        plt.text(0.5, 0.5, f"${latex_expression}$",
                 fontsize=12,
                 ha='center',
                 va='center')
        plt.axis('off')
        
        buf = BytesIO()
        plt.savefig(buf, format='jpg',
                    bbox_inches='tight',
                    pad_inches=0.05,
                    transparent=False,
                    dpi=dpi)
        plt.close(fig)
        
        buf.seek(0)
        return buf.getvalue()


    def render_latex_jpg_base64(self, latex_expression: str, dpi: int) -> str:
        jpg_bytes = self.render_latex_jpg(latex_expression, dpi)
        asyncio.run(self.save_image_localy(jpg_bytes))
        return self.convert_jpg_to_base64(jpg_bytes)
    
