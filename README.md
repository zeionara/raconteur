# Racounteur

An auxiliary tool for simplifying speech generation on arbitrary texts

## Set up enrivonment

Requires at least `7Gb` of disk space. To install the latest package versions use the following command:

```sh
conda create -n raconteur -y
conda activate raconteur
pip install scipy ipython pydub audioop-lts music-tag tqdm num2words requests torch transliterate transformers click pandas python-telegram-bot[job-queue] beautifulsoup4 omegaconf sentencepiece flask google-images-search
```

For sticking with the latest tested versions:

```sh
conda create -n raconteur python=3.13 -y
conda activate raconteur
pip install audioop-lts==0.2.2 beautifulsoup4==4.13.5 click==8.2.1 ipython==9.5.0 music-tag==0.4.3 num2words==0.5.14 omegaconf==2.3.0 pandas==2.3.2 pydub==0.25.1 'python-telegram-bot[job-queue]==22.3' requests==2.32.5 scipy==1.16.1 torch==2.8.0 tqdm==4.67.1 transformers==4.56.0 transliterate==1.10.2 sentencepiece==0.2.1 flask==3.1.2 google-images-search==1.4.7
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

### Start telegram bot

Requires env variables `RACONTEUR_BOT_TOKEN`, `MY_CHAT_ID`, `KARMA_USERNAME`, `KARMA_PASSWORD` to be set:

```sh
mkdir -p assets/bot
python -m rr start assets/bot/snapshots -a assets/bot/alternation-list.txt -t assets/bot/audio -c /2ch
```

Then periodically check file `assets/bot/alternation-list.txt` using the following command (requires env variables `MUCH_VK_POST_TOKEN`, `MUCH_VK_POST_OWNER`, `MUCH_VK_POST_ALBUM`, `MUCH_VK_AUDIO_TOKEN`, `MUCH_VK_AUDIO_OWNER`, `RR_GIS_API_KEY`, `RR_GIS_API_KEY_FALLBACK` to be set):

```sh
python -m much alternate assets/bot/alternation-list.txt assets/threads assets/bot/audio -r assets/images
```
