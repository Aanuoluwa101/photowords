FROM amazonlinux:2023.6.20250203.1

ENV PYTHONUNBUFFERED=1


RUN ulimit -n 2024 && \
    yum update -y && \
    yum install -y python39 python-pip zip && \
    pip install virtualenv && \
    yum clean all


    # RUN ulimit -n 2024 && \
    # yum update -y && \
    # yum install -y python39 python-pip zip && \
    # pip install virtualenv && \
    # yum clean all

    

# docker build -t aws_lambda_builder_image .