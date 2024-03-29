import os.path
import shutil
import platform

from PIL import Image
from yolov5.detect import run

def count_tentacles_actual(img):
    # Find image type: could be .jpg, .png, etc.
    img_type = img[-4:]
    resized_image_name = 'resized' + img_type

    # Clear out old results (old exp folder)
    parent_folder = os.getcwd()
    if platform.system() == 'Windows':
        path = parent_folder + '\\runs'
    else:
        path = parent_folder + '/runs'

    if (os.path.isdir(path)):
        shutil.rmtree(path)

    # Resize image to 640 x 640 (or it won't count properly)
    resized_img = Image.open(img).resize((640, 640))
    resized_img.save(resized_image_name)

    if platform.system() == 'Windows':
        model = parent_folder + '\\coral_model.pt'
    else:
        model = parent_folder + '/coral_model.pt'

    # Run the model
    run(
        weights=model, 
        data = 'Coral-Tentacle-Detection-1/data.yaml',
        source=resized_image_name,
        imgsz=(640, 640),
        conf_thres=0.3,
        save_txt=True,
        hide_labels=True
    )

    # Return filename of image in main folder (to be deleted later)
    if platform.system() == 'Windows':
        main_location = os.getcwd() + '\\' + resized_image_name
    else:
        main_location = os.getcwd() + '/' + resized_image_name
    
    return main_location


def get_coordinates():
    if platform.system() == 'Windows':
        filename = os.getcwd() + '\\runs\detect\exp\labels\\resized.txt'
    else:
        filename = os.getcwd() + '/runs/detect/exp/labels/resized.txt'
    
    if not os.path.exists(filename):
        return None
    else:
        file = open(filename, 'r')
        file_lines = file.readlines()
        large_array = []

        for line in file_lines:
            array = line.split(' ')
            new_array = []

            new_array.append(float(array[1]))   # x_center of bounding box
            new_array.append(float(array[2]))   # y_center of bounding box
            
            large_array.append(new_array)

        file.close()
        return large_array