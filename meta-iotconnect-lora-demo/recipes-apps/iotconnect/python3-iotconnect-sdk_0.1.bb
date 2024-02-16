# Recipe created by recipetool
# This is the basis of a recipe and may need further editing in order to be fully functional.
# (Feel free to remove these comments when editing.)

# Unable to find any files that looked like license statements. Check the accompanying
# documentation and source headers and set LICENSE and LIC_FILES_CHKSUM accordingly.
#
# NOTE: LICENSE is being set to "CLOSED" to allow you to at least start building - if
# this is not accurate with respect to the licensing of the software being built (it
# will not be in most cases) you must specify the correct value before using this
# recipe for anything other than initial testing/development!
LICENSE = "GPL-3.0-only"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/GPL-3.0-only;md5=c79ff39f19dfec6d293b95dea7b07891"

SRC_URI = "git://git@github.com/avnet-iotconnect/iotc-python-sdk.git;protocol=ssh;branch=master-std-21"

# Modify these as desired
PV = "1.0+git${SRCPV}"
SRCREV = "8d03c8251db071c7cc9651a12e8709445ad4c56d"

S = "${WORKDIR}/git/iotconnect-sdk-1.0"
DISTUTILS_SETUP_PATH = "${WORKDIR}/git/iotconnect-sdk-1.0"

# NOTE: no Makefile found, unable to determine what needs to be done
inherit setuptools3


RDEPENDS:${PN} += " python3-pip"

RDEPENDS:${PN} += " python3-ntplib"
RDEPENDS:${PN} += " python3-paho-mqtt"
RDEPENDS:${PN} += " python3-wheel"

distutils_do_configure () {
	# Specify any needed configure commands here
	:
}

distutils_do_compile () {
	# Specify compilation commands here
	:
}

distutils_do_install () {
	# Specify install commands here
	:
}