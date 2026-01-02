# Copyright (c) 2018 Uber Technologies, Inc.
#
# Licensed under the Uber Non-Commercial License (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at the root directory of this project.
#
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import sys
import textwrap
import traceback

from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext
from setuptools.errors import (
    CompileError,
    LinkError,
)
from setuptools.errors import (
    PlatformError as DistutilsPlatformError,
)


# Read version from __init__.py without importing (avoids circular dependency)
def get_version():
    init_file = os.path.join(os.path.dirname(__file__), "jpeg2dct", "__init__.py")
    with open(init_file, "r") as f:
        content = f.read()
        version_match = re.search(
            r"^__version__\s*=\s*['\"]([^'\"]+)['\"]", content, re.M
        )
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string in jpeg2dct/__init__.py")


__version__ = get_version()

common_lib = Extension("jpeg2dct.common.common_lib", [])
numpy_lib = Extension("jpeg2dct.numpy._dctfromjpg_wrapper", [])


def get_cpp_flags(build_ext):
    last_err = None

    # Windows (MSVC) uses different compiler flags
    if sys.platform == "win32":
        # MSVC compiler flags
        flags_to_try = [
            ["/std:c++14", "/O2"],  # Try C++14 first (better support)
            ["/std:c++11", "/O2"],  # Fallback to C++11
        ]
    elif sys.platform == "darwin":
        # macOS: Clang with libc++
        default_flags = ["-std=c++11", "-fPIC", "-O2"]
        flags_to_try = [default_flags + ["-stdlib=libc++"], default_flags]
    else:
        # Linux: GCC/Clang
        default_flags = ["-std=c++11", "-fPIC", "-O2"]
        flags_to_try = [default_flags, default_flags + ["-stdlib=libc++"]]

    for cpp_flags in flags_to_try:
        try:
            test_compile(
                build_ext,
                "test_cpp_flags",
                extra_preargs=cpp_flags,
                code=textwrap.dedent("""\
                    #include <unordered_map>
                    void test() {
                    }
                    """),
            )

            return cpp_flags
        except (CompileError, LinkError):
            last_err = "Unable to determine C++ compilation flags (see error above)."
        except Exception:
            last_err = (
                "Unable to determine C++ compilation flags.  "
                "Last error:\n\n%s" % traceback.format_exc()
            )

    raise DistutilsPlatformError(last_err)


def test_compile(
    build_ext,
    name,
    code,
    libraries=None,
    include_dirs=None,
    library_dirs=None,
    macros=None,
    extra_preargs=None,
):
    test_compile_dir = os.path.join(build_ext.build_temp, "test_compile")
    if not os.path.exists(test_compile_dir):
        os.makedirs(test_compile_dir)

    source_file = os.path.join(test_compile_dir, "%s.cc" % name)
    with open(source_file, "w") as f:
        f.write(code)

    compiler = build_ext.compiler
    [object_file] = compiler.object_filenames([source_file])
    shared_object_file = compiler.shared_object_filename(
        name, output_dir=test_compile_dir
    )

    compiler.compile(
        [source_file],
        extra_preargs=extra_preargs,
        include_dirs=include_dirs,
        macros=macros,
    )
    compiler.link_shared_object(
        [object_file],
        shared_object_file,
        libraries=libraries,
        library_dirs=library_dirs,
    )

    return shared_object_file


def get_conda_include_dir():
    prefix = os.environ.get("CONDA_PREFIX", ".")
    return [os.path.join(prefix, "include")]


def get_system_jpeg_paths():
    """Get libjpeg include and library paths for the current platform."""
    include_dirs = []
    library_dirs = []

    if sys.platform == "darwin":
        # macOS: Check Homebrew prefixes (Apple Silicon and Intel)
        brew_prefixes = ["/opt/homebrew", "/usr/local"]

        for prefix in brew_prefixes:
            # Check for libjpeg-turbo
            jpeg_include = os.path.join(prefix, "opt", "jpeg-turbo", "include")
            jpeg_lib = os.path.join(prefix, "opt", "jpeg-turbo", "lib")

            if os.path.exists(jpeg_include):
                include_dirs.append(jpeg_include)
            if os.path.exists(jpeg_lib):
                library_dirs.append(jpeg_lib)

            # Also check regular jpeg as fallback
            jpeg_include_alt = os.path.join(prefix, "opt", "jpeg", "include")
            jpeg_lib_alt = os.path.join(prefix, "opt", "jpeg", "lib")

            if (
                os.path.exists(jpeg_include_alt)
                and jpeg_include_alt not in include_dirs
            ):
                include_dirs.append(jpeg_include_alt)
            if os.path.exists(jpeg_lib_alt) and jpeg_lib_alt not in library_dirs:
                library_dirs.append(jpeg_lib_alt)

    elif sys.platform.startswith("linux"):
        # Linux: Check common system paths
        common_paths = [
            "/usr/include",
            "/usr/local/include",
            "/usr/include/x86_64-linux-gnu",
            "/usr/include/aarch64-linux-gnu",
        ]
        common_lib_paths = [
            "/usr/lib",
            "/usr/local/lib",
            "/usr/lib/x86_64-linux-gnu",
            "/usr/lib/aarch64-linux-gnu",
        ]

        for path in common_paths:
            if os.path.exists(path):
                include_dirs.append(path)

        for path in common_lib_paths:
            if os.path.exists(path):
                library_dirs.append(path)

    elif sys.platform == "win32":
        # Windows: Check common installation paths
        # vcpkg default path
        vcpkg_root = os.environ.get("VCPKG_ROOT")
        if vcpkg_root:
            vcpkg_include = os.path.join(
                vcpkg_root, "installed", "x64-windows", "include"
            )
            vcpkg_lib = os.path.join(vcpkg_root, "installed", "x64-windows", "lib")
            if os.path.exists(vcpkg_include):
                include_dirs.append(vcpkg_include)
            if os.path.exists(vcpkg_lib):
                library_dirs.append(vcpkg_lib)

    return include_dirs, library_dirs


