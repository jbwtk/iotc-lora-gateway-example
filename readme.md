## Build Instructions

These instructions leverage the power of Docker to create a reproducible build that works across different OS environments, one of the main ideas is to avoid problems caused by having a too old/new version of Linux being used the Yocto build system, as those can cause build failures.

Provided are both the `Dockerfile` and `Makefile` to simplify the build process.

This guide is based off [How to integrate LoRaWAN gateway](https://wiki.st.com/stm32mpu-ecosystem-v3/wiki/How_to_integrate_LoRaWAN_gateway#How_to_run_the_ChirpStack_application_on_STM32MP157x-DKx_Discovery_kit)

The "metaphor" that reflects the LoRaWan entities against IOTConnect is simplistic; it creates an IOTC Gateway instance to represent a single gateway/concentrator on the Chirpstack LNS, with all the LoRaWan nodes as child devices of this entity. This should satisfy 80% of use cases.

Tested on Ubuntu 20.04, 22.04

### Requirements
- Repo tool (from Google) - https://android.googlesource.com/tools/repo
- Docker - https://docs.docker.com/engine/install/ubuntu/ + https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user
- git name and email added to global scope
- STM32_Programmer_CLI - similar steps to [this](https://wiki.somlabs.com/index.php/Installing_STM32CubeProgrammer_on_Ubuntu_18.04) but use the latest release

### Method
1. Create a work directory, for example ~/work
```bash
cd ~/work
```

2. Create project directory and enter it
```bash
mkdir iotconnect-stm32mp17-kirkstone && cd iotconnect-stm32mp17-kirkstone
```

3. Use repo tool to get the yocto sources
```bash
repo init -u https://github.com/STMicroelectronics/oe-manifest.git -b refs/tags/openstlinux-5.15-yocto-kirkstone-mp1-v23.07.26 && repo sync    
```

4. wget provided Makefile and Dockerfile to project directory and execute these commands in the terminal
```bash
wget https://raw.githubusercontent.com/akarnil/iotconnect-lora-demo/master/Makefile && \
wget https://raw.githubusercontent.com/akarnil/iotconnect-lora-demo/master/Dockerfile

git clone git@github.com:akarnil/iotconnect-lora-demo.git -b master ./layers/iotconnect-lora-demo
cd ./layers/iotconnect-lora-demo
git submodule update --init
cd -

make docker

DISTRO=openstlinux-weston MACHINE=stm32mp1 source layers/meta-st/scripts/envsetup.sh
### go through all of the EULA and accept everything

exit

make env
bitbake-layers add-layer ../layers/iotconnect-lora-demo/meta-iotconnect-lora-demo/
bitbake-layers add-layer ../layers/iotconnect-lora-demo/meta-st-stm32mpu-app-lorawan/

exit

make build
### this will take a while as this is the initial build.
```

5. Continue from Step 7 of [How to integrate LoRaWAN gateway](https://wiki.st.com/stm32mpu-ecosystem-v3/wiki/How_to_integrate_LoRaWAN_gateway#Software_setup) to prepare the board for flashing, you can use the `make flash` target to simplifiy the process instead.

6. Continue through ST's tutorial to set up the LNS, the gateway and connect your devices in chirpstack.
Once all of that is done, create a Global API key within chirpstack's interface and save it for further use.

7. Via `ssh` or `serial` access the `STM32MP157` and modify the `local_settings.py` file

(use a text editor of choice, nano is also available)

```bash
vi /usr/bin/local/iotc/local_settings.py
```

#### Chirpstack connection:

replace the truncated value for `chirpstack_api_token` with the global API key you just created.

#### Template and device creation:

If you have credentials for the IOTConnect template/device API, uncomment the `iotc_config` section.

Replace the values in `iotc_config` (`company_name, solution_key, company_guid`) with the correct values for your account.

This will automatically create and update the template and gateway device instance on IOTC as the lora nodes provide telemetry.

If you do not have these credentials, a template json file (`./template[Unique ID].json`) will be written to the filesystem. 

As the lora nodes provide telemetry this will be updated, and can be uploaded to the IOTC portal.

The template will be complete once all nodes have updated their attributes.

It may be necessary to edit this file with e.g. the correct value for auth_type, which defaults to 1.

If you have not yet created the template and device instance on the IOTConnect back end, it is straightforward to save the file and run the application to build the template json file and upload it before setting credentials for the SDK client.

#### IOTConnect connection:

Replace the truncated value for `sid` with the correct value from IOTConnect, and make sure the values of `cpid` and `env` are correct for your account.

Make sure you save your changes with `!wq`

8. To launch the application execute
```bash
./usr/bin/local/iotc/lora_demo.py 
```
the terminal multiplexer `screen` is installed.

### Notes

- This setup has been tested with the `RAK5146 SPI with GPS` variant as well as the `RAK5146 USB with GPS`, which will need to be explicitly selected during `chirpstack` configuration.

### Extras

- To flash
```bash
make flash
```

- Use the `systemd` service so the IoTConnect application executes on boot
```bash
systemctl enable lora-demo.service
systemctl start lora-demo.service
```

- To watch the logs use
```bash
journalctl -fu lora-demo
```


