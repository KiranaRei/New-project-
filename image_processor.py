from PIL import Image, ImageDraw, ImageFont, ImageFilter
import aiohttp
import io
import os

class ImageProcessor:
    def __init__(self):
        self.default_font_size = 50
        self.username_font_size = 60
        self.server_font_size = 40
        self.member_count_font_size = 30

    async def create_welcome_image(self, username, server_name, avatar_url, bg_image_url=None, member_count=None):
        """Create a welcome image with user avatar and text"""
        try:
            # Create base image
            if bg_image_url:
                background = await self._download_image(bg_image_url)
                if background:
                    background = background.resize((800, 400), Image.Resampling.LANCZOS)
                else:
                    background = self._create_default_background()
            else:
                background = self._create_default_background()
            
            # Create a copy to work with
            img = background.copy()
            draw = ImageDraw.Draw(img)
            
            # Add semi-transparent overlay for better text readability
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 100))
            img = Image.alpha_composite(img.convert('RGBA'), overlay)
            draw = ImageDraw.Draw(img)
            
            # Download and process avatar
            avatar = await self._download_image(avatar_url)
            if avatar:
                avatar = self._create_circular_avatar(avatar, 120)
                # Paste avatar in the center-left area
                avatar_x = 100
                avatar_y = (img.height - avatar.height) // 2
                img.paste(avatar, (avatar_x, avatar_y), avatar)
            
            # Add text
            text_x = 250
            text_start_y = 120
            
            # Welcome text
            try:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", self.username_font_size)
                font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", self.server_font_size)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", self.member_count_font_size)
            except:
                # Fallback to default font
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Draw username
            draw.text((text_x, text_start_y), f"Welcome", font=font_medium, fill=(255, 255, 255))
            draw.text((text_x, text_start_y + 50), username, font=font_large, fill=(255, 255, 255))
            
            # Draw server name
            draw.text((text_x, text_start_y + 120), f"to {server_name}", font=font_medium, fill=(200, 200, 200))
            
            # Draw member count if provided
            if member_count:
                draw.text((text_x, text_start_y + 170), f"Member #{member_count}", font=font_small, fill=(150, 150, 150))
            
            # Convert to bytes
            img_buffer = io.BytesIO()
            img.convert('RGB').save(img_buffer, format='PNG', quality=95)
            img_buffer.seek(0)
            
            return img_buffer
            
        except Exception as e:
            print(f"Error creating welcome image: {e}")
            return None

    def _create_default_background(self):
        """Create a default gradient background"""
        img = Image.new('RGB', (800, 400), color=(54, 57, 63))
        draw = ImageDraw.Draw(img)
        
        # Create a simple gradient
        for y in range(img.height):
            color_value = int(54 + (y / img.height) * 30)
            draw.line([(0, y), (img.width, y)], fill=(color_value, color_value + 3, color_value + 6))
        
        return img

    def _create_circular_avatar(self, avatar_img, size):
        """Create a circular avatar with border"""
        avatar_img = avatar_img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Create circular mask
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        
        # Apply mask to avatar
        output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        output.paste(avatar_img, (0, 0))
        output.putalpha(mask)
        
        # Add border
        border_size = 4
        border_img = Image.new('RGBA', (size + border_size * 2, size + border_size * 2), (0, 0, 0, 0))
        border_draw = ImageDraw.Draw(border_img)
        border_draw.ellipse((0, 0, size + border_size * 2, size + border_size * 2), outline=(255, 255, 255, 255), width=border_size)
        
        # Paste avatar onto border
        border_img.paste(output, (border_size, border_size), output)
        
        return border_img

    async def _download_image(self, url):
        """Download an image from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        return Image.open(io.BytesIO(image_data))
            return None
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None
