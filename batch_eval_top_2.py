from cv2 import imread, imwrite
import numpy as np
from os.path import join, exists
from os import mkdir, listdir
from PIL import Image

def create_patch_batch_list(input_img,
                            batch_size,
                            num_channels=3,
                            patch_size=32,
                            vertical_stride=16,
                            horizontal_stride=16):
    input_batch_list = []
    gt_annotation_batch_list = []
    coordinate_batch_list = []
    global_patch_index = 0

    height = input_img.shape[0]
    width = input_img.shape[1]

    num_vertical_points = int((height - patch_size) / vertical_stride) + 1
    num_horizontial_points = int((width - patch_size) / horizontal_stride) + 1
    for i in range(num_vertical_points):
        for j in range(num_horizontial_points):
            local_patch_index = global_patch_index % batch_size
            if local_patch_index == 0:
                current_input_batch = np.zeros((batch_size, patch_size, patch_size, num_channels))
                current_gt_annotation_batch = np.array([None] * batch_size)
                current_coordinate_batch = [(None, None)] * batch_size
            current_coordinate_batch[local_patch_index] = (i * vertical_stride, j * horizontal_stride)
            current_input_batch[local_patch_index, :, :, :] = input_img[current_coordinate_batch[local_patch_index][0]:current_coordinate_batch[local_patch_index][0] + patch_size,
                                                              current_coordinate_batch[local_patch_index][1]:current_coordinate_batch[local_patch_index][1] + patch_size,:]

            if local_patch_index == batch_size - 1:
                input_batch_list.append(current_input_batch)
                gt_annotation_batch_list.append(current_gt_annotation_batch)
                coordinate_batch_list.append(current_coordinate_batch)
            global_patch_index += 1
    for i in range(num_vertical_points):
        local_patch_index = global_patch_index % batch_size
        if local_patch_index == 0:
            current_input_batch = np.zeros((batch_size, patch_size, patch_size, num_channels))
            current_gt_annotation_batch = np.array([None] * batch_size)
            current_coordinate_batch = [(None, None)] * batch_size
        current_coordinate_batch[local_patch_index] = (i * vertical_stride, width - patch_size)
        current_input_batch[local_patch_index, :, :, :] = input_img[current_coordinate_batch[local_patch_index][0]:current_coordinate_batch[local_patch_index][0] + patch_size,
                                                           current_coordinate_batch[local_patch_index][1]:current_coordinate_batch[local_patch_index][1] + patch_size,:]
        if local_patch_index == batch_size - 1:
            input_batch_list.append(current_input_batch)
            gt_annotation_batch_list.append(current_gt_annotation_batch)
            coordinate_batch_list.append(current_coordinate_batch)
        global_patch_index += 1
    for i in range(num_horizontial_points):
        local_patch_index = global_patch_index % batch_size
        if local_patch_index == 0:
            current_input_batch = np.zeros((batch_size, patch_size, patch_size, num_channels))
            current_gt_annotation_batch = np.array([None] * batch_size)
            current_coordinate_batch = [(None, None)] * batch_size
        current_coordinate_batch[local_patch_index] = (height - patch_size, i * horizontal_stride)
        current_input_batch[local_patch_index, :, :, :] = input_img[current_coordinate_batch[local_patch_index][0]:current_coordinate_batch[local_patch_index][0] + patch_size,
                                                           current_coordinate_batch[local_patch_index][1]:current_coordinate_batch[local_patch_index][1] + patch_size,:]
        if local_patch_index == batch_size - 1:
            input_batch_list.append(current_input_batch)
            gt_annotation_batch_list.append(current_gt_annotation_batch)
            coordinate_batch_list.append(current_coordinate_batch)
        global_patch_index += 1
    local_patch_index = global_patch_index % batch_size
    if local_patch_index == 0:
        current_input_batch = np.zeros((batch_size, patch_size, patch_size, num_channels))
        current_gt_annotation_batch = np.array([None] * batch_size)
        current_coordinate_batch = [(None, None)] * batch_size
    current_coordinate_batch[local_patch_index] = (height - patch_size, width - patch_size)
    current_input_batch[local_patch_index, :, :, :] = input_img[current_coordinate_batch[local_patch_index][0]:current_coordinate_batch[local_patch_index][0] + patch_size,
                                                       current_coordinate_batch[local_patch_index][1]:current_coordinate_batch[local_patch_index][1] + patch_size,:]
    if local_patch_index == batch_size - 1:
        input_batch_list.append(current_input_batch)
        gt_annotation_batch_list.append(current_gt_annotation_batch)
        coordinate_batch_list.append(current_coordinate_batch)
    global_patch_index += 1
    local_patch_index = global_patch_index % batch_size
    if local_patch_index != 0:
        for i in range(batch_size - local_patch_index):
            local_patch_index = global_patch_index % batch_size
            current_coordinate_batch[local_patch_index] = (height - patch_size, width - patch_size)
            current_input_batch[local_patch_index, :, :, :] = input_img[current_coordinate_batch[local_patch_index][0]:current_coordinate_batch[local_patch_index][0] + patch_size,
                                                               current_coordinate_batch[local_patch_index][1]:current_coordinate_batch[local_patch_index][1] + patch_size,:]
            if local_patch_index == batch_size - 1:
                input_batch_list.append(current_input_batch)
                gt_annotation_batch_list.append(current_gt_annotation_batch)
                coordinate_batch_list.append(current_coordinate_batch)
            global_patch_index += 1
    return input_batch_list, coordinate_batch_list, height, width

