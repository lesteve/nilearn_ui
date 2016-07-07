import os
import os.path as osp
import json
import shutil

from report import prepare_report_directory
from report import report_api as api

import nibabel

from nilearn import datasets
from nilearn.plotting import plot_stat_map, plot_glass_brain
from nilearn.decomposition.canica import CanICA


def get_fitted_canica(func_files, **params):
    input_folder = params.pop('input_folder')
    func_files = sorted(os.path.join(root, filename)
                        for root, dirs, filenames in os.walk(input_folder)
                        for filename in filenames
                        if filename.endswith('.nii.gz'))

    canica = CanICA(memory='nilearn_cache', memory_level=5, random_state=0,
                    n_jobs=-1, **params)

    if not func_files:
        raise ValueError('Could not find any files in the input folder')
    canica.fit(func_files)
    return canica


def generate_images(components_img, n_components, images_dir, glass=False):
    # Remove existing images
    if os.path.exists(images_dir):
        shutil.rmtree(images_dir)
    os.makedirs(images_dir)
    output_filenames = [osp.join(images_dir, 'IC_{}.png'.format(i))
                        for i in range(n_components)]

    for i, output_file in enumerate(output_filenames):
        plot_stat_map(nibabel.Nifti1Image(components_img.get_data()[..., i],
                                          components_img.get_affine()),
                      display_mode="z", title="IC %d" % i, cut_coords=7,
                      colorbar=False, output_file=output_file)
    if glass:
        output_filenames = [osp.join(images_dir, 'glass_IC_{}.png'.format(i))
                            for i in range(n_components)]
        for i, output_file in enumerate(output_filenames):
            plot_glass_brain(nibabel.Nifti1Image(
                components_img.get_data()[..., i],
                components_img.get_affine()),
                display_mode="ortho", title="IC %d" % i,
                             output_file=output_file)


def generate_report(params_dict, img_src_filenames):
    report = api.Report()

    report.add(api.Section('Model parameters'),
               api.Table(params_dict.iteritems(),
                         headers=('Parameter', 'Value')))

    for counter, filename in enumerate(img_src_filenames):
        caption = 'component {}'.format(counter)
        section = api.Section('Component #{}'.format(counter))
        section.add(
            api.Image(filename, caption=caption)
            )
        report.add(section)
    report.add(api.Section('About').add(
        api.Paragraph(
            'This report has been generated using the nilearn toolkit.')))
    report.add(api.Section('Contact').add(
        api.Paragraph(
            'See <a href="https://github.com/nilearn/nilearn/"'
            '>https://github.com/nilearn/nilearn/</a>')))

    return report


def run(func_files, params, output_dir):
    canica = get_fitted_canica(func_files, **params)
    # Retrieve the independent components in brain space
    components_img = canica.masker_.inverse_transform(canica.components_)
    generate_images(components_img, params['n_components'],
                    osp.join(output_dir, 'images'),
                    glass=True)
    json.dump(params, open(osp.join(output_dir, 'params.json'), 'w'))


def run_canica(params):
    """CanICA

    Perform Canonical Independent Component Analysis.

    Parameters
    ----------

    n_components: (20) number of components

    smoothing_fwhm: (6.) smoothing fwhm

    threshold: (3.) specify threshold

    verbose: (['10', '0', '10']) select verbosity level

    input_folder: (folder) select input folder

    output_folder: (folder) define ouput folder

    References
    ----------
    * G. Varoquaux et al. "A group model for stable multi-subject ICA on
      fMRI datasets", NeuroImage Vol 51 (2010), p. 288-299

    * G. Varoquaux et al. "ICA-based sparse features recovery from fMRI
      datasets", IEEE ISBI 2010, p. 1177
    """
    dataset = datasets.fetch_adhd()
    func_files = dataset.func
    output_dir = osp.abspath(params.pop('output_folder'))
    prepare_report_directory(output_dir)
    run(func_files, params, output_dir)
    json.dump(params, open(osp.join(output_dir, 'params.json'), 'w'))
    img_src_filenames = [osp.join(output_dir, 'images', fname) for fname in
                         os.listdir(osp.join(output_dir, 'images'))
                         if fname.startswith('IC_')]
    report = generate_report(params, img_src_filenames)
    reportindex = osp.abspath(osp.join(output_dir, 'index.html'))
    report.save_html(reportindex)
    return ('file', 'file://{}'.format(reportindex))
