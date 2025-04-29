virtualenv --python=/usr/bin/python3.9 python 
source python/bin/activate 
pip install -r requirements.txt -t python/lib/python3.9/site-packages
cp /redis_client.py python/redis_client.py

zip -r9 python.zip python 
echo "PYTHON VERSION IS $(python3 --version)"



    
# python3.9 -m venv /opt/venv
# cp requirements.txt /opt/
# /opt/venv/bin/pip install --upgrade pip
# /opt/venv/bin/pip install -r /opt/requirements.txt --target /opt/python
# zip -r python.zip /opt/python