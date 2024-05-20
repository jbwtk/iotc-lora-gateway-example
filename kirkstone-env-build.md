
### Build patched Kirkstone Yocto image:
```bash
mkdir iotconnect-stm32mp17-kirkstone
cd iotconnect-stm32mp17-kirkstone

repo init -u https://github.com/STMicroelectronics/oe-manifest.git -b refs/tags/openstlinux-5.15-yocto-kirkstone-mp1-v23.07.26
repo sync    

wget https://raw.githubusercontent.com/avnet-iotconnect/iotc-lora-gateway-example/master/Makefile
wget https://raw.githubusercontent.com/avnet-iotconnect/iotc-lora-gateway-example/master/Dockerfile

git clone git@github.com:avnet-iotconnect/iotc-lora-gateway-example.git -b master ./layers/iotconnect-lora-demo
cd ./layers/iotconnect-lora-demo
git submodule update --init
cd -

make docker

DISTRO=openstlinux-weston MACHINE=stm32mp1 source layers/meta-st/scripts/envsetup.sh
#### go through all of the EULA and accept everything

exit

make env
bitbake-layers add-layer ../layers/iotconnect-lora-demo/meta-st-stm32mpu-app-lorawan/
exit
```

At this point we have the kirkstone source and patches. 

Before build we take out the chirpstack and application stuff as all we actually want it for is patch HAL with necessary bits from ST Chirpstack layer to emulate temperature sensor missing from RAK5146

Remove `meta-iotconnect-lora-demo/` from `./layers/iotconnect-lora-demo`

Remove `recipes-framework` and `recipes-st` from `./layers/iotconnect-lora-demo/meta-st-stm32mpu-app-lorawan/`

Remove or comment out all the `IMAGE_INSTALL:append` content in `./layers/iotconnect-lora-demo/meta-st-stm32mpu-app-lorawan/conf/layer.conf`

append build tools in `./build-openstlinuxweston-stm32mp1/conf/bblayers.conf`
```bash
EXTRA_IMAGE_FEATURES += " tools-sdk tools-debug debug-tweaks"
IMAGE_INSTALL:append = "git"
```
These tools are large and the default maximum filesystem size must be increased:<br>
edit `STM32MP_ROOTFS_MAXSIZE_NAND` in `./layers/meta-st/meta-st-stm32mp/conf/machine/include/st-machine-common-stm32mp.inc` replacing 753664 with a larger number (>800000 ... 1232896?)

Now you can build:
```bash
make build
```
this will take a while as this is the initial build.

### flash device
https://wiki.st.com/stm32mpu-ecosystem-v3/wiki/STM32MP1_Distribution_Package#Flashing_the_built_image

```bash
STM32_Programmer_CLI -c port=usb1 -w flashlayout_st-image-weston/trusted/FlashLayout_sdcard_stm32mp157c-dk2-trusted.tsv
```
or `make flash`