def get_common_options(build_ext):
    cpp_flags = get_cpp_flags(build_ext)

    system_includes, system_libs = get_system_jpeg_paths()

    MACROS = []
    INCLUDES = [] + get_conda_include_dir() + system_includes
    SOURCES = []
    COMPILE_FLAGS = cpp_flags
    LINK_FLAGS = []
    LIBRARY_DIRS = [] + system_libs
    LIBRARIES = []

    return dict(
        MACROS=MACROS,
        INCLUDES=INCLUDES,
        SOURCES=SOURCES,
        COMPILE_FLAGS=COMPILE_FLAGS,
        LINK_FLAGS=LINK_FLAGS,
        LIBRARY_DIRS=LIBRARY_DIRS,
        LIBRARIES=LIBRARIES,
    )


def build_common_extension(build_ext, options, abi_compile_flags):
    common_lib.define_macros = options["MACROS"]
    common_lib.include_dirs = options["INCLUDES"]
    common_lib.sources = options["SOURCES"] + ["jpeg2dct/common/dctfromjpg.cc"]
    common_lib.extra_compile_args = options["COMPILE_FLAGS"] + abi_compile_flags
    common_lib.extra_link_args = options["LINK_FLAGS"]
    common_lib.library_dirs = options["LIBRARY_DIRS"]
    common_lib.libraries = options["LIBRARIES"] + ["jpeg"]
    # Set runtime library paths for Linux (helps find libjpeg.so at runtime)
    if sys.platform.startswith("linux"):
        common_lib.runtime_library_dirs = options["LIBRARY_DIRS"]

    build_ext.build_extension(common_lib)


def build_numpy_extension(build_ext, options, abi_compile_flags):
    import numpy

    numpy_lib.define_macros = options["MACROS"]
    numpy_lib.include_dirs = options["INCLUDES"] + [numpy.get_include()]
    numpy_lib.sources = options["SOURCES"] + [
        "jpeg2dct/numpy/dctfromjpg_wrap.cc",
        "jpeg2dct/common/dctfromjpg.cc",
    ]
    numpy_lib.extra_compile_args = options["COMPILE_FLAGS"] + abi_compile_flags
    numpy_lib.extra_link_args = options["LINK_FLAGS"]
    numpy_lib.library_dirs = options["LIBRARY_DIRS"]
    numpy_lib.libraries = options["LIBRARIES"] + ["jpeg"]
    # Set runtime library paths for Linux (helps find libjpeg.so at runtime)
    if sys.platform.startswith("linux"):
        numpy_lib.runtime_library_dirs = options["LIBRARY_DIRS"]

    build_ext.build_extension(numpy_lib)


# run the customize_compiler
class custom_build_ext(build_ext):
    def build_extensions(self):
        options = get_common_options(self)
        abi_compile_flags = []
        # On Windows, skip common_lib (causes linking issues,
        # not needed since code is in numpy_lib)
        if sys.platform != "win32":
            build_common_extension(self, options, abi_compile_flags)
        build_numpy_extension(self, options, abi_compile_flags)


# Build extensions list based on platform
# On Windows, only build numpy_lib (common_lib causes linking issues)
ext_modules = [numpy_lib] if sys.platform == "win32" else [common_lib, numpy_lib]

setup(
    name="jpeg2dct-numpy",
    version=__version__,
    packages=find_packages(),
    description=textwrap.dedent("""\
          Library providing a Python function to read JPEG image as a numpy
          array."""),
    author="Uber Technologies, Inc.",
    author_email="",
    maintainer="Chun Chet Ng",
    long_description=textwrap.dedent("""\
          jpeg2dct library provides native Python function to read JPEG image
          as a numpy array.

          This is a community-maintained fork with Python 3.10-3.14 support,
          macOS Apple Silicon compatibility, and libjpeg-turbo integration."""),
    long_description_content_type="text/plain",
    url="https://github.com/chunchet-ng/jpeg2dct",
    ext_modules=ext_modules,
    cmdclass={"build_ext": custom_build_ext},
    setup_requires=["numpy"],
    install_requires=["numpy"],
    tests_require=["pytest"],
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: C++",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    keywords="jpeg dct image-processing numpy",
    zip_safe=False,
)
