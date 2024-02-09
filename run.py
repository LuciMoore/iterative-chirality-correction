import os
import glob
from utils import create_crude_LR_mask
from utils import correct_chirality
import argparse

def main():
    parser = argparse.ArgumentParser(description="iterative chirality correction run outside of BIBSNet")
    parser.add_argument("bibsnet_output_dir", help="Folder that contains subject/session folders containing BIBSNet work dir called work")
    args = parser.parse_args()
    root_dir=args.bibsnet_output_dir

    # Get the directory of run.py in order to find the filepath to the FreeSurfer LUT
    script_dir = os.path.dirname(os.path.realpath(__file__))
    fsl_lut = os.path.join(script_dir, 'FreeSurferColorLUT.txt')

    # Go to the root folder and generate list of sub/ses folders 
    os.chdir(root_dir)
    subses=glob.glob('sub-*/ses-*')
    subses.sort()

    for i in subses:
        sub=i.split('/')[0]
        ses=i.split('/')[1]
        sub_ses=sub+'_'+ses

        #Define file paths/folders
        sub_root=f'{root_dir}/{i}'
        anat_dilated2_wd=f'{sub_root}/anat_dilated2_work'
        anat_dilated2_deriv=f'{sub_root}/anat_dilated2'
        final_deriv_aseg=f'{anat_dilated2_deriv}/{sub_ses}_space-T1w_desc-aseg_dseg.nii.gz'

        if os.path.exists(final_deriv_aseg):
            print(f'{final_deriv_aseg} exists - skipping')
        
        else:
            cc_aseg_postBN=f'{sub_root}/work/postbibsnet/{i}/chirality_correction/corrected_{sub_ses}_optimal_resized.nii.gz'
            if not os.path.exists(cc_aseg_postBN):
                print(f'Original corrected aseg postbibsnet workdir missing: {cc_aseg_postBN}')
            
            else:
                print(f'Performing iterative chirality correction on {i}')
                
                # Make derivatives dir to save final corrected T1w-space aseg out to and work dir to save intermediate output files 
                if not os.path.exists(anat_dilated2_deriv):
                    os.mkdir(anat_dilated2_deriv) 
                if not os.path.exists(anat_dilated2_wd):
                    os.mkdir(anat_dilated2_wd)

                # Split the chirality corrected acpc aseg image from postbibsnet into left and right to create a crude chirality correction mask 
                crude_mask=f'{anat_dilated2_wd}/crude_mask.nii.gz'
                create_crude_LR_mask(cc_aseg_postBN, crude_mask)

                # Iteration 1: Perform chirality correction on the chirality corrected aseg image from postbibsnet using the crude LR mask
                crude_corrected_aseg=f'{anat_dilated2_wd}/crude_corr_aseg.nii.gz'
                correct_chirality(cc_aseg_postBN, crude_mask, crude_corrected_aseg, fsl_lut)

                # Iteration 2: Perform chirality correction on the crudely corrected aseg using the original dilated LR mask
                orig_dil_LRmask=f'{sub_root}/work/postbibsnet/{i}/lrmask_dil_wd/LRmask_dil.nii.gz'
                cc_aseg_iteration2=f'{anat_dilated2_wd}/cc_aseg_acpc.nii.gz'
                correct_chirality(crude_corrected_aseg, orig_dil_LRmask, cc_aseg_iteration2, fsl_lut)

                # Transform final corrected aseg into native T1w space 
                ref_img=f'{sub_root}/work/prebibsnet/{i}/averaged/{sub_ses}_0000.nii.gz'
                init=f'{sub_root}/work/postbibsnet/{i}/chirality_correction/seg_reg_to_T1w_native.mat'

                cmd=f'flirt -applyxfm -ref {ref_img} -in {cc_aseg_iteration2} -init {init} -o {final_deriv_aseg} -interp nearestneighbour'
                os.system(cmd)

if __name__ == "__main__":
    main()
