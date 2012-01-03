#!/bin/bash
if [ "$#" -ne 1 ]; then
	echo "Expected one parameter: installation directory (for example: /exp/mvgompel/local/)" >&2
	exit 1
fi
TARGET=$1
cd $TARGET
mkdir src bin etc lib share
cd src
svn co https://ilk.uvt.nl/svn/trunk/sources/Timbl6
cd Timbl6
svn update
bash bootstrap && ./configure --prefix=$TARGET && make && make install
if [ $? -ne 0 ]; then
        echo "Error during installation of Timbl" >&2
        exit 1
fi
cd ..
svn co https://ilk.uvt.nl/svn/trunk/sources/TimblServer
cd TimblServer && svn update
sh bootstrap && ./configure --prefix=$TARGET && make && make install
if [ $? -ne 0 ]; then
        echo "Error during installation of TimblServer" >&2
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
cd ..
svn co https://ilk.uvt.nl/svn/sources/libfolia/trunk libfolia
cd libfolia && svn update
sh bootstrap && ./configure --prefix=$TARGET && make && make install
if [ $? -ne 0 ]; then
        echo "Error during installation of libfolia" >&2
        exit 1
fi
cd ..
svn co https://ilk.uvt.nl/svn/sources/ucto/trunk ucto
cd ucto && svn update
sh bootstrap && ./configure --prefix=$TARGET && make && make install
if [ $? -ne 0 ]; then
        echo "Error during installation of ucto" >&2
        exit 1
fi
cd ..
svn co https://ilk.uvt.nl/svn/sources/Frog/trunk Frog
cd Frog && svn update
sh bootstrap && ./configure --prefix=$TARGET && make && make install
if [ $? -ne 0 ]; then
        echo "Error during installation of Frog" >&2
        exit 1
fi
cd ../..
git clone git://github.com/proycon/pynlpl.git
cd pynlpl && git pull
cd ..
#svn co https://ilk.uvt.nl/svn/trunk/sources/pbmbmt/trunk pbmbmt
#cd pbmbmt && svn update
#ln -s ../pynlpl
#./install-svn.sh
cd ..
echo "All done"

