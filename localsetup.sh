#!/bin/bash
TARGET=$1
cd $TARGET
mkdir src bin etc lib share
cd src
svn co https://ilk.uvt.nl/svn/trunk/sources/Timbl6
cd Timbl6
svn update
bash bootstrap && ./configure --prefix=$TARGET && make && make install
if [ $? -ne 0 ]; then
        echo "Error during installation of Timbl"
        exit 1
fi
cd ..
svn co https://ilk.uvt.nl/svn/trunk/sources/TimblServer
cd TimblServer && svn update
sh bootstrap && ./configure --prefix=$TARGET && make && make install
if [ $? -ne 0 ]; then
        echo "Error during installation of TimblServer"
        exit 1
fi
cd ..
svn co https://ilk.uvt.nl/svn/trunk/sources/Mbt3
cd Mbt3 && svn update
sh bootstrap && ./configure --prefix=$TARGET && make && make install
if [ $? -ne 0 ]; then
        echo "Error during installation of Mbt"
        exit 1
fi
svn co https://ilk.uvt.nl/svn/sources/libfolia/
cd libfolia && svn update
sh bootstrap && ./configure --prefix=$TARGET && make && make install
if [ $? -ne 0 ]; then
        echo "Error during installation of libfolia"
        exit 1
fi
cd ..
svn co https://ilk.uvt.nl/svn/sources/ucto/trunk ucto
cd ucto && svn update
sh bootstrap && ./configure --prefix=$TARGET && make && make install
if [ $? -ne 0 ]; then
        echo "Error during installation of ucto"
        exit 1
fi
cd ..
svn co https://ilk.uvt.nl/svn/sources/Frog/trunk Frog
cd Frog && svn update
sh bootstrap && ./configure --prefix=$TARGET && make && make install
if [ $? -ne 0 ]; then
        echo "Error during installation of Frog"
        exit 1
fi
cd ../..
svn co https://ilk.uvt.nl/svn/trunk/sources/pynlpl
cd pynlpl && svn update
cd ..
svn co https://ilk.uvt.nl/svn/trunk/sources/pbmbmt/trunk pbmbmt
cd pbmbmt && svn update
ln -s ../pynlpl
./install-svn.sh
cd ..
echo "All done"

