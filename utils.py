import numpy as np
import nibabel as nib

CHIRALITY_CONST = dict(UNKNOWN=0, LEFT=1, RIGHT=2, BILATERAL=3)
LEFT = 'Left-'
RIGHT = 'Right-'

def get_id_to_region_mapping(mapping_file_name, separator=None):
    file = open(mapping_file_name, 'r')
    lines = file.readlines()

    id_to_region = {}
    for line in lines:
        line = line.strip()
        if line.startswith('#') or line == '':
            continue
        if separator:
            parts = line.split(separator)
        else:
            parts = line.split()
        region_id = int(parts[0])
        region = parts[1]
        id_to_region[region_id] = region
    return id_to_region

def check_and_correct_region(should_be_left, region, segment_name_to_number, new_data, chirality,
                             floor_ceiling, scanner_bore):
    if should_be_left:
        expected_prefix = LEFT
        wrong_prefix = RIGHT
    else:
        expected_prefix = RIGHT
        wrong_prefix = LEFT
    if region.startswith(wrong_prefix):
        flipped_region = expected_prefix + region[len(wrong_prefix):]
        flipped_id = segment_name_to_number[flipped_region]
        new_data[chirality][floor_ceiling][scanner_bore] = flipped_id

def correct_chirality(nifti_input_file_path, left_right_mask_nifti_file, nifti_output_file_path, fslLUT):
    free_surfer_label_to_region = get_id_to_region_mapping(fslLUT)
    segment_name_to_number = {v: k for k, v in free_surfer_label_to_region.items()}
    img = nib.load(nifti_input_file_path)
    data = img.get_data()
    left_right_img = nib.load(left_right_mask_nifti_file)
    left_right_data = left_right_img.get_data()

    new_data = data.copy()
    data_shape = img.header.get_data_shape()
    left_right_data_shape = left_right_img.header.get_data_shape()
    width = data_shape[0]
    height = data_shape[1]
    depth = data_shape[2]
    assert \
        width == left_right_data_shape[0] and height == left_right_data_shape[1] and depth == left_right_data_shape[2]
    for i in range(width):
        for j in range(height):
            for k in range(depth):
                voxel = data[i][j][k]
                region = free_surfer_label_to_region[voxel]
                chirality_voxel = int(left_right_data[i][j][k])
                if not (region.startswith(LEFT) or region.startswith(RIGHT)):
                    continue
                if chirality_voxel == 1 or chirality_voxel == 2:
                    check_and_correct_region(
                        chirality_voxel == 1, region, segment_name_to_number, new_data, i, j, k)
    fixed_img = nib.Nifti1Image(new_data, img.affine, img.header)
    nib.save(fixed_img, nifti_output_file_path)

def create_crude_LR_mask(input_aseg, out_crude_mask):
    img = nib.load(input_aseg)
    data = img.get_fdata()
    affine = img.affine
    
    # Determine the midpoint of X-axis and make new image 
    midpoint_x = data.shape[0] // 2
    modified_data = np.zeros_like(data)
    
    # Assign value 1 to left-side voxels with values greater than 0 value 2 to right-side voxels with values greater than 0
    modified_data[:midpoint_x, :, :][data[:midpoint_x, :, :] > 0] = 1
    modified_data[midpoint_x:, :, :][data[midpoint_x:, :, :] > 0] = 2

    save_nifti(modified_data, affine, out_crude_mask)

    return out_crude_mask

def save_nifti(data, affine, file_path):
    img = nib.Nifti1Image(data, affine)
    nib.save(img, file_path)