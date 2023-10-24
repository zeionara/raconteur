# Racounteur

An auxiliary tool for simplifying speech generation on arbitrary texts

## Usage

### Generate speech for any text

To generate speech for an arbitrary text, use the following command:

```sh
python -m rr say 'Привет, мир'
```

Example of command for **generating an audio book from a txt file**:

```sh
python -m rr say -e silero -a baya -grx -b 10000 -t assets/player-one.txt
```

By default [RuTTS toolkit][1] is used, but you can specify other model using `-e` (`--engine`) cli argument:

```sh
python -m rr say 'Привет, мир' -e bark
```

Currently the following engines are supported:

1. [rutts][1] - an economical model only for russian texts;
1. [bark][3] - multilingual model, requires a lot of gpu;
1. [salute][4] - adapter to the cloud service from sber, requires environment variable `SALUTE_SPEECH_AUTH` to be set;
1. [crt][5] - adapter to the cloud service from crt, requires environment variables `CRT_USERNAME`, `CRT_PASSWORD`, `CRT_DOMAIN` to be set;
1. [coqui][6] - multilingual `xtts` model, utilizes a moderate amount of gpu (much less than [bark][3], but works better), works very slowly (270.43189 seconds per anek in average on gtx 1650 vs 3-5 seconds for rutts), **requires file `assets/female.wav`** which can be downloaded from [here][6] and replaced with desired speaker's voice recording).
1. [silero][8] - amazing models for speech generation, which produce audio with good quality in a reasonable amount of time without requiring a lot of resources.

For a full list of available cli options see [`__main__.py`][2].

### Convert anecdotes to voice

The app natively supports one specific use-case: it allows to synthesize speech for anecdotes from [this kaggle dataset](https://www.kaggle.com/datasets/zeionara/anecdotes?select=anecdotes.tsv). The command is similar to the examples listed above, to use `rutts` model for reading aloud the first 10 anecdotes you can just type:

```sh
python -m rr handle-aneks -n 10
```

Also you can use another model and specify input / output paths:

```sh
python -m rr handle-aneks -e bark -s 'assets/anecdotes.tsv' -d 'assets/anecdotes' -n 10
```

For a full list of available cli options see [`__main__.py`][2].

Also, see the [exemplary jupyter notebook](./example.ipynb) which is regularly updated.

## Installation

To create a `conda` environment with required dependencies run the following command:

```sh
conda env create -f environment.yml
```

Install the following dependencies manually:

```sh
sudo apt-get install libportaudio2
```

Also you need to clone [`unofficial mail ru cloud api package`][7] for being able to seamlessly upload generated files to mail ru cloud:

```sh
pushd "/home/$USER"
git clone git@github.com:zeionara/carma.git
popd
ln -s "/home/$USER/carma/cloud_mail_api"
```

## Testing

To run tests use the following statement:

```sh
python -m unittest discover test
```

[1]: https://github.com/Tera2Space/RUTTS
[2]: https://github.com/zeionara/raconteur/blob/master/rr/__main__.py
[3]: https://github.com/suno-ai/bark
[4]: https://developers.sber.ru/portal/products/smartspeech
[5]: https://cloud.speechpro.com/home
[6]: https://huggingface.co/spaces/coqui/xtts
[7]: https://github.com/zeionara/carma
[8]: https://github.com/snakers4/silero-models
