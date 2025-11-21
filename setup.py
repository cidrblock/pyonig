"""Setup script for pyonig with C extension."""
import glob
import os
import subprocess
import sys
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

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


class BuildExtWithConfigure(build_ext):
    """Custom build_ext that runs autoreconf and configure for oniguruma."""

    def run(self):
        """Run autoreconf and configure before building the extension."""
        onig_dir = "deps/oniguruma"
        config_h = os.path.join(onig_dir, "src", "config.h")
        
        # Only configure if config.h doesn't exist
        if not os.path.exists(config_h):
            print("Configuring oniguruma...")
            try:
                # Run autoreconf
                subprocess.check_call(
                    ["autoreconf", "-vfi"],
                    cwd=onig_dir,
                )
                # Run configure
                subprocess.check_call(
                    ["./configure", "--disable-shared", "--enable-static"],
                    cwd=onig_dir,
                )
                print("Oniguruma configured successfully")
            except subprocess.CalledProcessError as e:
                print(f"ERROR: Failed to configure oniguruma: {e}", file=sys.stderr)
                print("Please run manually:", file=sys.stderr)
                print(f"  cd {onig_dir} && autoreconf -vfi && ./configure --disable-shared --enable-static", file=sys.stderr)
                sys.exit(1)
            except FileNotFoundError as e:
                print(f"ERROR: Required tool not found: {e}", file=sys.stderr)
                print("Please install autotools: autoconf, automake, libtool", file=sys.stderr)
                sys.exit(1)
        else:
            print("Oniguruma already configured, skipping autoreconf/configure")
        
        # Now run the normal build_ext
        super().run()


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
    cmdclass={"build_ext": BuildExtWithConfigure},
)

