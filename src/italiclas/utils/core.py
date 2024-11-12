"""Core utilities (no local dependencies)."""

import functools
import lzma
import os
import pickle
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

Typ = TypeVar("Typ")


# =====================================================================
def save_obj(
    obj: Any,  # noqa: ANN401
    filepath: Path,
    serializer: Callable = pickle.dumps,
    compressor: Callable | None = lzma.compress,
    *,
    binary: bool = True,
) -> None:
    """Save object to filepath.

    Args:
        obj: The object to save.
        filepath: The target filepath.
        serializer: Serialization function.
            Defaults to pickle.dumps.
        compressor: Compression function.
            Defaults to lzma.compress.
        binary: Open file as binary.
            Defaults to True.

    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with filepath.open(f"w{'b' if binary else ''}") as f:
        if callable(compressor):
            f.write(compressor(serializer(obj)))
        else:
            f.write(serializer(obj))


# =====================================================================
def load_obj(
    filepath: Path,
    deserializer: Callable = pickle.loads,
    decompressor: Callable | None = lzma.decompress,
    *,
    binary: bool = True,
) -> Any:  # noqa: ANN401
    """Load object from filepath.

    Args:
        filepath: The source filepath.
        deserializer: Deserialization function.
            Defaults to pickle.loads.
        decompressor: Decompression function.
            Defaults to lzma.decompress.
        binary: Open file as binary.
            Defaults to True.

    Returns:
        The loaded object.

    """
    with filepath.open(f"r{'b' if binary else ''}") as f:
        if callable(decompressor):
            obj = deserializer(decompressor(f.read()))
        else:
            obj = deserializer(f.read())
        return obj


# =====================================================================
def transform(
    obj: Typ,
    *transforms: Callable[[Typ], Typ],
) -> Typ:
    """Apply a sequence of transformation to an object.

    Args:
        obj: The input object.
        transforms: The transformation functions.
            Defaults to ().

    Returns:
        The transformed object.

    Examples:
        >>> transform("Ciao ", str.lower, str.strip)
        'ciao'

    """
    result = obj
    for transform in transforms:
        result = transform(result)
    return result


# =====================================================================
def simpler_text(
    text: str,
    allowed: str = "a-zA-Z0-9._-",
    replacing: str = "_",
    *,
    quench: bool = True,
) -> str:
    """Simplify a text string by replacing / removing unwanted characters.

    Args:
        text: The input string.
        allowed: The valid characters.
            Regular expression ranges can be used
            (e.g. a-z for lower case letters).
            Most other characters can be simply listed.
            The following characters need to be escaped:
             - The literal matching of "]" must be "\\["
             - The literal matching of "-" must be "\\-" or placed at the end.
            Defaults to "a-zA-Z0-9._-"
        replacing (str): The replacement text.
        quench (bool): Group consecutive non-allowed characters.
            If True, consecutive non-allowed characters are replaced by a
            single replacement.
            Otherwise, each character is replaced individually.

    Returns:
        The simplified text string.

    Examples:
        >>> print(simpler_text("ciao-ciao"))
        ciao-ciao
        >>> print(simpler_text(" -> data science is funny!!!"))
        _-_data_science_is_funny_

    """  # noqa: D301
    return re.sub(rf"[^{allowed}]{'+' if quench else ''}", replacing, text)


# =====================================================================
def namify(text: str) -> str:
    """Convert any text to a name-like string.

    Args:
        text: The input text.

    Returns:
        The name-like string.

    Examples:
        >>> print(namify("ciao-ciao"))
        ciao_ciao
        >>> print(namify("ciao-Ciao"))
        ciao_Ciao

    """
    return transform(
        text,
        functools.partial(
            simpler_text,
            allowed="a-zA-Z0-9_",
            replacing="_",
            quench=True,
        ),
        lambda x: x.strip("_"),
    )


# =====================================================================
def filenamify(text: str) -> str:
    """Convert any text to a filename-like string.

    Args:
        text: The input text.

    Returns:
        The name-like string.

    Examples:
        >>> print(filenamify("ciao-ciao.txt"))
        ciao_ciao.txt
        >>> print(filenamify("ciao-Ciao.TXT"))
        ciao_Ciao.TXT

    """
    return transform(
        text,
        functools.partial(
            simpler_text,
            allowed="a-zA-Z0-9_.",
            replacing="_",
            quench=True,
        ),
        lambda x: x.strip("_"),
    )


# =====================================================================
def labelify(name: str) -> str:
    """Convert a string from a name-like to a label-like format.

    Args:
        name: The input name-like string.

    Returns:
        The label-like string.

    Examples:
        >>> print(labelify("_ciao_ciao_"))
        Ciao Ciao

    """
    return transform(
        name,
        lambda x: re.sub(r"_+", " ", x),
        str.title,
        str.strip,
    )


# =====================================================================
def number2str(
    value: float,
    precision: int = 4,
    e_notation_after: int = 4,
    thousand_sep: str = "_",
) -> str:
    """Convert a value to a string with a given number of significant figures.

    This is achieved through a first conversion of the value to a string while
    truncating the number of significant figures using the `g` format.
    This alone has the issue of switching to exponent notation for integers.
    An extra round of conversions (back to `float` and again to `str`)
    workaround the issue.

    Args:
        value: The number to convert.
        precision: The number of significant figures.
            Must be 0 or more. If 0, this is treated as 1.
            Defaults to 4.
        e_notation_after: The exponential notation switch value.
            The exponential notation is used if the order of magnitude is
            smaller than -4 or if it is larger than or equal to
            `precision + e_notation_after`.
            Otherwise, use the standard notation.
            Must be 0 or more.
            Defaults to 2.
        thousand_sep: The thousand separator.
            Defaults to "_".

    Returns:
        The number with the specified number of significant figures as string.

    Examples:
        >>> values = [123 * 10 ** k for k in range(0, 6)]
        >>> for p in range(1, 5):
        ...     print([number2str(value, p) for value in values])
        ['100', '1_000', '10_000', '1e+05', '1e+06', '1e+07']
        ['120', '1_200', '12_000', '120_000', '1.2e+06', '1.2e+07']
        ['123', '1_230', '12_300', '123_000', '1_230_000', '1.23e+07']
        ['123', '1_230', '12_300', '123_000', '1_230_000', '12_300_000']
        >>> for p in range(1, 5):
        ...     print([number2str(value, p, 0) for value in values])
        ['1e+02', '1e+03', '1e+04', '1e+05', '1e+06', '1e+07']
        ['1.2e+02', '1.2e+03', '1.2e+04', '1.2e+05', '1.2e+06', '1.2e+07']
        ['123', '1.23e+03', '1.23e+04', '1.23e+05', '1.23e+06', '1.23e+07']
        ['123', '1_230', '1.23e+04', '1.23e+05', '1.23e+06', '1.23e+07']

        >>> values = [123 * 10 ** k for k in range(-7, 0)]
        >>> for p in range(1, 5):
        ...     print([number2str(value, p) for value in values])
        ['1e-05', '0.0001', '0.001', '0.01', '0.1', '1', '10']
        ['1.2e-05', '0.00012', '0.0012', '0.012', '0.12', '1.2', '12']
        ['1.23e-05', '0.000123', '0.00123', '0.0123', '0.123', '1.23', '12.3']
        ['1.23e-05', '0.000123', '0.00123', '0.0123', '0.123', '1.23', '12.3']
        >>> for p in range(1, 5):
        ...     print([number2str(value, p, 0) for value in values])
        ['1e-05', '0.0001', '0.001', '0.01', '0.1', '1', '1e+01']
        ['1.2e-05', '0.00012', '0.0012', '0.012', '0.12', '1.2', '12']
        ['1.23e-05', '0.000123', '0.00123', '0.0123', '0.123', '1.23', '12.3']
        ['1.23e-05', '0.000123', '0.00123', '0.0123', '0.123', '1.23', '12.3']

    """
    if precision == 0:
        precision = 1
    comma = "," if thousand_sep else ""
    result = f"{float(f'{value:.{precision}g}'):{comma}.{precision + e_notation_after}g}"  # noqa: E501
    if thousand_sep:
        result = result.replace(",", thousand_sep)
    return result


# =====================================================================
def no_blanks(text: str, replacing: str = "", *, quench: bool = True) -> str:
    """Replace blanks.

    Args:
        text: The input text.
        replacing: The replacement text.
            Defaults to "".
        quench (bool): Group consecutive blank characters.
            If True, consecutive blanks are replaced by a single replacement.
            Otherwise, each character is replaced individually.

    Returns:
        The processed text.

    Examples:
        >>> no_blanks("  ciao  mondo ")
        'ciaomondo'
        >>> no_blanks("  ciao  mondo ", "_")
        '_ciao_mondo_'
        >>> no_blanks("  ciao  mondo ", "_", quench=False)
        '__ciao__mondo_'

        >>> no_blanks("  ciao  mondo ".strip(), "_")
        'ciao_mondo'

    """
    return re.sub(rf"\s{'+' if quench else ''}", replacing, text)


# =====================================================================
def is_running_in_docker(
    *,
    use_env: bool = True,
    use_dockerenv: bool = True,
    use_cgroup: bool = True,
) -> bool:
    """Check if the script is running inside a Docker container.

    Internally, it relies on a custom heuristic looking:
        - `DOCKER_CONTAINER` environment variable being defined either
          in the `Dockerfile` or otherwise before running this script,
          as Docker itself does not provide it out-of-the-box.
        - the `/.dockerenv` file being present
        - the `/proc/self/cgroup` file containing the word `docker`

    If the Docker image is not based on a POSIX (UNIX/Linux) system,
    the last two heuristics will not work.

    Note that this requires some diligence, as nothing prevents a malicious
    user from artificially make this function evaluate to True even outside of
    a Docker container.

    Implementation note: internally is uses `os.path` instead of `pathlib`
    for speed.

    Args:
        use_env: Activate check on `DOCKER_CONTAINER` env var.
            Defaults to False.
        use_dockerenv: Activate check on `/.dockerenv` file presence.
            Defaults to True.
        use_cgroup: Activate check on `/proc/self/cgroup` file content.
            Specifically, it looks for the word `docker` inside such file.
            Defaults to True.

    Returns:
        True if heuristics detect the use of Docker, False otherwise.

    Examples:
        >>> is_running_in_docker()
        False

    """
    # : use os.path for speed
    dockerenv_path = Path("/.dockerenv")
    cgroup_path = Path("/proc/self/cgroup")
    return (
        (use_env and bool(os.environ.get("DOCKER_CONTAINER", False)))
        or (use_dockerenv and dockerenv_path.is_file())
        or (
            use_cgroup
            and cgroup_path.is_file()
            and any("docker" in line for line in cgroup_path.open())
        )
    )
