# Racounteur

An auxiliary tool for simplifying speech generation on arbitrary texts

## Install dependencies

To create a `conda` environment with required dependencies run the following command:

```sh
conda env create -f environment.yml
```

Install the following dependencies manually:

```sh
sudo apt-get install libportaudio2
```

## Testing

To run tests use the following statement:

```sh
python -m unittest discover test
```

## Usage

The app allows to synthesize speech for anecdotes from [this kaggle dataset](https://www.kaggle.com/datasets/zeionara/anecdotes?select=anecdotes.tsv) using various speech engines. To apply [salute-speech](https://developers.sber.ru/portal/products/smartspeech) for the task update the [`__main__.py`](https://github.com/zeionara/raconteur/blob/master/rr/__main__.py) script uncommenting the corresponding line with target engine and commenting the others, then execute the following command:

```sh
python -m rr handle-aneks -d assets/salute-speech -c 4000 -n 10
```

Similarly, to use [RuTTS toolkit](https://github.com/Tera2Space/RUTTS) run the following command:

```sh
python -m rr handle-aneks -n 10 -c 1000 -g
```

To use [Bark](https://github.com/suno-ai/bark) model use the following snippet:

```sh
python -m rr handle-aneks -n 10 -c 200
```
