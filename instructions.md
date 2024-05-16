# Lora Basics Station on STM32MP157DK
Initially I could not get the basicstation to cross compile for the target platform. This may be due to my unfamiliarity with the format of setup.gmk.
Also could not compile on the Kirkstone build from the lora demo Python app layer project, but was hardware-limited at the time and didn't want to corrupt the working build I had.

Succeeded in compiling basicstation on a Dunfell build which will run on a HAL-patched Kirkstone.


## Create Environment

These instructions should enable a working system to be created. I was not certain exactly what was happening in the ST LoRaWAN/Chirpstack build that was facilitating the RAK5146 to hook up so stripped that build to get here - undoubtedly it would be more efficient to create a discrete build that facilitates simple installation but this is an analogue of how the working build was initially achieved.

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

append build tools to Yocto build:

```bash
./build-openstlinuxweston-stm32mp1/conf/bblayers.conf
EXTRA_IMAGE_FEATURES += " tools-sdk tools-debug debug-tweaks"
IMAGE_INSTALL:append = "git"


make build
```
this will take a while as this is the initial build.

flash device


## Compile lora basics station on host

apt get install git?

Obtain and compile basicstation: following https://doc.sm.tc/station/compile.html
```bash
$git clone https://github.com/lorabasics/basicstation.git
```

RAK5146 is in theory CoreCell compliant - I chose to separate the build at the stage I discovered that it wasn't:
 
create symlink to arm-ostl-linux-gnueabi-gcc - (/usr ?)
```bash
$ln -s [path]  ~/toolchain-stm32
```

edit ./setup.gmk echoing corecell setup for RAK5146 on stm32 platform:
```bash
ARCH.stm32 = arm-ostl-linux-gnueabi      
CFG.stm32 = linux lgw1 no_leds sx1302 
DEPS.stm32 = mbedtls lgw1302
CFLAGS.stm32.debug = -g O0
LIBS.stm32 = -llgw1302  ${MBEDLIBS}      -lpthread -lrt

$make platform=stm32 variant=std
$make platform=stm32 variant=debug
```
## Configure Concentrator

### Set up STM32 gateway and Nucleo WL55, Astra1B at IOTC

See https://docs.iotconnect.io/iotconnect/user-manuals/devices/device/lorawan/

get and save certs and trust chain

### Set up local instance
create and cd to ~/basicstation/projects/iotc
Get startup script:
```bash
$cp ../../examples/corecell/start-station.sh ./
$sed -i 's/corecell/stm32/g' start-station.sh
```
create reset using libgpiod instead of deprecated /sys/class/gpio interface

edit `./concentrator-reset.sh`:
```bash
#!/bin/bash

#echo "Reset GPIO17/PG8 on STM32MP1"
gpioset gpiochip6 8=1
sleep 0.1
#echo "set to 1"
gpioset gpiochip6 8=0
#echo "set to 0"
sleep 0.1
gpioget gpiochip6 8
sleep 0.5
```
create wrapper for init (called by start-station.sh)
```bash
$vi ./rinit.sh

#!/bin/bash
:./concentrator-reset.sh

$:wq
```

### Configure LNS

```bash
$mkdir lns-iotc
$cd lns-iotc
$cp ../../examples/corecell/lns-ttn/station.conf ./
```
#### set pulse per second true to somewhat mitigate clock drifts

in `"SX1302_conf":{}` add:
```bash
"pps": true, 
```
import certs from IOTC<br>
in `tc.uri` put wss:// websockets url from iotc<br>
in `cups.uri` put https:// cups url from iotc<br>

get cups archive from iotc
```
$mv certificate.pem.crt cups.crt
$mv private.key cups.key
```

you should have: 
```bash
	station.conf
	cups.crt
	cups.key
	cups.trust
	cups.uri
	tc.crt
	tc.key
	tc.trust
	tc.uri
```
## Run The Station

```bash
$ ssh root@stm32mp1.local
$ screen
$ cd basicstation/projects/iotc/
$ ./start-station.sh -l lns-iotc
```
check connection at IOTC

power up end nodes Nucleo WL55, Astra1b

check telemetry at IOTC

return to terminal and detach from screen session:<br>
ctrl + a<br>
ctrl + d<br>
`$ exit`


The Nucleo WL55 has been successfully connected and stayed online<br>
The Astra1b has not stayed connected for more than a half hour so far - however there have been issues raised with Softweb support fairly regularly and this might be due to ongoing back end adjustments.

## Notes
Set up a TTN account to test/compare connectivity.<br>
The Nucleowl1 was set to LoRaWAN spec 1.0.4 with RP002 Regional Parameters 1.0.1<br>
The Astra was set to the LoraWAN spec 1.0.2 with RP001 Regional Parameters 1.0.2<br>
This was unexpected - when setting up with Chirpstack the same device profile was used for both devices - LoRaWAN spec 1.0.4, RP002 Regional Parameters 1.0.1

Otherwise the setup was fairly simple: the data was retrieved in CayenneLPP format and both devices reported successfully 
