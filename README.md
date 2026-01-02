# jpeg2dct-numpy: Fast JPEG to DCT Coefficients

[![PyPI version](https://badge.fury.io/py/jpeg2dct-numpy.svg)](https://badge.fury.io/py/jpeg2dct-numpy)
[![Python Versions](https://img.shields.io/pypi/pyversions/jpeg2dct-numpy.svg)](https://pypi.org/project/jpeg2dct-numpy/)

> **Note**: This is a NumPy-only fork of the original [uber-research/jpeg2dct](https://github.com/uber-research/jpeg2dct) with modern Python support (3.10-3.14), **pre-built wheels with bundled libjpeg**, no TensorFlow dependency, macOS Apple Silicon compatibility, and active maintenance.

This repository contains source code useful for reproducing results presented in the paper [Faster Neural Networks Straight from JPEG](https://openreview.net/forum?id=S1ry6Y1vG) (ICLR workshop 2018):

```
@inproceedings{gueguen_2018_ICLR
  title={Faster Neural Networks Straight from JPEG},
  author={Lionel Gueguen and Alex Sergeev and Ben Kadlec and Rosanne Liu and Jason Yosinski},
  booktitle={International Conference on Learning Representations},
  year={2018}
}
```

## About

The jpeg2dct-numpy library provides native Python functions to read the Discrete Cosine Transform coefficients from images encoded in JPEG format.
The I/O operation leverages standard JPEG libraries ([libjpeg](http://libjpeg.sourceforge.net/) or [libjpeg-turbo](https://libjpeg-turbo.org/)) to perform the Huffman decoding and obtain the DCT coefficients.

**✨ New:** Pre-built wheels come with **libjpeg bundled** - no need to install system dependencies for most users!

## Usage
#### Read into numpy array
```python
from jpeg2dct.numpy import load, loads


#read from a file
jpeg_file = '/<jpeg2dct dir>/test/data/DCT_16_16.jpg'
dct_y, dct_cb, dct_cr = load(jpeg_file)
print ("Y component DCT shape {} and type {}".format(dct_y.shape, dct_y.dtype))
print ("Cb component DCT shape {} and type {}".format(dct_cb.shape, dct_cb.dtype))
print ("Cr component DCT shape {} and type {}".format(dct_cr.shape, dct_cr.dtype))

#read from in memory buffer
with open(jpeg_file, 'rb') as src:
    buffer = src.read()
dct_y, dct_cb, dct_cr = loads(buffer)

```

## Installation

### Quick Install (Recommended)

**For most users**, simply install via pip - pre-built wheels include libjpeg:

```bash
pip install jpeg2dct-numpy
```

**That's it!** The pre-built wheels for **Linux, macOS, and Windows** come with **libjpeg-turbo bundled**, so you don't need to install any system dependencies.

**Supported Platforms (Pre-built Wheels):**
- 🐧 **Linux** - x86_64, manylinux_2_17+ (most modern distributions)
- 🍎 **macOS** - macOS 15+ (Sequoia), Apple Silicon (arm64)
- 🪟 **Windows** - Windows 10/11, x64
- 🐍 **Python** - 3.10, 3.11, 3.12, 3.13, 3.14

> **Note:** Older macOS versions (14 or earlier) and Intel Macs will automatically fall back to building from source, which requires installing libjpeg-turbo manually. See "Building from Source" section below.

---

### Building from Source

If you need to build from source (development, unsupported platform, or custom builds), you'll need to install libjpeg-turbo first.

<details>
<summary><b>Click to expand: Building from Source Instructions</b></summary>

#### Requirements for Building from Source
1. Python 3.10+ (tested up to Python 3.14)
2. Numpy>=1.14.0
3. **libjpeg or libjpeg-turbo** (system library - see platform-specific instructions below)
4. C++ compiler (gcc, clang, or MSVC)

#### Platform-Specific Setup

Choose the instructions for your operating system:

<details>
<summary><b>🍎 macOS (Intel & Apple Silicon)</b></summary>

Install libjpeg-turbo via Homebrew:

```bash
# Install libjpeg-turbo
brew install jpeg-turbo

# Install jpeg2dct-numpy
pip install jpeg2dct-numpy
```

The setup.py automatically detects Homebrew installations in:
- `/opt/homebrew` (Apple Silicon M1/M2/M3)
- `/usr/local` (Intel)

</details>

<details>
<summary><b>🐧 Linux (Ubuntu/Debian)</b></summary>

Install libjpeg-turbo development package:

```bash
# Update package list
sudo apt-get update

# Install libjpeg-turbo with headers
sudo apt-get install -y libjpeg-turbo8-dev

# Alternatively, install standard libjpeg (slower)
# sudo apt-get install -y libjpeg-dev

# Install jpeg2dct-numpy
pip install jpeg2dct-numpy
```

**For other Linux distributions:**

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install libjpeg-turbo-devel
# or: sudo yum install libjpeg-turbo-devel
pip install jpeg2dct-numpy
```

**Arch Linux:**
```bash
sudo pacman -S libjpeg-turbo
pip install jpeg2dct-numpy
```

</details>

<details>
<summary><b>🪟 Windows</b></summary>

**Option 1: Using vcpkg (Recommended)**

```powershell
# Install vcpkg if you haven't already
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg
.\bootstrap-vcpkg.bat

# Install libjpeg-turbo
.\vcpkg install libjpeg-turbo:x64-windows

# Set environment variable (in the same session or permanently)
$env:VCPKG_ROOT = "C:\path\to\vcpkg"

# Install jpeg2dct-numpy
pip install jpeg2dct-numpy
```

**Option 2: Using Conda (Easier)**

```powershell
# Install libjpeg via conda
conda install -c conda-forge libjpeg-turbo

# Install jpeg2dct-numpy
pip install jpeg2dct-numpy
```

**Note**: You'll need Microsoft Visual C++ 14.0 or greater. Get it from "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/

</details>

#### Installing from Source

After installing libjpeg-turbo (see platform-specific setup above):

```bash
# Clone the repository
git clone https://github.com/chunchet-ng/jpeg2dct.git
cd jpeg2dct

# Install in development mode
pip install -e .
```

The build process automatically:
- Detects libjpeg installation paths on your platform:
  - **macOS**: Homebrew paths (`/opt/homebrew`, `/usr/local`)
  - **Linux**: System paths (`/usr/include`, `/usr/lib`, arch-specific paths)
  - **Windows**: vcpkg paths (via `VCPKG_ROOT` environment variable)
- Detects Conda environments (all platforms)
- Configures appropriate C++ compilation flags for your platform
- Links against the libjpeg library

</details>

---

### Verifying the Installation

```bash
# Test import
python -c "from jpeg2dct.numpy import load, loads; print('jpeg2dct-numpy installed successfully!')"

# Run full test suite (if you have pytest installed)
pytest -v
```

---

## Troubleshooting

> **Note:** Most issues below only apply when **building from source**. If you're using pre-built wheels via `pip install jpeg2dct-numpy`, you won't encounter these issues.

<details>
<summary><b>❌ "cannot find -ljpeg" or "jpeglib.h: No such file or directory"</b></summary>

This error only occurs when **building from source**. Pre-built wheels don't have this issue.

If building from source, this means libjpeg is not installed or not found by the compiler.

**Linux:**
```bash
# Make sure you installed the -dev package
sudo apt-get install libjpeg-turbo8-dev

# Check if library exists
ldconfig -p | grep jpeg
```

**macOS:**
```bash
# Reinstall jpeg-turbo
brew reinstall jpeg-turbo

# Check installation
brew info jpeg-turbo
```

**Windows:**
```powershell
# Make sure VCPKG_ROOT is set
echo $env:VCPKG_ROOT

# Verify libjpeg is installed
.\vcpkg list | Select-String jpeg
```

</details>

<details>
<summary><b>❌ "Microsoft Visual C++ 14.0 or greater is required" (Windows)</b></summary>

Install Microsoft C++ Build Tools:
1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run the installer
3. Select "Desktop development with C++"
4. Install and restart

</details>

<details>
<summary><b>❌ ModuleNotFoundError: No module named '_dctfromjpg_wrapper'</b></summary>

The C++ extension wasn't built properly. Try:

```bash
# Clean and rebuild
pip uninstall jpeg2dct-numpy
pip install --no-cache-dir jpeg2dct-numpy

# Or from source:
pip install -e . --force-reinstall --no-cache-dir
```

</details>

<details>
<summary><b>❌ ImportError: libjpeg.so.X: cannot open shared object file (Linux)</b></summary>

If you see this error even with pre-built wheels, your system might be missing the libjpeg runtime library. Install it:

```bash
# Ubuntu/Debian
sudo apt-get install libjpeg-turbo8

# Fedora/RHEL/CentOS
sudo dnf install libjpeg-turbo
```

Note: The pre-built wheels should work without this on most modern Linux systems (manylinux compatible).

</details>

<details>
<summary><b>✓ Manual Library Path Configuration</b></summary>

If libjpeg is installed in a custom location, set environment variables:

**Linux/macOS:**
```bash
export C_INCLUDE_PATH=/path/to/jpeg/include:$C_INCLUDE_PATH
export LIBRARY_PATH=/path/to/jpeg/lib:$LIBRARY_PATH
export LD_LIBRARY_PATH=/path/to/jpeg/lib:$LD_LIBRARY_PATH
pip install jpeg2dct-numpy
```

**Windows:**
```powershell
$env:INCLUDE = "C:\path\to\jpeg\include;$env:INCLUDE"
$env:LIB = "C:\path\to\jpeg\lib;$env:LIB"
pip install jpeg2dct-numpy
```

</details>

---

## About This Fork

This fork is maintained by [Chun Chet Ng](https://github.com/chunchet-ng) and includes the following improvements over the original [uber-research/jpeg2dct](https://github.com/uber-research/jpeg2dct):

### What's New
- ✅ **Pre-built wheels with bundled libjpeg** - No system dependencies needed!
- ✅ **Python 3.10-3.14 support** (original supported up to 3.7)
- ✅ **Multi-platform wheels** - Linux (manylinux), macOS (Intel & Apple Silicon), Windows
- ✅ **Apple Silicon (M1/M2/M3) native support** for macOS
- ✅ **Automated releases** with semantic versioning
- ✅ **CI/CD with GitHub Actions** for automated testing and publishing
- ✅ **Modern Python packaging** with pyproject.toml
- ✅ **Improved documentation** with clear installation instructions
- ✅ **No TensorFlow dependency** - Pure NumPy implementation

### Why This Fork Exists
The original uber-research/jpeg2dct repository has been inactive since 2020. This fork aims to:
1. Keep the library compatible with modern Python versions
2. Provide easy installation with pre-built wheels (no compilation needed!)
3. Fix build issues on modern systems (especially macOS)
4. Provide ongoing maintenance and support
5. Make installation as simple as `pip install jpeg2dct-numpy`

### License
See [LICENSE](LICENSE) for full details.

### Contributing
Issues and pull requests are welcome!
