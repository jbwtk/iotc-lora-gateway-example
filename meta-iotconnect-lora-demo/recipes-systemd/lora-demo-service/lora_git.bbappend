# systemd component, installs only if systemd is part of image
inherit systemd
SYSTEMD_AUTO_ENABLE = "disable"
SYSTEMD_SERVICE:${PN} = "lora-demo.service"

FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI += " file://lora-demo.service "


FILES:${PN} += "${systemd_unitdir}/system/lora-demo.service"
HAS_SYSTEMD = "${@bb.utils.contains('DISTRO_FEATURES', 'systemd', 'true', 'false', d)}"
do_install:append() {
    if ${HAS_SYSTEMD}; then
        install -d ${D}/${systemd_unitdir}/system
        install -m 0644 ${WORKDIR}/lora-demo.service ${D}/${systemd_unitdir}/system
    fi
}