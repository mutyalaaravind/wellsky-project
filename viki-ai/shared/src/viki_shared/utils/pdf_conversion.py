"""
PDF Conversion Utility

This module provides utilities for converting common image formats to PDF.
Useful for standardizing document formats before processing.
"""

import io
from typing import BinaryIO, List, Optional, Union
from pathlib import Path
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class PDFConversionError(Exception):
    """Base exception for PDF conversion operations."""
    pass


class UnsupportedImageFormat(PDFConversionError):
    """Raised when an unsupported image format is provided."""
    pass


class PDFConverter:
    """
    Utility class for converting images to PDF format.
    
    Supports common image formats: JPEG, PNG, TIFF, BMP, GIF, WEBP
    """
    
    SUPPORTED_FORMATS = {
        'JPEG', 'JPG', 'PNG', 'TIFF', 'TIF', 'BMP', 'GIF', 'WEBP'
    }
    
    def __init__(self, quality: int = 95, optimize: bool = True):
        """
        Initialize the PDF converter.
        
        Args:
            quality: JPEG quality for compression (1-100, default: 95)
            optimize: Whether to optimize the PDF size (default: True)
        """
        self.quality = max(1, min(100, quality))
        self.optimize = optimize
        logger.info(f"PDF Converter initialized with quality={self.quality}, optimize={self.optimize}")

    def is_supported_format(self, file_path_or_format: Union[str, Path]) -> bool:
        """
        Check if the image format is supported.
        
        Args:
            file_path_or_format: File path or format string (e.g., 'JPEG', 'PNG')
            
        Returns:
            bool: True if format is supported
        """
        if isinstance(file_path_or_format, Path):
            # Extract extension from Path object
            format_str = file_path_or_format.suffix.lstrip('.').upper()
        elif isinstance(file_path_or_format, str):
            # Check if it's a file path (contains . or /) or just a format string
            if '.' in file_path_or_format or '/' in file_path_or_format or '\\' in file_path_or_format:
                # It's a file path
                path = Path(file_path_or_format)
                format_str = path.suffix.lstrip('.').upper()
            else:
                # It's already a format string
                format_str = file_path_or_format.upper()
        else:
            format_str = str(file_path_or_format).upper()
        
        # Handle common variations
        if format_str == 'JPG':
            format_str = 'JPEG'
        elif format_str == 'TIF':
            format_str = 'TIFF'
            
        return format_str in self.SUPPORTED_FORMATS

    def convert_image_to_pdf(
        self, 
        image_data: BinaryIO, 
        output_stream: Optional[BinaryIO] = None,
        original_filename: Optional[str] = None
    ) -> BinaryIO:
        """
        Convert a single image to PDF format.
        
        Args:
            image_data: Input image data as binary stream
            output_stream: Optional output stream. If None, creates a new BytesIO
            original_filename: Original filename for format detection
            
        Returns:
            BinaryIO: PDF data as binary stream
            
        Raises:
            UnsupportedImageFormat: If image format is not supported
            PDFConversionError: If conversion fails
        """
        try:
            # Reset stream position
            image_data.seek(0)
            
            # Open image with PIL
            with Image.open(image_data) as img:
                # Detect format
                image_format = img.format
                if not image_format and original_filename:
                    # Try to detect from filename
                    path = Path(original_filename)
                    extension = path.suffix.lstrip('.').upper()
                    image_format = 'JPEG' if extension == 'JPG' else extension
                
                if not self.is_supported_format(image_format or ''):
                    raise UnsupportedImageFormat(
                        f"Unsupported image format: {image_format}. "
                        f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
                    )
                
                logger.info(f"Converting {image_format} image to PDF (size: {img.size})")
                
                # Convert image to RGB if necessary (required for PDF)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparent images
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Create output stream if not provided
                if output_stream is None:
                    output_stream = io.BytesIO()
                
                # Save as PDF
                img.save(
                    output_stream,
                    format='PDF',
                    quality=self.quality,
                    optimize=self.optimize,
                    resolution=300.0  # 300 DPI for good quality
                )
                
                # Reset stream position for reading
                output_stream.seek(0)
                
                logger.info("Successfully converted image to PDF")
                return output_stream
                
        except UnsupportedImageFormat:
            raise
        except Exception as e:
            logger.error(f"Failed to convert image to PDF: {str(e)}")
            raise PDFConversionError(f"Image to PDF conversion failed: {str(e)}") from e

    def convert_multiple_images_to_pdf(
        self,
        image_streams: List[BinaryIO],
        output_stream: Optional[BinaryIO] = None,
        filenames: Optional[List[str]] = None
    ) -> BinaryIO:
        """
        Convert multiple images into a single multi-page PDF.
        
        Args:
            image_streams: List of image data streams
            output_stream: Optional output stream. If None, creates a new BytesIO
            filenames: Optional list of original filenames for format detection
            
        Returns:
            BinaryIO: Multi-page PDF data as binary stream
            
        Raises:
            UnsupportedImageFormat: If any image format is not supported
            PDFConversionError: If conversion fails
        """
        if not image_streams:
            raise PDFConversionError("No image streams provided")
        
        try:
            images = []
            filenames = filenames or [None] * len(image_streams)
            
            # Process each image
            for i, (image_data, filename) in enumerate(zip(image_streams, filenames)):
                image_data.seek(0)
                
                with Image.open(image_data) as img:
                    # Detect format
                    image_format = img.format
                    if not image_format and filename:
                        path = Path(filename)
                        extension = path.suffix.lstrip('.').upper()
                        image_format = 'JPEG' if extension == 'JPG' else extension
                    
                    if not self.is_supported_format(image_format or ''):
                        raise UnsupportedImageFormat(
                            f"Unsupported image format in image {i+1}: {image_format}"
                        )
                    
                    logger.info(f"Processing image {i+1}/{len(image_streams)}: {image_format} (size: {img.size})")
                    
                    # Convert to RGB if necessary
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Store the processed image
                    images.append(img.copy())
            
            # Create output stream if not provided
            if output_stream is None:
                output_stream = io.BytesIO()
            
            # Save all images as a multi-page PDF
            if len(images) == 1:
                images[0].save(
                    output_stream,
                    format='PDF',
                    quality=self.quality,
                    optimize=self.optimize,
                    resolution=300.0
                )
            else:
                images[0].save(
                    output_stream,
                    format='PDF',
                    save_all=True,
                    append_images=images[1:],
                    quality=self.quality,
                    optimize=self.optimize,
                    resolution=300.0
                )
            
            # Reset stream position for reading
            output_stream.seek(0)
            
            logger.info(f"Successfully converted {len(images)} images to multi-page PDF")
            return output_stream
            
        except UnsupportedImageFormat:
            raise
        except Exception as e:
            logger.error(f"Failed to convert multiple images to PDF: {str(e)}")
            raise PDFConversionError(f"Multiple images to PDF conversion failed: {str(e)}") from e

    @classmethod
    def quick_convert(
        cls,
        image_data: BinaryIO,
        original_filename: Optional[str] = None,
        quality: int = 95
    ) -> BinaryIO:
        """
        Quick conversion method for single images with default settings.
        
        Args:
            image_data: Input image data as binary stream
            original_filename: Original filename for format detection
            quality: JPEG quality (1-100, default: 95)
            
        Returns:
            BinaryIO: PDF data as binary stream
        """
        converter = cls(quality=quality)
        return converter.convert_image_to_pdf(image_data, original_filename=original_filename)

    def get_image_info(self, image_data: BinaryIO) -> dict:
        """
        Get information about an image without converting it.
        
        Args:
            image_data: Input image data as binary stream
            
        Returns:
            dict: Image information including format, size, mode
        """
        try:
            image_data.seek(0)
            with Image.open(image_data) as img:
                return {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height,
                    'is_supported': self.is_supported_format(img.format or ''),
                    'has_transparency': img.mode in ('RGBA', 'LA', 'P') and 'transparency' in img.info
                }
        except Exception as e:
            logger.error(f"Failed to get image info: {str(e)}")
            return {
                'error': str(e),
                'is_supported': False
            }