import os
import sys
from pathlib import Path

import click
import dicom2nifti

from go_nifti.src.utils import find_dicom_folders


def validate_root_folder(ctx, param, value):
    if not Path(value).exists():
        raise click.BadParameter(f"Folder {value} does not exist.")
    return Path(value)


def convert(root_folder, mode):
    dicom_folders = find_dicom_folders(root_folder)
    click.echo(f"Found {len(dicom_folders)} DICOM folders.")
    with click.progressbar(dicom_folders, label="Converting DICOM to NIFTI") as bar:
        for folder in bar:
            if mode == 'save_in_folder':
                save_path = folder / 'nifti.nii.gz'
            elif mode == 'save_in_exam_date':
                save_path = folder.with_suffix('.nii.gz')
            elif mode == 'save_in_separate_dir':
                nii_root = root_folder.name + '_as_nifti'
                nii_root_folder = root_folder.parent / nii_root
                nii_root_folder.mkdir(exist_ok=True)
                rel_path = folder.relative_to(root_folder)
                save_path = nii_root_folder / (rel_path.with_suffix('.nii.gz'))
            else:
                raise click.ClickException("Invalid mode.")
            save_path.parent.mkdir(parents=True, exist_ok=True)

            stdout, stderr = sys.stdout, sys.stderr
            with open(os.devnull, 'w') as f:
                sys.stdout = f
                sys.stderr = f
                try:
                    dicom2nifti.dicom_series_to_nifti(folder, save_path)
                except:
                    pass
            sys.stdout = stdout
            sys.stderr = stderr

    click.echo("Transformation completed.")

@click.command()
@click.argument('root_folder', callback=validate_root_folder)
@click.option('--mode', default='save_in_separate_dir', type=click.Choice(['save_in_separate_dir', 'save_in_folder', 'save_in_exam_date']))
def cli(root_folder, mode):
    convert(root_folder=root_folder, mode=mode)

if __name__ == '__main__':
    cli()