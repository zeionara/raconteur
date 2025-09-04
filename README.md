# Racounteur

An auxiliary tool for simplifying speech generation on arbitrary texts

## Set up enrivonment

Requires at least `7Gb` of disk space. To install the latest package versions use the following command:

```sh
conda create -n raconteur -y
conda activate raconteur
pip install scipy ipython pydub audioop-lts music-tag tqdm num2words requests torch transliterate transformers click pandas python-telegram-bot beautifulsoup4 omegaconf
```

For sticking with the latest tested versions:

```sh
conda create -n raconteur python=3.13 -y
conda activate raconteur
pip install audioop-lts==0.2.2 beautifulsoup4==4.13.5 click==8.2.1 ipython==9.5.0 music-tag==0.4.3 num2words==0.5.14 omegaconf==2.3.0 pandas==2.3.2 pydub==0.25.1 python-telegram-bot==22.3 requests==2.32.5 scipy==1.16.1 torch==2.8.0 tqdm==4.67.1 transformers==4.56.0 transliterate==1.10.2
```

## Usage

### Generate speech from file using salute TTS model

Requires env variable `SALUTE_SPEECH_AUTH` to be set:

```sh
python -m rr say -t oedipus.txt -e salute -d oedipus.salute.mp3 -r -a Bys
```

### Generate speech from plain file using silero TTS model

```sh
python -m rr say -t oedipus.txt -e silero -d oedipus.silero.mp3 -r -a baya
```

### Generate speech from file with 2ch threads using silero TTS model

```sh
python -m rr alternate assets/philosophy.txt
```
