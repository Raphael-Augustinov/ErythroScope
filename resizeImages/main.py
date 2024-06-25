import os
from PIL import Image, ExifTags

Image.MAX_IMAGE_PIXELS = None

# Define the source and destination directories
source_dir = "C:/Users/rapha/OneDrive - Universitatea Politehnica Timisoara/Projects/Erythroscope - Anemia Detection/demo_images2/normal"
destination_dir = "C:/Users/rapha/OneDrive - Universitatea Politehnica Timisoara/Projects/Erythroscope - Anemia Detection/demo_images/normal"
# 13586 13647 14528 18518 14408 12926 18482
original_width, original_height = 4000, 3000

# Calculate the cropping box
left = 1300
top = 1015
right = left + 1200
bottom = top + 1200
crop_box = (left, top, right, bottom)
print(f'Cropping box: {crop_box}')

def correct_orientation(img):
    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation] == 'Orientation':
            break

    exif = img._getexif()
    if exif is not None:
        orientation_value = exif.get(orientation)
        if orientation_value == 3:
            img = img.rotate(180, expand=True)
        elif orientation_value == 6:
            img = img.rotate(270, expand=True)
        elif orientation_value == 8:
            img = img.rotate(90, expand=True)
    return img

# List all files in the source directory
for filename in os.listdir(source_dir):
    # Construct the full file path
    file_path = os.path.join(source_dir, filename)
    try:
        # Open the image
        with Image.open(file_path) as img:
            # Correct the orientation if necessary
            img = correct_orientation(img)
            # Crop the image
            cropped_img = img.crop(crop_box)
            # Construct the destination file path
            dest_file_path = os.path.join(destination_dir, filename)
            # Save the cropped image to the destination directory
            cropped_img.save(dest_file_path)
            print(f'Cropped and saved {filename} to {destination_dir}')
    except Exception as e:
        print(f'Error processing {filename}: {e}')
