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

### Update baneks datasets

#### Update text dataset

1. Pull the marude [repo][marude]:

```sh
cd $HOME
git clone git@github.com:zeionara/marude.git
cd marude
git submodule update --init --recursive
```

2. Create and activate environment:

```sh
conda env create -f environment.yml
conda activate marude
python -c 'import nltk; nltk.download("punkt")'
```

3. Download anecdotes as plain text fragments (set the relevant date instead of `31.12.2025`):

```sh
./fetch.sh 31.12.2025
```

4. Pull the dataset [repo][baneks]:

```sh
cd $HOME
git clone git@hf.co:datasets/zeio/baneks
```

5. Copy generated files to `baneks` dataset:

```sh
cp marude/assets/baneks/31.12.2025/default.tsv baneks
cp marude/assets/baneks/31.12.2025/inflated.tsv baneks
cp marude/assets/baneks/31.12.2025/censored.tsv baneks
```

6. Update dataset version by editing `baneks/README.md`.

7. Upload the changes:

```sh
cd baneks
git add -u
git commit -m 'add(anecdotes): pulled more anecdotes from vk'
git push
```

#### Update speech dataset

1. Pull the dataset [repo][baneks-speech]:

```sh
cd $HOME
git clone git@hf.co:datasets/zeio/baneks-speech
```

2. Extract all records to a single folder

```sh
mkdir baneks-speech-merged
for file in $(ls ./baneks-speech/speech/*.tar.xz); do echo tar -xJvf $file -C $HOME/baneks-speech-merged; done
```

3. Pull the raconteur [repo][raconteur]:

```sh
git clone git@github.com:zeionara/raconteur.git
```

4. Create conda environment and configure required environment variables:

```sh
conda env create -f environment.yml
conda activate raconteur
export SALUTE_SPEECH_AUTH='salute speech token'
```

5. Run generation:

```sh
cd raconteur
python -m rr handle-aneks -s $HOME/baneks/default.tsv -d $HOME/baneks-speech-merged -e salute -rkv
```

6. Open directory `$HOME/baneks-speech-merged` in file manager, review generated records, delete irrelevant ones. Then move records which correspond to batches that should be updated, to separate folders, like `$HOME/baneks-speech-040001-041000` and `$HOME/baneks-speech-041001-041555`. The last batch might be incomplete.

7. Generate tar archives from the created folders using script inside `baneks-speech` project:

```sh
cd $HOME/baneks-speech
mv speech deprecated || echo 'Directory speech does not exist'
python make-batches.py $HOME/baneks-speech-merged speech
```

8. Update python script `$HOME/baneks-speech/baneks-speech.py` and `$HOME/baneks-speech/README.md`. Make sure that it contains the correct value of `BaneksSpeech.VERSION` and `_N_TOTAL`.

9. Upload the changes:

```sh
cd baneks-speech
git add speech/*.tar.xz
git commit -m 'feat(aneks): added more anekdotes'
git push
```

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

## Etc

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
[baneks-speech]: https://huggingface.co/datasets/zeio/baneks-speech
[raconteur]: https://github.com/zeionara/raconteur
[marude]: https://github.com/zeionara/marude
[baneks]: https://huggingface.co/datasets/zeio/baneks
