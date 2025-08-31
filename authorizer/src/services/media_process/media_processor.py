import hashlib
from io import BytesIO

from eyemath_schemas import ImageProcessResult, ImageProcessMeta  # type: ignore[import-untyped]
from fastapi import HTTPException
from PIL import Image as PILImage
from starlette import status

from src.core.config import ConfigLoader
from src.core.utils import EnvTools


class MediaProcessor:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.max_image_size_bytes: int = int(EnvTools.required_load_env_var("s3_max_image_size_mb")) * 1024 * 1024


    def process_image(self, raw: bytes, content_type: str | None) -> ImageProcessResult:
        self._validate_raw(raw)
        img = self._open_image(raw)
        fmt = self._choose_format(content_type, img.format)
        processed_bytes, mime = self._encode_without_exif(img, fmt)
        meta = self._build_meta(processed_bytes, img, fmt, mime)

        return ImageProcessResult(
            data=processed_bytes,
            meta=meta
        )


    def _validate_raw(self, raw: bytes) -> None:
        if not raw:
            raise HTTPException(status_code=400, detail="Empty file")
        if len(raw) > self.max_image_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Image too large",
            )


    def _open_image(self, raw: bytes) -> PILImage.Image:
        try:
            img = PILImage.open(BytesIO(raw))
            img.load()
            return img
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image: {e}")


    def _choose_format(self, content_type: str | None, orig_fmt: str | None) -> str:
        """
        Returns the final encoding format: 'JPEG' or the original one.
        JPEG is the default, if nothing is clear.
        """
        if content_type:
            ct = content_type.lower()
            if ct.endswith("jpeg") or ct.endswith("jpg"):
                return "JPEG"
            if ct.endswith("png"):
                return "PNG"
            if ct.endswith("webp"):
                return "WEBP"
        if orig_fmt:
            return orig_fmt.upper()

        return "JPEG"


    def _encode_without_exif(self, img: PILImage.Image, fmt: str) -> tuple[bytes, str]:
        """
        Saving without EXIF. For JPEG → RGB, optimization.
        Returns (bytes, mime).
        """
        buf = BytesIO()
        f = fmt.upper()
        if f == "JPEG":
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            img.save(buf, format="JPEG", optimize=True, quality=90)
            return buf.getvalue(), "image/jpeg"
        else:
            img.save(buf, format=f)
            return buf.getvalue(), f"image/{f.lower()}"


    def _build_meta(self, processed: bytes, img: PILImage.Image, fmt: str, mime: str) -> ImageProcessMeta:
        width, height = img.size
        colorspace = img.mode
        checksum = hashlib.sha256(processed).hexdigest()

        return ImageProcessMeta(
            mime=mime,
            size=len(processed),
            width=width,
            height=height,
            exif_stripped=True,
            colorspace=colorspace,
            format=fmt.upper(),
            checksum_sha256=checksum,
        )
