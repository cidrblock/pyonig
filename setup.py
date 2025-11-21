"""Setup script for pyonig with C extension."""
import glob
import os
from setuptools import Extension, setup

# Get all oniguruma C source files
# Note: unicode_*_data.c files are #included by unicode.c, not compiled separately
# But the unicode_fold*_key.c and unicode_unfold_key.c files ARE compiled separately
onig_src_dir = "deps/oniguruma/src"
onig_sources = [
    os.path.join(onig_src_dir, f) for f in [
        "regparse.c", "regcomp.c", "regexec.c", "reggnu.c",
        "regerror.c", "regext.c", "regsyntax.c", "regtrav.c",
        "regversion.c", "st.c", "regenc.c", "regposix.c",
        "unicode.c",  # This file #includes the unicode_*_data.c files
        "unicode_unfold_key.c", "unicode_fold1_key.c",
        "unicode_fold2_key.c", "unicode_fold3_key.c",
        "ascii.c", "utf8.c", "utf16_be.c", "utf16_le.c",
        "utf32_be.c", "utf32_le.c",
        "euc_jp.c", "euc_jp_prop.c", "sjis.c", "sjis_prop.c", "iso8859_1.c", "iso8859_2.c",
        "iso8859_3.c", "iso8859_4.c", "iso8859_5.c", "iso8859_6.c",
        "iso8859_7.c", "iso8859_8.c", "iso8859_9.c", "iso8859_10.c",
        "iso8859_11.c", "iso8859_13.c", "iso8859_14.c", "iso8859_15.c",
        "iso8859_16.c", "euc_tw.c", "euc_kr.c", "big5.c",
        "gb18030.c", "koi8_r.c", "cp1251.c",
        "onig_init.c",
    ]
]

# Our extension module
extension = Extension(
    "pyonig._pyonig",
    sources=["src/pyonig/_pyonigmodule.c"] + onig_sources,
    include_dirs=[onig_src_dir],
    define_macros=[],
    extra_compile_args=["-DHAVE_CONFIG_H"],
)

setup(
    ext_modules=[extension],
)

