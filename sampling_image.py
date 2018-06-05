import numpy as np
from cv2 import imread, imwrite
from os.path import exists, join, splitext
from os import listdir, mkdir

training_dir = "../FCN_OCR_dataset/training"
validation_dir = "../FCN_OCR_dataset/validation"
gt_dir = "../FCN_OCR_dataset/ground_truth"

input_img_dir = "../FCN_OCR_dataset/input_img"
annotation_dir = "../FCN_OCR_dataset/annotations"

CROP_SIZE = 32
validation_image = ["841289701567_01267729233_023245368_1_2015122120241757.png"]

def create_training_dataset():
    if not exists(training_dir):
        mkdir(training_dir)
    if not exists(gt_dir):
        mkdir(gt_dir)
    for filename in listdir(annotation_dir):
        if filename in validation_image:
            continue
        input_image = imread(join(input_img_dir, filename))
        annotation_image = imread(join(annotation_dir, filename), -1)
        width = np.shape(input_image)[1]
        height = np.shape(input_image)[0]
        print(height, width)        
        i = 0
        for x in range(height - CROP_SIZE + 1):
            for y in range(width - CROP_SIZE + 1):
                print((x, y))
                i += 1
                input_image_cropped = input_image[x:x + CROP_SIZE, y:y + CROP_SIZE, :]
                imwrite(join(training_dir, splitext(filename)[0] + "_" + str(i) + ".png"), input_image_cropped)
                annotation_image_cropped = annotation_image[x:x + CROP_SIZE, y:y + CROP_SIZE]
                imwrite(join(gt_dir,splitext(filename)[0] + "_" + str(i) + ".png"), annotation_image_cropped)
    return None


def create_validation_dataset():
    if not exists(validation_dir):
        mkdir(validation_dir)
    for filename in validation_image:
        input_image = imread(join(input_img_dir, filename))
        annotation_image = imread(join(annotation_dir, filename), -1)
        width = np.shape(input_image)[1]
        height = np.shape(input_image)[0]
        print(height, width)
        i = 0
        for x in range(height - CROP_SIZE + 1):
            for y in range(width - CROP_SIZE + 1):
                print((x, y))
                i += 1
                input_image_cropped = input_image[x:x + CROP_SIZE, y:y + CROP_SIZE, :]
                imwrite(join(validation_dir, splitext(filename)[0] + "_" + str(i) + ".png"), input_image_cropped)
                annotation_image_cropped = annotation_image[x:x + CROP_SIZE, y:y + CROP_SIZE]
                imwrite(join(gt_dir,splitext(filename)[0] + "_" + str(i) + ".png"), annotation_image_cropped)
    return None

if __name__=="__main__":
    np.random.seed(3796)
    create_training_dataset()
    create_validation_dataset()