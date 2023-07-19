FROM kbase/sdkpython:3.8.0
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

RUN apt-get update && apt-get -y upgrade \
  && apt-get install -y --no-install-recommends \
    git \
    wget \
    g++ \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*



RUN rm /bin/sh && ln -s /bin/bash /bin/sh
RUN conda create -n py39 python=3.9 \
    && source activate py39 \
    && conda install nose jinja2 \
    && pip3 install jsonrpcbase numpy pandas biopython \
    && pip3 install coverage


WORKDIR /tmp

RUN apt-get update && \
    apt-get -y install apt-transport-https gnupg

RUN wget http://dl.secondarymetabolites.org/antismash-stretch.list -O /etc/apt/sources.list.d/antismash.list && \
    wget -q -O- http://dl.secondarymetabolites.org/antismash.asc | apt-key add -

RUN apt-get update && \
    apt-get -y install hmmer2 hmmer diamond-aligner fasttree prodigal ncbi-blast+ muscle glimmerhmm




#RUN wget --quiet https://github.com/bbuchfink/diamond/releases/download/v2.0.9/diamond-linux64.tar.gz && \
#    tar -zxf diamond-linux64.tar.gz diamond && \
#    mv diamond /usr/bin/diamond && \
#    diamond version


RUN wget https://dl.secondarymetabolites.org/releases/7.0.0/antismash-7.0.0.tar.gz  \
      && tar -zxf antismash-7.0.0.tar.gz 

RUN source activate py39 && pip install ./antismash-7.0.0
RUN source activate py39 && download-antismash-databases && antismash --check-prereqs





#RUN  wget https://dl.secondarymetabolites.org/antismash-stretch.list -O /etc/apt/sources.list.d/antismash.list
#RUN  wget -q -O- https://dl.secondarymetabolites.org/antismash.asc | sudo apt-key add -
#RUN  apt-get update
#RUN apt-get install -y  hmmer2 hmmer  fasttree prodigal ncbi-blast+ muscle glimmerhmm
#RUN wget --quiet https://github.com/bbuchfink/diamond/releases/download/v2.0.9/diamond-linux64.tar.gz && \
#    tar -zxf diamond-linux64.tar.gz diamond && \
#    mv diamond /usr/bin/diamond && \
#    diamond version

#WORKDIR /tmp
#RUN wget https://dl.secondarymetabolites.org/releases/6.0.0/antismash-6.0.0.tar.gz && tar -zxf antismash-6.0.0.tar.gz 

#RUN sed -i 's/biopython >=1.78/biopython==1.76/' antismash-6.0.0/setup.py
#RUN sed -i 's/jinja2/jinja2==3.0.0/' antismash-6.0.0/setup.py

#RUN source activate py39 && pip install ./antismash-6.0.0
#RUN source activate py39 && download-antismash-databases


RUN pip install pandas
#===========


COPY . /kb/module


RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
