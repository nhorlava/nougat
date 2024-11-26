<div align="center">
<h1>Nougat: Neural Optical Understanding for Academic Documents</h1>

[![Paper](https://img.shields.io/badge/Paper-arxiv.2308.13418-white)](https://arxiv.org/abs/2308.13418)
[![GitHub](https://img.shields.io/github/license/facebookresearch/nougat)](https://github.com/facebookresearch/nougat)
[![PyPI](https://img.shields.io/pypi/v/nougat-ocr?logo=pypi)](https://pypi.org/project/nougat-ocr)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Hugging Face Spaces](https://img.shields.io/badge/🤗%20Hugging%20Face-Community%20Space-blue)](https://huggingface.co/spaces/ysharma/nougat)

</div>

This is the fork of the official repository for Nougat, the academic document PDF parser that understands LaTeX math and tables.
Original project page: https://facebookresearch.github.io/nougat/

<b> This fork is part of a collaborative project I am contributing to as an employee of the Max Planck Computing and Data Facility (MPCDF). The project involves the following organizations: </b>
- Max Planck Computing and Data Facility (MPCDF)
- Max Planck Institute for Research on Collective Goods
  
<b> Key changes: </b>
- for pages were the original "nougat" tool produced "[MISSING_PAGE_*]" error, simpler OCR methods (e.g. `pytesseract` tool)  were used to recognize text.
- additionally, the repo was containerized using "apptainer". The recipe is located at `container/apptainer/nougat.def`

<b> Example of running: </b>
`apptainer exec $path_to_container nougat $path/to/directory -o output_directory --batchsize 1`


## Install

From repository:
```
git clone https://github.com/nhorlava/nougat.git
cd nougat
apptainer build --fakeroot nougat.sif container/apptainer/nougat.def
```


### Get prediction for a PDF
#### CLI

To get predictions for a PDF run

```
$ nougat path/to/file.pdf -o output_directory
```

A path to a directory or to a file where each line is a path to a PDF can also be passed as a positional argument

```
$ nougat path/to/directory -o output_directory
```

```
usage: nougat [-h] [--batchsize BATCHSIZE] [--checkpoint CHECKPOINT] [--model MODEL] [--out OUT]
              [--recompute] [--markdown] [--no-skipping] pdf [pdf ...]

positional arguments:
  pdf                   PDF(s) to process.

options:
  -h, --help            show this help message and exit
  --batchsize BATCHSIZE, -b BATCHSIZE
                        Batch size to use.
  --checkpoint CHECKPOINT, -c CHECKPOINT
                        Path to checkpoint directory.
  --model MODEL_TAG, -m MODEL_TAG
                        Model tag to use.
  --out OUT, -o OUT     Output directory.
  --recompute           Recompute already computed PDF, discarding previous predictions.
  --full-precision      Use float32 instead of bfloat16. Can speed up CPU conversion for some setups.
  --no-markdown         Do not add postprocessing step for markdown compatibility.
  --markdown            Add postprocessing step for markdown compatibility (default).
  --no-skipping         Don't apply failure detection heuristic.
  --pages PAGES, -p PAGES
                        Provide page numbers like '1-4,7' for pages 1 through 4 and page 7. Only works for single PDFs.
```

The default model tag is `0.1.0-small`. If you want to use the base model, use `0.1.0-base`.
```
$ nougat path/to/file.pdf -o output_directory -m 0.1.0-base
```

In the output directory every PDF will be saved as a `.mmd` file, the lightweight markup language, mostly compatible with [Mathpix Markdown](https://github.com/Mathpix/mathpix-markdown-it) (we make use of the LaTeX tables).

> Note: On some devices the failure detection heuristic is not working properly. If you experience a lot of `[MISSING_PAGE]` responses, try to run with the `--no-skipping` flag. Related: [#11](https://github.com/facebookresearch/nougat/issues/11), [#67](https://github.com/facebookresearch/nougat/issues/67)

#### API

With the extra dependencies you use `app.py` to start an API. Call

```sh
$ nougat_api
```

To get a prediction of a PDF file by making a POST request to http://127.0.0.1:8503/predict/. It also accepts parameters `start` and `stop` to limit the computation to select page numbers (boundaries are included).

The response is a string with the markdown text of the document.

```sh
curl -X 'POST' \
  'http://127.0.0.1:8503/predict/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@<PDFFILE.pdf>;type=application/pdf'
```
To use the limit the conversion to pages 1 to 5, use the start/stop parameters in the request URL: http://127.0.0.1:8503/predict/?start=1&stop=5

## FAQ

- Why am I only getting `[MISSING_PAGE]`?

  Nougat was trained on scientific papers found on arXiv and PMC. Is the document you're processing similar to that?
  What language is the document in? Nougat works best with English papers, other Latin-based languages might work. **Chinese, Russian, Japanese etc. will not work**.
  If these requirements are fulfilled it might be because of false positives in the failure detection, when computing on CPU or older GPUs ([#11](https://github.com/facebookresearch/nougat/issues/11)). Try passing the `--no-skipping` flag for now.

- Where can I download the model checkpoint from.

  They are uploaded here on GitHub in the release section. You can also download them during the first execution of the program. Choose the preferred preferred model by passing `--model 0.1.0-{base,small}`

## Citation

```
@misc{blecher2023nougat,
      title={Nougat: Neural Optical Understanding for Academic Documents}, 
      author={Lukas Blecher and Guillem Cucurull and Thomas Scialom and Robert Stojnic},
      year={2023},
      eprint={2308.13418},
      archivePrefix={arXiv},
      primaryClass={cs.LG}
}
```

## Acknowledgments

This repository builds on top of the [Donut](https://github.com/clovaai/donut/) repository.

## License

Nougat codebase is licensed under MIT.

Nougat model weights are licensed under CC-BY-NC.
