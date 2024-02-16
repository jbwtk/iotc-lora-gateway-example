SUMMARY = "My Example Recipe"
HOMEPAGE = "https://www.example.com"
LICENSE = "CLOSED"
# LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=8e5f264c6988aec56808a3a11e77b913"

SRC_URI = "https://github.com/brocaar/chirpstack-api/archive/refs/tags/v3.12.4.tar.gz"

SRC_URI[md5sum] = "2491d0962f0c5f23e1b8ebf9d14010db"
SRC_URI[sha256sum] = "6dc6716ce23e56ff6ffb80d42140000f6e817a7356bc56607eea4f56c95c8154"

S = "${WORKDIR}/chirpstack-api-3.12.4/python/src"

inherit setuptools3

DEPENDS += "python3-native"

BBCLASSEXTEND = "native"