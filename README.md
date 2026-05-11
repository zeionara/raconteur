# Racounteur

An auxiliary tool for simplifying speech generation on arbitrary texts

## Set up enrivonment

Requires at least `7Gb` of disk space. First, clone the [marude][madure] repo:

```sh
git clone git@github.com:zeionara/marude.git /tmp/marude && sudo mv /tmp/marude /opt/marude && sudo chown -R $USERNAME:$USERNAME /opt/marude
```

After cloning the repo initialize the submodules:

```sh
cd /opt/marude && git submodule update --init
```

Configure links to `marude` submodules at the `/opt`:

```sh
for folder in /opt/marude/submodules/*; do submodule=$(echo $folder | rev | cut -d '/' -f 1 | rev); sudo ln -s /opt/marude/submodules/$submodule /opt/$submodule; cd /opt/$submodule; git pull origin master; git checkout master; done
```

Then create a new virtual environment (the package requires `Python 3.11.14`):

```sh
# Install python3.11 on gentoo
sudo emerge --ask dev-lang/python:3.11
eselect python list
eselect python set 2
# Install python3.11 on ubuntu
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.11
sudo apt-get install python3.11-venv
# Create virtual environment
python3.11 -m venv /opt/marude/.venv
```

Activate the environment using this command:

```sh
source /opt/marude/.venv/bin/activate
```

## Set up raconteur-only repo

Requires at least `7Gb` of disk space. First, clone the repo:

```sh
git clone git@github.com:zeionara/raconteur.git /tmp/raconteur && sudo mv /tmp/raconteur /opt && sudo chown -R $USERNAME:$USERNAME /opt/raconteur
```

After cloning the repo initialize the submodules:

```sh
cd /opt/raconteur && git submodule update --init
```

Then create a new virtual environment (the package requires `Python 3.11.14`):

```sh
# Install python3.11 on gentoo
sudo emerge --ask dev-lang/python:3.11
eselect python list
eselect python set 2
# Install python3.11 on ubuntu
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.11
sudo apt-get install python3.11-venv
# Create virtual environment
python3.11 -m venv .venv
```

For convenience, create link to `/opt/raconteur/submodules/much` at the `/opt/much`:

```sh
sudo ln -s /opt/raconteur/submodules/much /opt/much
```

Checkout the latest version of `much` package:

```sh
cd /opt/much
git pull origin master
git checkout master
```

Likewise, create link to `/opt/raconteur/submodules/karma` at the `/opt/karma`:

```sh
sudo ln -s /opt/raconteur/submodules/karma /opt/karma
```

Checkout the latest version of `karma` package:

```sh
cd /opt/karma
git pull origin master
git checkout master
```

Go back to `/opt/raconteur` and activate the environment:

```sh
cd /opt/raconteur
source .venv/bin/activate
```

Install dependencies by running the following command:

```sh
pip install chatterbox-tts kokoro ipython music-tag num2words transliterate 'python-telegram-bot[job-queue]' peft sentencepiece aiohttp beautifulsoup4
```

Or using provided `requirements.txt`:

```sh
pip install -r requirements.txt
```

## Set up patch dataset

Go to the `/opt/much/assets` folder:

```sh
cd /opt/much/assets
```

Clone [patch][patch] dataset there:

```sh
git clone git@hf.co:datasets/zeio/patch
```

Install `git lfs`:

```sh
cd /opt/much/assets/patch
# Install git lfs on gentoo
sudo emerge --ask dev-vcs/git-lfs
# Install git lfs on ubuntu
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt-get install git-lfs
```

To enable `git lfs` for `patch` repo:

```sh
git lfs install
```

Pull `lfs` files:

```sh
git lfs pull
```

On how to update [patch][patch] dataset see [this guide](https://github.com/zeionara/much#pulling-all-active-threads-from-the-2ch-website-to-update-patch-dataset).

## Use

### Update baneks datasets

#### Update text dataset

Clone the [marude][marude] repo:

```sh
git clone git@github.com:zeionara/marude.git /tmp/marude && sudo mv /tmp/marude /opt/marude && sudo chown -R $USERNAME:$USERNAME /opt/marude
```

2. Create and activate environment:

```sh
# 1. Install python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.11
sudo apt-get install python3.11-venv
# 2. Create environment
cd /opt/marude
python3.11 -m venv .venv
# 3. Install dependencies
. .venv/bin/activate
pip install -r requirements.txt
```

3. Download anecdotes as plain text fragments (set the relevant date instead of `31.12.2025`):

```sh
mkdir -p assets/baneks
./fetch.sh 31.12.2025
```

4. Pull the dataset [repo][baneks]:

```sh
git clone git@hf.co:datasets/zeio/baneks /tmp/baneks
sudo mv /tmp/baneks /opt/baneks
sudo chown -R zeio:zeio /opt/baneks
```

5. Copy generated files to `baneks` dataset:

```sh
cp assets/baneks/31.12.2025/default.tsv /opt/baneks
cp assets/baneks/31.12.2025/inflated.tsv /opt/baneks
cp assets/baneks/31.12.2025/censored.tsv /opt/baneks
```

6. Update dataset version by editing `/opt/baneks/README.md`:

```sh
cd /opt/baneks
vim README.md
```

7. Upload the changes:

```sh
cd /opt/baneks
git add -u
git commit -m 'add(anecdotes): pulled more anecdotes from vk'
git push
```

#### Update speech dataset

1. Pull the dataset [repo][baneks-speech]:

```sh
git clone git@hf.co:datasets/zeio/baneks-speech /tmp/baneks-speech
sudo mv /tmp/baneks-speech /opt/baneks-speech
sudo chown -R zeio:zeio /opt/baneks-speech
```

2. Extract all records to a single folder

```sh
cd /opt/baneks-speech
mkdir extracted
for file in $(ls ./speech/*.tar.xz); do tar -xJvf $file -C ./extracted; done
```

3. Configure [raconteur][raconteur] environment:

```sh
conda activate raconteur
export SALUTE_SPEECH_AUTH='salute speech token'
```

4. Run generation:

```sh
cd /opt/marude
python -m rr handle-aneks -s /opt/baneks/default.tsv -d /opt/baneks-speech/extracted -e salute -rkv
```

6. Create folder with the last batch:

```sh
cd /opt/baneks-speech
mkdir extracted-last
tar -xJvf speech/041001-041425.tar.xz -C ./extracted-last
```

7. Copy recently generated files to the last batch, move files which exceed the batch size to the next batch:

```sh
find ./extracted/ -mmin -60 -type f | xargs -I {} cp {} ./extracted-last
mkdir ./extracted-next
ls -t ./extracted-last | head -n 135 | xargs -I {} mv ./extracted-last/{} ./extracted-next
```

7. Generate tar archives from the created folders:

```sh
tar -cJvf speech/041001-042000.tar.xz -C extracted-last .
tar -cJvf speech/042001-042135.tar.xz -C extracted-last .
rm speech/041001-041425.tar.xz
```

8. Update python script `$HOME/baneks-speech/baneks-speech.py` and `$HOME/baneks-speech/README.md`. Make sure that it contains the correct value of `BaneksSpeech.VERSION` and `_N_TOTAL`.

9. Upload the changes:

```sh
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
[fuck]: https://github.com/zeionara/fuck
[baneks]: https://huggingface.co/datasets/zeio/baneks
[patch]: https://huggingface.co/datasets/zeio/patch
