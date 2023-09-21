import re


SPACE = re.compile('\\s+')


class Splitter:
    def __init__(self, max_n_characters: int = None):
        self.max_n_characters = max_n_characters

    def split(self, text: str):
        if self.max_n_characters is None:
            return (text, )
        if len(text) < 1:
            return ('', )

        max_n_characters = self.max_n_characters

        chunks = []
        n_characters_in_current_chunk = 0
        current_chunk = []

        current_token = []
        current_space = []
        previous_c = None

        n_characters_in_current_token = 0
        n_characters_in_space_after_current_token = 0
        n_characters_in_space_after_previous_token = None
        previous_space = None

        watching_space = True if SPACE.fullmatch(text[0]) else False

        # def increment():
        #     nonlocal n_characters_in_current_token, n_characters_in_space_after_current_token

        #     if watching_space:
        #         n_characters_in_space_after_current_token += 1
        #     else:
        #         n_characters_in_current_token += 1

        def push(c: str):
            nonlocal current_token, current_space, n_characters_in_current_token, n_characters_in_space_after_current_token, previous_space

            if watching_space:
                current_space.append(c)
                n_characters_in_space_after_current_token += 1
            else:
                current_token.append(c)
                n_characters_in_current_token += 1

        def reset(c: str = None):
            nonlocal n_characters_in_current_token, n_characters_in_space_after_current_token, current_token, n_characters_in_current_chunk, n_characters_in_space_after_previous_token, current_chunk
            nonlocal current_space, previous_space

            # print(current_token, current_space, n_characters_in_current_chunk)

            if n_characters_in_current_token > 0:
                if n_characters_in_current_chunk + n_characters_in_current_token + (
                    0 if n_characters_in_space_after_previous_token is None else n_characters_in_space_after_previous_token
                ) <= max_n_characters:
                    n_characters_in_current_chunk += n_characters_in_current_token

                    if n_characters_in_space_after_previous_token is not None:
                        n_characters_in_current_chunk += n_characters_in_space_after_previous_token
                        current_chunk.extend(previous_space)

                    n_characters_in_space_after_previous_token = n_characters_in_space_after_current_token
                    previous_space = current_space

                    current_chunk.extend(current_token)
                else:
                    chunks.append(''.join(current_chunk))

                    current_chunk = current_token
                    n_characters_in_current_chunk = n_characters_in_current_token

                    n_characters_in_space_after_previous_token = n_characters_in_space_after_current_token
                    previous_space = current_space

            # print(current_token, current_chunk)

            if c is not None:
                current_token = [c]
                current_space = []

                n_characters_in_current_token = 1
                n_characters_in_space_after_current_token = 0
            else:
                chunks.append(''.join(current_chunk))

        for c in text:
            if not SPACE.fullmatch(c) and previous_c is not None and SPACE.fullmatch(previous_c):  # token + space has finished
                watching_space = False
                # print(current_token)
                reset(c)
            else:
                if SPACE.fullmatch(c) and previous_c is not None and not SPACE.fullmatch(previous_c):  # token has finished, space has started
                    watching_space = True
                else:
                    if n_characters_in_current_token >= max_n_characters:
                        reset(c)
                        continue
                    # print('--')
                # current_token.append(c)
                push(c)
                # print(n_characters_in_current_chunk, c)

            # n_characters_in_current_chunk += 1
            previous_c = c

            # increment()

        reset()

        return tuple(chunks)
