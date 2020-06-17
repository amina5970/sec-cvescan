import bz2
import contextlib
import os
import pathlib
import shutil
import urllib.parse

import appdirs
import cachecontrol
import cachecontrol.caches.file_cache
import requests
import vistir

from cvescan.errors import BZ2Error, DownloadError


def get_cache_dir() -> str:
    cache_dir_base = os.environ.get("SNAP_USER_COMMON", None)
    if cache_dir_base is not None:
        cache_dir = pathlib.Path(cache_dir_base) / "cvescan"
    else:
        cache_dir = pathlib.Path(
            appdirs.user_cache_dir("cvescan", appauthor="canonical")
        )
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_cache_path_for_url(url: str) -> str:
    parsed_url = urllib.parse.urlparse(url)
    cache_dir = get_cache_dir() / parsed_url.netloc
    cache_dir.mkdir(exist_ok=True)
    return cache_dir.as_posix()


def default_handler(source_fp, target_handle):
    shutil.copyfileobj(source_fp, target_handle)


def bz2_handler(source_fp, target_handle):
    target_handle.write(bz2.decompress(source_fp.read()))


def download(download_url, target=None, handler=default_handler):
    if target is None:
        target = get_cache_path_for_url(download_url)
    parsed_url = urllib.parse.urlparse(download_url)
    filename = os.path.join(target, os.path.basename(parsed_url.path))
    web_cache = cachecontrol.caches.file_cache.FileCache(target)
    ctx = contextlib.ExitStack()
    try:
        with contextlib.ExitStack() as ctx:
            requests_session = ctx.enter_context(requests.Session())
            session = ctx.enter_context(
                cachecontrol.CacheControl(requests_session, web_cache)
            )
            cache_handle = ctx.enter_context(open(filename, "wb"))
            fp = ctx.enter_context(
                vistir.contextmanagers.open_file(
                    download_url, session=session, stream=True
                )
            )
            handler(fp, cache_handle)
    except Exception as ex:
        raise DownloadError("Downloading %s failed: %s" % (download_url, ex))
    finally:
        ctx.close()
    return filename


def bz2_download(bz2_archive):
    target = get_cache_path_for_url(bz2_archive)
    try:
        return download(bz2_archive, target, handler=bz2_handler)
    except Exception as ex:
        raise BZ2Error("Decompressing %s to %s failed: %s" % (bz2_archive, target, ex))


def download_bz2_file(logger, base_url, src_file):
    logger.debug("Downloading and decompressing %s/%s" % (base_url, src_file))
    return bz2_download("{0}/{1}".format(base_url, src_file))
