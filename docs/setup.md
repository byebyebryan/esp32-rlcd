# Development setup from a fresh machine

This repository contains three independent ESP-IDF applications and a shared
panel component. Start with a Linux machine, Bash, a USB-C data cable and the
Waveshare ESP32-S3-RLCD-4.2. The wrapper runs from Bash; interactive activation supports
Bash and Zsh. No other board project, preinstalled ESP-IDF, vendor checkout,
Arduino installation or editor extension is required.

## 1. Install host prerequisites

Install the packages for your distribution. These commands change system
packages and are run once by the workstation owner.

Arch Linux:

```sh
sudo pacman -S --needed base-devel git wget curl unzip gperf python python-pip \
    cmake ninja ccache dfu-util libusb libffi openssl
```

Debian/Ubuntu:

```sh
sudo apt-get update
sudo apt-get install build-essential git wget curl unzip flex bison gperf \
    python3 python3-pip python3-venv cmake ninja-build ccache libffi-dev \
    libssl-dev dfu-util libusb-1.0-0
```

Python must support pip, virtual environments and HTTPS. EIM checks these
prerequisites before installing the SDK. If it reports another missing
package, use [EIM's distribution-specific prerequisite list](https://docs.espressif.com/projects/idf-im-ui/en/latest/prerequisites.html).
The native pixel-packing check additionally uses the host C compiler and its
AddressSanitizer/UndefinedBehaviorSanitizer runtimes, provided by the packages
above. The firmware uses the cross-compiler installed by EIM.

Package lists follow [ESP-IDF v5.5.3's Linux setup guide](https://docs.espressif.com/projects/esp-idf/en/v5.5.3/esp32s3/get-started/linux-macos-setup.html).
macOS users should follow the linked Espressif prerequisites and EIM install
instructions; Linux's serial group and `/dev/serial/by-id` steps differ there.
The repository's setup scripts are not Windows PowerShell scripts.

## 2. Install Espressif's EIM CLI

EIM **0.19.0** is the installer version used for this repository's setup
checks. ESP-IDF itself is pinned independently to **v5.5.3**.

For Linux x86-64, install the official standalone CLI in your user directory:

```sh
mkdir -p "$HOME/.local/bin"
curl --fail --location --output eim-cli-linux-x64.zip \
    https://github.com/espressif/idf-im-ui/releases/download/v0.19.0/eim-cli-linux-x64.zip
unzip eim-cli-linux-x64.zip -d eim-cli
install -m 755 eim-cli/eim "$HOME/.local/bin/eim"
export PATH="$HOME/.local/bin:$PATH"
eim --version
```

Expected: `eim 0.19.0`. Keep `~/.local/bin` in your normal shell's PATH for
future sessions. For another CPU architecture, choose its CLI archive from
the [same official release](https://github.com/espressif/idf-im-ui/releases/tag/v0.19.0).
Distribution packages and Homebrew are also covered in
[Espressif's CLI installation guide](https://docs.espressif.com/projects/idf-im-ui/en/latest/cli_installation.html).
EIM does not need to run with sudo for the user-owned SDK installation below.

## 3. Get the repository and install the SDK

Use a checkout and installation path without spaces, as required by ESP-IDF.

```sh
git clone https://github.com/byebyebryan/esp32-rlcd.git
cd esp32-rlcd
./scripts/setup.sh
./scripts/idf.sh --version
./scripts/idf.sh -C projects/bringup build
./scripts/check-frame.sh
```

Expected IDF version: `ESP-IDF v5.5.3`. The first setup downloads the SDK,
its own Git submodules, toolchains and Python environment. The app repository
has no submodules and needs an ordinary clone.

`scripts/eim-config.toml` pins the SDK release and `esp32s3` target. It enables
ESP-IDF dependency checkout and disables EIM's optional component-registry
prefetch; these applications have no registry-managed dependencies. `setup.sh`
passes explicit SDK, tools, archive, activation and registry paths and checks the
resulting environment. An activation file alone does not prove a complete
installation.

By default, the paths are:

| Item | Location |
| --- | --- |
| ESP-IDF source | `~/.espressif/v5.5.3/esp-idf` |
| Tools and Python environment | `~/.espressif/tools` |
| Activation | `~/.espressif/tools/activate_idf_v5.5.3.sh` |
| Machine-specific EIM config | `~/.espressif/eim_config.toml` |

For a separate installation, use an absolute root and keep it set when
running setup and build commands:

```sh
export EIM_ROOT="$HOME/.local/share/esp32-rlcd-idf"
./scripts/setup.sh
./scripts/idf.sh -C projects/bringup build
```

The wrapper activates the selected toolchain on every invocation, so a fresh
terminal needs no existing `idf.py` function or globally installed esptool.
For interactive `idf.py` in Bash or Zsh:

```sh
. scripts/env.sh
idf.py --version
idf.py -C projects/bringup menuconfig
```

## 4. Configure USB access and select the board

Connect the board with a USB data cable and list stable device paths:

```sh
ls -l /dev/serial/by-id/
```

Unplug/replug the RLCD to identify the entry that changes. Multiple ESP32-S3
boards share the Espressif product name. Use the full by-id path for flashing;
`ttyACM` numbers can change between connections. The local board serial in
[bringup.md](bringup.md) is a recorded device, not a default for every clone.

Set the selected path and inspect its permissions:

```sh
RLCD_PORT='/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_YOUR_BOARD-if00'
ls -l "$(readlink -f "$RLCD_PORT")"
id -nG
```

If your account lacks read/write access, join the device's serial group.
Typical choices from [Espressif's serial guide](https://docs.espressif.com/projects/esp-idf/en/v5.5.3/esp32s3/get-started/establish-serial-connection.html):

```sh
# Arch Linux
sudo usermod -aG uucp "$USER"

# Debian/Ubuntu
sudo usermod -aG dialout "$USER"
```

Use the command appropriate to your distribution, then log out and back in.
Verify the group with `id -nG` in the new session. `setup.sh` does not modify
groups, install system packages or add udev rules. USB-Serial-JTAG uses the
Linux serial driver; an external UART adapter is not needed for this board.

Close any serial monitor or other process holding this specific port, then:

```sh
./scripts/idf.sh -C projects/bringup -p "$RLCD_PORT" flash monitor
```

Flashing replaces the selected board's firmware. Exit the monitor with
**Ctrl+]**. The pattern and expected logs are described in [README.md](../README.md).
No Wi-Fi credentials are needed for the panel test.

## Board configuration and generated files

The root `sdkconfig.defaults` is the shared board configuration used by all
three applications. Each application owns its generated `sdkconfig` and
`build/` directory. The benchmark also applies
`projects/render-bench/sdkconfig.defaults` for its workload-specific settings.
Existing ignored root or former example output files are historical local
artifacts; selecting a project with `-C` keeps current builds in that project's
directory.

The shared board configuration is:

| Setting | Value |
| --- | --- |
| Target | ESP32-S3 |
| Flash | 16 MiB |
| CPU | 240 MHz |
| PSRAM | Octal, 80 MHz, startup memory test enabled |
| Console | USB-Serial-JTAG |

Panel GPIOs, 10 MHz SPI3 and 400 x 300 landscape packing are defined in the
panel component and documented in [board.md](board.md). There is no backlight
configuration. The default IDF partition table has a single 1 MiB app partition;
the initial panel test fits it. Additional flash capacity is available for
future partition changes.

`menuconfig` changes the selected application's local configuration. To make a
setting reproducible, review and put the intended option in the root
`sdkconfig.defaults` or the benchmark's project override. Defaults seed a fresh
config; they do not overwrite existing local choices. To rebuild the bring-up
app from its defaults while preserving the old config:

```sh
mv projects/bringup/sdkconfig projects/bringup/sdkconfig.old
./scripts/idf.sh -C projects/bringup fullclean
./scripts/idf.sh -C projects/bringup build
```

Run the `mv` only when that project has a local `sdkconfig`. Preserve any local
evidence under `projects/bringup/build/` before `fullclean`. A new clone already
starts from defaults; an additional `set-target` command is unnecessary
because the defaults select `esp32s3`.

## Troubleshooting

| Symptom | Check or recovery |
| --- | --- |
| `eim not found` | Install the CLI and add its directory to PATH; check `eim --version` |
| Activation or Python environment is incomplete | Install missing prerequisites; rerun setup with a new empty `EIM_ROOT`, or use EIM's repair workflow below |
| Wrong SDK version | Use the v5.5.3 installation; activation validates the release and required files |
| USB port is absent | Check power, a data-capable cable and the board's PWR button; try another cable/USB port |
| `Permission denied` | Check the actual device group and log in again after joining it |
| Port busy | Exit monitors and inspect the process using this device; avoid resetting other connected boards |
| Cannot enter download mode | Follow the RLCD-specific BOOT/PWR procedure in [Waveshare's guide](https://docs.waveshare.com/ESP32-S3-RLCD-4.2) |
| Screen is hard to see | Use adequate ambient light; the panel is reflective |

EIM provides `eim fix` for repairing an existing installation. Consult
[`eim fix --help` and the official CLI reference](https://docs.espressif.com/projects/idf-im-ui/en/latest/cli_commands.html)
for the installed version. Use an explicit installation path when repairing
a shared toolchain. For an isolated project installation, selecting a new
empty `EIM_ROOT` is also a supported recovery path.

## Setup validation

On 2026-10-02, EIM 0.19.0 installed a fresh v5.5.3 SDK, its dependencies,
toolchains and Python environment under an isolated root on Starship. A copy
of this checkout with no local `sdkconfig` or build directory built successfully
using that installation. Generated board settings matched the shared defaults;
reusing the installation and the native pixel-packing check also passed.

Failure checks covered missing EIM, incomplete activation, a wrong SDK version
and an installer error. The host prerequisites were already present; the
package commands above were checked against Espressif's documentation.
This was a setup/build check; the running board's accepted firmware was retained.

[Validation summary and build inputs](evidence/2026-10-02-bootstrap/summary.json),
[installation excerpt](evidence/2026-10-02-bootstrap/fresh-install-tail.log),
[build excerpt](evidence/2026-10-02-bootstrap/clean-build-tail.log), and
[native check](evidence/2026-10-02-bootstrap/native-test.log).
