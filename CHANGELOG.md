# [1.0.0](https://github.com/chunchet-ng/jpeg2dct/compare/v0.1.0...v1.0.0) (2026-01-02)


### Features

* remove tensorflow and add automated releases with bundled libjpeg wheels ([a7cc457](https://github.com/chunchet-ng/jpeg2dct/commit/a7cc457d761e79ea291d5ba845efb5d988f8d828))


### BREAKING CHANGES

* - Configure semantic-release for automated versioning and PyPI publishing
- Set up cibuildwheel to build wheels for Python 3.10-3.14 on Linux, macOS, and Windows
- Bundle libjpeg-turbo in wheels via auditwheel/delocate/delvewheel
- Update README with badges and simplified installation instructions
- Users can now pip install without system libjpeg dependency
