#!/bin/bash

echo create revisionfile...

revdest="revisionfile.py"

mod=1
dif=$(git diff --shortstat)

if [ "$dif" == "" ] 
then
  mod=0
else
 echo repo modified!
fi

if [ "$BUILD_NUMBER" == "" ] ;then
 BUILD_NUMBER=0
fi

echo '"""' > $revdest
echo "  version info to be changed by build script" >>$revdest
echo '"""'   >>$revdest

git log -n 1  --format=format:"revision= '%h'%n" >> $revdest
echo buildnumber= \'$BUILD_NUMBER\' >> $revdest

echo "# eof"  >>$revdest

echo done.
# eof
