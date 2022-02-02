#!/usr/bin/env python3
"""
:mod:`text_stream` -- Text Data Model
=====================================

.. module text
   :platform: Unix, Windows, Mac, Linux
   :synopsis: An interface to unify the operations on a file, a multi-line string, or standard input.
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

from io import StringIO
from pathlib import PurePath, Path
from typing import Optional, Iterator, Tuple, Union

from lazy_property import LazyProperty

# ========================================= What can be exported? =========================================
__all__ = ['TextStream']


class TextStream:
    """
    This is a general model for text streams.
    A text stream consists of one or more lines of text that can be written to a text-oriented display
    so that they can be read. When reading from a text stream, the program reads a *newline* at
    the end of each line. When writing to a text stream, the program writes a *newline* to signal the
    end of a line. [#f]_

    You can specify nothing in ``TextStream`` instance creation procedure,
    then data will be read from interactive input, you can press <Ctrl+D> to end this input.
    If you give it a string, with *newline* separator specified by ``'\\n'`` or ``'\\r\\n'``,
    then the string will be parsed by this separator.
    If you give a file path in *inp*, and if it is valid, then the file will be read.

    .. rubric:: Footnotes

    .. [#f] Referenced from `here <https://docs.microsoft.com/en-us/cpp/c-runtime-library/text-and-binary-streams>`_.

    :param inp: Input, can be a ``str``, an ``StringIO`` instance, a ``pathlib.PurePath`` object,...
        or ``None`` (which means read from standard input).
    """

    def __init__(self, inp: Union[str, StringIO, PurePath, None] = None):
        self.__infile_path = None

        if inp is None:
            self.__stream = StringIO(_user_input())
        elif isinstance(inp, str):
            self.__stream = StringIO(inp)
        elif isinstance(inp, StringIO):
            self.__stream = inp
        elif isinstance(inp, PurePath):
            if Path(inp).expanduser().is_file():
                self.__infile_path = inp
                with open(inp) as f:
                    self.__stream = StringIO(f.read())
            else:
                raise FileNotFoundError(
                    "The *inp* argument '{0}' is not a valid file!".format(inp))
        else:
            raise TypeError(
                "Unsupported type! The only recognized types are ``str`` and ``io.StringIO`` and ``None``!")

    @property
    def stream(self) -> StringIO:
        """
        Read-only property.

        :return: An ``io.StringIO`` object, contain all the content in the input file or string.
        """
        return self.__stream

    @property
    def infile_path(self) -> Optional[PurePath]:
        """
        Read-only property.

        :return: A ``pathlib.PurePath`` object or ``None``.
        """
        if not self.__infile_path:
            return Path(self.__infile_path).expanduser()
        return None

    def generator(self) -> Iterator[str]:
        """
        Create a generate that iterates the whole content of the file or string.

        :return: An iterator iterating the lines of the text stream, separated by ``'\\n'`` or ``'\\r'``.
        """
        stream = self.stream  # In case that ``self.stream`` is changed.
        stream.seek(0)
        for line in stream:
            yield line

    def generator_telling_position(self) -> Iterator[Tuple[str, int]]:
        """
        Create a generate that iterates the whole content of the file or string, and also tells which offset is now.

        :return: An iterator iterating tuples, containing lines of the text stream,...
            separated by ``'\\n'`` or ``'\\r'``; and the offset (in bytes) of current line.
        """
        stream = self.stream  # In case that ``self.stream`` is changed.
        stream.seek(0)
        for line in stream:
            yield line, stream.tell()

    def generator_starts_from(self, offset, whence: Optional[int] = 0) -> Iterator[str]:
        """
        Create a generate that iterates the whole content of the file or string, starting from *offset* bytes.

        :param offset: Change the stream position to the given byte *offset*....
            *offset* is interpreted relative to the position indicated by *whence*. The default value for whence is ``SEEK_SET``.
        :param whence: Values for whence are:...
            - ``SEEK_SET`` or ``0`` – start of the stream (the default); *offset* should be zero or positive...
            - ``SEEK_CUR`` or ``1`` – current stream position; *offset* may be negative...
            - ``SEEK_END`` or ``2`` – end of the stream; *offset* is usually negative
        :return: An iterator iterating the lines of the text stream, separated by ``'\\n'`` or ``'\\r'``, starting...
            from given byte *offset*.
        """

        stream = self.stream  # In case that ``self.stream`` is changed.
        stream.seek(offset, whence)
        for line in stream:
            yield line

    def generator_between(self, begin: int, end: int) -> Iterator[str]:
        """
        Create a generate that iterates the whole content of the file or string, starting from *begin* index,
        end by *end* index. **Not byte!**

        :param begin: An integer labels the starting index.
        :param end: An integer labels the ending index.
        :return: An iterator of string.
        """

        s: str = self.content[begin:end + 1]
        for line in s:
            yield line

    @LazyProperty
    def content(self) -> str:
        """
        Read the whole file or string, and return it.

        :return: The whole contents of the file or the string.
        """

        return self.stream.getvalue()


def _user_input() -> str:
    """
    A helper function which waits for user multi-line input.

    :return: A string input by user, separated by ``'\\n'``.
    """

    lines = []
    try:
        while True:
            line = input()
            if line != '':
                lines.append(line)
            else:
                break
    except (EOFError, KeyboardInterrupt):
        return '\n'.join(lines)
