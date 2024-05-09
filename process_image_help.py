import os

from PIL import Image

import my_utils


def process_image(input_path, output_path):
    # Open the image
    img = Image.open(input_path)

    # Convert the image to RGBA mode (if not already in RGBA mode)
    img = img.convert("RGBA")

    # Get the image data as a list of tuples
    image_data = list(img.getdata())

    # Process each pixel
    processed_data = []
    for pixel in image_data:
        # Check if the pixel is not black
        if pixel[:3] != (0, 0, 0):
            # Set alpha to 100%
            processed_data.append((255, 255, 255, 0))
        else:
            # Leave black pixels unchanged
            processed_data.append(pixel)

    # Update the image data with the modified pixels
    img.putdata(processed_data)

    # Save the modified image
    img.save(output_path)

def process_image_outside_map_to_black(input_path, output_path):
    # Open the image
    img = Image.open(input_path)

    # Convert the image to RGBA mode (if not already in RGBA mode)
    img = img.convert("RGBA")

    # Get the image data as a list of tuples
    image_data = list(img.getdata())

    # Process each pixel
    processed_data = []
    for pixel in image_data:
        if pixel[:3] == (122, 127, 124):
            # Set alpha to 100%
            processed_data.append((255, 255, 255, 0))
        elif pixel[:3] != (0, 0, 0):
            processed_data.append((0, 0, 255, 255))
        else:
            # Leave black pixels unchanged
            processed_data.append((0, 0, 0, 255))

    # Update the image data with the modified pixels
    img.putdata(processed_data)

    # Save the modified image
    img.save(output_path)


def process_image_non_transparent_to_mask(input_path, output_path):
    # Open the image
    img = Image.open(input_path)

    # Convert the image to RGBA mode (if not already in RGBA mode)
    img = img.convert("RGBA")

    # Get the image data as a list of tuples
    image_data = list(img.getdata())
    mask_col = my_utils.mask_color()
    # Process each pixel
    processed_data = []
    for pixel in image_data:
        if pixel[3] != 0:
            processed_data.append(mask_col)
        else:
            processed_data.append((255, 255, 255, 0))

    # Update the image data with the modified pixels
    img.putdata(processed_data)

    # Save the modified image
    img.save(output_path)

# Example usage:
def make_my_masks():
    input_path_dir = "./textures/pwr_map/map_collision_masks"
    output_path_dir = "./textures/pwr_map/map_collision_masks2"

    names = os.listdir(input_path_dir)

    for name in names:
        process_image_non_transparent_to_mask(os.path.join(input_path_dir, name), os.path.join(output_path_dir, name))


if __name__ == '__main__':
    make_my_masks()
