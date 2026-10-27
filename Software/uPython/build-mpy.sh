#!/bin/bash
# compile micropython modules to .mpy into folder mpy/
#
# usage: ./build-mpy.sh [module.py ...]
#   without arguments all default modules are compiled
#
# env:
#   MPY_CROSS  mpy-cross binary (default: mpy-cross)
#   MPY_OPT    optimisation level 0..3 (default: 0)
#   MPY_ARCH   -march value for native code, e.g. armv7emsp, xtensawin (default: none)

cd "$(dirname "$0")" || exit 1

MPY_CROSS=${MPY_CROSS:-mpy-cross}
MPY_OPT=${MPY_OPT:-0}
outdir="mpy"

# boot.py and main.py stay plain .py on the board
modules="gwxctrl.py comu.py HYT221.py windsensor.py timer.py watertable.py hwspec.py revisionfile.py"

if [ $# -gt 0 ] ;then
  modules="$*"
fi

if ! command -v "$MPY_CROSS" >/dev/null ;then
  echo "$MPY_CROSS not found, install with: pip install mpy-cross==1.19.1"
  exit 1
fi

echo "using $($MPY_CROSS --version)"

./updateVersionInfo.sh || exit 1

mkdir -p $outdir

opts="-O$MPY_OPT"
if [ "$MPY_ARCH" != "" ] ;then
  opts="$opts -march=$MPY_ARCH"
fi

err=0
for src in $modules ;do
  dst="$outdir/$(basename "${src%.py}").mpy"
  echo "  $src -> $dst"
  if ! $MPY_CROSS $opts "$src" -o "$dst" ;then
    err=1
  fi
done

if [ $err -ne 0 ] ;then
  echo failed!
  exit 1
fi

echo done.
