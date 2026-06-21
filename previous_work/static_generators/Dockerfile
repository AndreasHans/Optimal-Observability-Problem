FROM python:3.13.7-bookworm

RUN apt-get update && apt-get -y upgrade
RUN apt -y install make gcc g++ default-jdk git
# Z3 4.12 can't build wheel, get 4.13+ or latest
RUN pip3 install z3-solver importlib-resources
RUN git clone https://github.com/prismmodelchecker/prism.git
RUN cd prism/prism && make && make test
RUN cp /prism/prism/bin/prism /bin/
RUN git clone https://github.com/alyziakonsta/Optimal-Observability-Problem.git
RUN cp -a /Optimal-Observability-Problem/. /


