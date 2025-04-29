yum update -y
yum groupinstall "Development Tools" -y
yum install gcc openssl-devel bzip2-devel libffi-devel -y
yum install -y wget
wget https://www.python.org/ftp/python/3.13.0/Python-3.13.0.tgz
tar -xzf Python-3.13.0.tgz
cd Python-3.13.0
./configure --enable-optimizations



sudo yum update -y
sudo yum groupinstall -y "Development Tools"
sudo yum install -y openssl-devel bzip2-devel libffi-devel zlib-devel wget make
cd /usr/src
tar xzf Python-3.12.0.tgz
cd Python-3.12.0
./configure --enable-optimizations