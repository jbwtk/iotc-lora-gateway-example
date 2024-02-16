LICENSE = "GPL-3.0-only"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/GPL-3.0-only;md5=c79ff39f19dfec6d293b95dea7b07891"

RDEPENDS:${PN} += " bash"

RDEPENDS:${PN} += " python3-pip"

RDEPENDS:${PN} += " python3-iotconnect-sdk"

RDEPENDS:${PN} += " python3-cachetools"               
RDEPENDS:${PN} += " python3-certifi"                  
RDEPENDS:${PN} += " python3-charset-normalizer"      
RDEPENDS:${PN} += " python3-chirpstack-api"           
RDEPENDS:${PN} += " python3-google-api-core"          
RDEPENDS:${PN} += " python3-google-auth"              
RDEPENDS:${PN} += " python3-googleapis-common-protos" 
RDEPENDS:${PN} += " python3-grpcio"                   
RDEPENDS:${PN} += " python3-idna"                     
RDEPENDS:${PN} += " python3-ntplib"                   
RDEPENDS:${PN} += " python3-paho-mqtt"                
RDEPENDS:${PN} += " python3-protobuf"                 
RDEPENDS:${PN} += " python3-pyasn1"                   
RDEPENDS:${PN} += " python3-pyasn1-modules"           
RDEPENDS:${PN} += " python3-requests"                 
RDEPENDS:${PN} += " python3-rsa"                      
RDEPENDS:${PN} += " python3-urllib3"                 

SRC_URI += " file://lora_demo.py"
SRC_URI += " file://local_settings.py"
SRC_URI += " file://models"
SRC_URI += " file://helpers"


APP_INSTALL_DIR = "${base_prefix}/usr/bin/local/iotc"
PRIVATE_DATA_DIR = "${base_prefix}/usr/local/iotc"

do_install() {
    install -d ${D}${APP_INSTALL_DIR}
    for f in ${WORKDIR}/models/*
    do
        if [ -f $f ]; then
            if [ ! -d ${D}${APP_INSTALL_DIR}/models ]; then
                install -d ${D}${APP_INSTALL_DIR}/models
            fi
            install -m 0755 $f ${D}${APP_INSTALL_DIR}/models/
        fi
    done

    for f in ${WORKDIR}/helpers/*
    do
        if [ -f $f ]; then
            if [ ! -d ${D}${APP_INSTALL_DIR}/helpers ]; then
                install -d ${D}${APP_INSTALL_DIR}/helpers
            fi
            install -m 0755 $f ${D}${APP_INSTALL_DIR}/helpers/
        fi
    done

    install -m 0755 ${WORKDIR}/lora_demo.py ${D}${APP_INSTALL_DIR}/
    install -m 0755 ${WORKDIR}/local_settings.py ${D}${APP_INSTALL_DIR}/



}