def batch_inference(input_tensor,
                    logits,
                    keep_probability,
                    encoding_keep_prob,
                    sess,
                    is_training,
                    input_batch_list,
                    coordinate_batch_list,
                    height,
                    width,
                    patch_size=32):
    logits_map = np.zeros((height, width, 2), dtype=np.float32)
    for i in range(len(input_batch_list)):
        if encoding_keep_prob == None:
            logits_batch = sess.run(logits, feed_dict={input_tensor: input_batch_list[i], keep_probability: 1.0, is_training: False})
        else:
            logits_batch = sess.run(logits, feed_dict={input_tensor: input_batch_list[i], keep_probability: 1.0, is_training: False, encoding_keep_prob: 1.0})
        for j in range(logits_batch.shape[0]):
            logits_map[coordinate_batch_list[i][j][0]:coordinate_batch_list[i][j][0] + patch_size,
                       coordinate_batch_list[i][j][1]:coordinate_batch_list[i][j][1] + patch_size, :] += logits_batch[j]
    return np.argmax(logits_map, axis=2)

def batch_logits_map_inference(input_tensor,
                               logits,
                               keep_probability,
                               sess,
                               is_training,
                               input_batch_list,
                               coordinate_batch_list,
                               height,
                               width,
                               encoding_keep_prob=None,
                               patch_size=32):
    logits_map = np.zeros((height, width, 2), dtype=np.float32)
    for i in range(len(input_batch_list)):
        if encoding_keep_prob == None:
            logits_batch = sess.run(logits, feed_dict={input_tensor: input_batch_list[i], keep_probability: 1.0, is_training: False})
        else:
            logits_batch = sess.run(logits, feed_dict={input_tensor: input_batch_list[i], keep_probability: 1.0, is_training: False, encoding_keep_prob: 1.0})
        for j in range(logits_batch.shape[0]):
            logits_map[coordinate_batch_list[i][j][0]:coordinate_batch_list[i][j][0] + patch_size,
                       coordinate_batch_list[i][j][1]:coordinate_batch_list[i][j][1] + patch_size, :] += logits_batch[j]
    return logits_map

def eval_dir(input_tensor,
             logits,
             keep_probability,
             sess, is_training,
             batch_size,
             log_dir,
             epoch_num,
             encoding_keep_prob=None,
             num_channels=3,
             patch_size=32,
             vertical_stride=16,
             horizontal_stride=16,
             is_validation=True):
    files = listdir("../FCN_OCR_dataset/annotations")
    if is_validation:
        filename = files[:int(len(files) * 0.8)]
        acc_logfile = 'epoch_val_acc.csv'
    else:
        filename = files[int(len(files) * 0.8):]
        acc_logfile = 'epoch_train_acc.csv'
    num_matches = 0
    num_pixels = 0
    for fn in filename:
        input_batch_list, coordinate_batch_list, height, width = create_patch_batch_list(fn, batch_size, num_channels=num_channels)
        pred_annotation_map = batch_inference(input_tensor, logits, keep_probability, encoding_keep_prob, sess, is_training, input_batch_list, coordinate_batch_list, height, width)
        num_matches += np.sum(pred_annotation_map == imread("../FCN_OCR_dataset/annotations/" + fn, -1))
        num_pixels += pred_annotation_map.shape[0] * pred_annotation_map.shape[1]
    with open(join(log_dir, acc_logfile), 'a') as f:
        f.write(str(epoch_num) + ',' + str(num_matches / num_pixels) + '\n')

