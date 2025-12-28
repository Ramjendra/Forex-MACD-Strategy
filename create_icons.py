#!/usr/bin/env python3
"""
Create favicon and optimized logo from BiasBuster logo
"""

from PIL import Image
import os

# Paths
logo_path = "biasbuster_logo.jpg"
favicon_path = "favicon.ico"
icon_192 = "biasbuster_icon_192.png"
icon_512 = "biasbuster_icon_512.png"

print("📸 Creating favicon and icons from BiasBuster logo...")

# Load the logo
img = Image.open(logo_path)

# Create favicon (32x32)
favicon = img.resize((32, 32), Image.Resampling.LANCZOS)
favicon.save(favicon_path, format='ICO')
print(f"✅ Created favicon: {favicon_path}")

# Create 192x192 icon for mobile
icon192 = img.resize((192, 192), Image.Resampling.LANCZOS)
icon192.save(icon_192, format='PNG', optimize=True)
print(f"✅ Created 192x192 icon: {icon_192}")

# Create 512x512 icon for mobile
icon512 = img.resize((512, 512), Image.Resampling.LANCZOS)
icon512.save(icon_512, format='PNG', optimize=True)
print(f"✅ Created 512x512 icon: {icon_512}")

print("\n🎉 All icons created successfully!")
