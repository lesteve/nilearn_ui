import os.path as osp
from numpy import (ogrid, zeros, conj)

import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt

from report import prepare_report_directory
from report import report_api as api


def mandelbrot(h, w, maxit=20):
    """Returns an image of the Mandelbrot fractal of size (h,w).
    """
    y, x = ogrid[-1.4:1.4:h*1j, -2:0.8:w * 1j]
    c = x + y * 1j
    z = c
    divtime = maxit + zeros(z.shape, dtype=int)

    for i in xrange(maxit):
        z = z**2 + c
        diverge = z*conj(z) > 2**2            # who is diverging
        div_now = diverge & (divtime == maxit)  # who is diverging now
        divtime[div_now] = i                  # note when
        z[diverge] = 2  # avoid diverging too much

    return divtime


def generate_report(params_dict, img_src_filenames):
    report = api.Report()

    report.add(api.Section('Model parameters'),
               api.Table(params_dict.items(),
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


def run_mandelbrot(params):
    """Mandelbrot

    Call mandelbrot function to display mandebrot fractal

    Parameters
    ----------

    height: (100) image height

    width: (100) image width

    itmin: (20) minimum iteratiion

    itmax: (22) maximum iteration

    output_dir: (folder) ouput folder


    Notes
    -----

    This not a nilearn function.
    **Only for nilearn_ui docmentation**

    """
    h = params['height']
    w = params['width']
    itmin = params['itmin']
    itmax = params['itmax']
    output_dir = params['output_dir']
    prepare_report_directory(output_dir)
    images = []
    for it in xrange(itmin, itmax):
        plt.imshow(mandelbrot(h, w, it))
        image_name = osp.join(output_dir, 'mandelbrot%s.png' % it)
        images.append(image_name)
        plt.savefig(image_name)
    report = generate_report(params, images)
    reportindex = osp.abspath(osp.join(output_dir, 'index.html'))
    report.save_html(reportindex)
    return ('file', 'file://{}'.format(reportindex))