def get_patches(image_name, patch_size=32, vertical_stride=16, horizontal_stride=16):
    input_img = imread("../FCN_OCR_dataset/top/" + image_name + ".png")
    annotation_img = imread("../FCN_OCR_dataset/annotations/" + image_name, -1)
    height = np.shape(input_img)[0]
    width = np.shape(input_img)[1]
    number_of_vertical_points = (height - patch_size) // vertical_stride + 1
    number_of_horizontial_points = (width - patch_size) // horizontal_stride + 1
    input_patch = []
    gt_patch = []
    coordinate = []
    num_patches = 0
    for i in range(number_of_vertical_points):
        for j in range(number_of_horizontial_points):
            current_coodinate = (i * vertical_stride, j * horizontal_stride)
            current_input_patch = input_img[current_coodinate[0]:current_coodinate[0] + patch_size,
                                            current_coodinate[1]:current_coodinate[1] + patch_size,:]
            current_gt_patch = annotation_img[current_coodinate[0]:current_coodinate[0] + patch_size,
                                              current_coodinate[1]:current_coodinate[1] + patch_size]
            coordinate.append(current_coodinate)
            gt_patch.append(current_gt_patch)
            input_patch.append(current_input_patch)
            num_patches += 1
    for i in range(number_of_vertical_points):
        current_coodinate = (i * vertical_stride, width - patch_size)
        current_input_patch = input_img[current_coodinate[0]:current_coodinate[0] + patch_size,
                                        current_coodinate[1]:current_coodinate[1] + patch_size,:]
        current_gt_patch = annotation_img[current_coodinate[0]:current_coodinate[0] + patch_size,
                                          current_coodinate[1]:current_coodinate[1] + patch_size]
        coordinate.append(current_coodinate)
        gt_patch.append(current_gt_patch)
        input_patch.append(current_input_patch)
        num_patches += 1
    for i in range(number_of_horizontial_points):
        current_coodinate = (height - patch_size, i * horizontal_stride)
        current_input_patch = input_img[current_coodinate[0]:current_coodinate[0] + patch_size,
                                        current_coodinate[1]:current_coodinate[1] + patch_size,:]
        current_gt_patch = annotation_img[current_coodinate[0]:current_coodinate[0] + patch_size,
                                          current_coodinate[1]:current_coodinate[1] + patch_size]
        coordinate.append(current_coodinate)
        gt_patch.append(current_gt_patch)
        input_patch.append(current_input_patch)
        num_patches += 1
    current_coodinate = (height - patch_size, width - patch_size)
    current_input_patch = input_img[current_coodinate[0]:current_coodinate[0] + patch_size,
                                    current_coodinate[1]:current_coodinate[1] + patch_size,:]
    current_gt_patch = annotation_img[current_coodinate[0]:current_coodinate[0] + patch_size,
                                        current_coodinate[1]:current_coodinate[1] + patch_size]
    coordinate.append(current_coodinate)
    gt_patch.append(current_gt_patch)
    input_patch.append(current_input_patch)
    num_patches += 1
    return input_patch, gt_patch, coordinate, num_patches

def infer_submission(input_tensor,
             logits,
             keep_probability,
             sess,
             batch_size,
             log_dir,
             is_training,
             encoding_keep_prob=None,
             num_channels=3,
             patch_size=32,
             vertical_stride=16,
             horizontal_stride=16):
    filename = ['top_mosaic_09cm_area2', 'top_mosaic_09cm_area4', 'top_mosaic_09cm_area6',
                'top_mosaic_09cm_area8', 'top_mosaic_09cm_area10', 'top_mosaic_09cm_area12',
                'top_mosaic_09cm_area14', 'top_mosaic_09cm_area16', 'top_mosaic_09cm_area20',
                'top_mosaic_09cm_area22', 'top_mosaic_09cm_area24', 'top_mosaic_09cm_area27',
                'top_mosaic_09cm_area29', 'top_mosaic_09cm_area31', 'top_mosaic_09cm_area33',
                'top_mosaic_09cm_area35', 'top_mosaic_09cm_area38']
    # 2,4,6,8,10,12,14,16,20,22,24,27,29,31,33,35,38
    for fn in filename:
        print(">> Inferring:", fn)
        input_batch_list, coordinate_batch_list, height, width = create_patch_batch_list(fn, batch_size, num_channels=num_channels)
        pred_annotation_map = batch_inference(input_tensor, logits, keep_probability, encoding_keep_prob, sess, is_training, input_batch_list, coordinate_batch_list, height, width)
        height = pred_annotation_map.shape[0]
        width = pred_annotation_map.shape[1]
        output_image = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(height):
            for j in range(width):
                if pred_annotation_map[i,j]==0:
                    output_image[i,j]=np.array([255,255,255])
                elif pred_annotation_map[i,j]==1:
                    output_image[i,j]=np.array([0,0,255])
                elif pred_annotation_map[i,j]==2:
                    output_image[i,j]=np.array([0,255,255])
                elif pred_annotation_map[i,j]==3:
                    output_image[i,j]=np.array([0,255,0])
                elif pred_annotation_map[i,j]==4:
                    output_image[i,j]=np.array([255,255,0])
                elif pred_annotation_map[i,j]==5:
                    output_image[i,j]=np.array([255,0,0])
        # imwrite(log_dir + 'submission/' + image_name + '.png', output_image)
        if not exists(join(log_dir, 'submission_cv2')):
            mkdir(join(log_dir, 'submission_cv2'))
        if not exists(join(log_dir, 'submission_PIL')):
            mkdir(join(log_dir, 'submission_PIL'))
        im = Image.fromarray(output_image)
        b, g, r = im.split()
        im = Image.merge("RGB", (r, g, b))
        im.save(join(log_dir, 'submission_PIL', fn + '.png'))
        imwrite(join(log_dir, 'submission_cv2', fn + '.png'), output_image)

        # imsave(join(log_dir, 'submission', fn + '.png'), output_image)