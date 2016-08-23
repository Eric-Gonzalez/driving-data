import csv

import h5py
import numpy as np
from PIL import Image
from PIL import ImageOps

image_size = 320, 160


# Resize and repackage our images to match the Comma AI format
# number_frames x 3 x 160 x 320
def resize_image(image_path):
    image = Image.open(image_path)
    resized = ImageOps.fit(image, image_size, Image.ANTIALIAS)
    # resized.save('output.jpg')
    array = np.asarray(resized)
    return np.uint8(array.transpose(2, 0, 1))


def create_dataset(h5_set, dataset_name, array):
    np_array = np.stack(array)
    h5_set.create_dataset(dataset_name, np_array.shape, "<f8", np_array)


if __name__ == '__main__':
    camera_set = h5py.File("dataset/camera/data2.h5", "w")
    log_set = h5py.File("dataset/log/data2.h5", "w")
    image_arrays = []
    gas_array = []
    speed_array = []
    steering_angle_array = []
    brake_array = []
    cam1_ptr_array = []  # Index of Frame
    times_array = []

    current_time = 0
    with open('driving_log.csv', 'rb') as driving_csv:
        reader = csv.reader(driving_csv)
        for row in reader:
            array = resize_image(row[0])
            image_arrays.append(array)

            steering_angle_array.append(float(row[1]))
            gas_array.append(float(row[2]))
            brake_array.append(float(row[3]))
            speed_array.append(float(row[4]))

            cam1_ptr_array.append(float(reader.line_num - 1))
            times_array.append(float(current_time))
            current_time += 0.2
            print "Processed: " + row.__str__()
    stacked_array = np.stack(image_arrays)
    camera_set.create_dataset("X", stacked_array.shape, "uint8", stacked_array)

    create_dataset(log_set, "steering_angle", steering_angle_array)
    create_dataset(log_set, "gas", gas_array)
    create_dataset(log_set, "brake", brake_array)
    create_dataset(log_set, "speed", speed_array)
    create_dataset(log_set, "cam1_ptr", cam1_ptr_array)
    create_dataset(log_set, "times", times_array)
    print "Reshaping Complete: " + stacked_array.shape.__str__()
