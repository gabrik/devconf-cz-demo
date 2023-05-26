FROM ubuntu:focal as build

# first let's build the runtime, the python binding and the python api
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install git python3-venv python3-pip equivs musl-tools build-essential devscripts debhelper pkg-config dpkg-dev equivs libpython3-dev python-is-python3 python3-distutils -y

# install rust
RUN curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- --default-toolchain 1.66.0 -y

# clone zenoh-flow runtime and zenoh-flow-python repos
RUN git clone https://github.com/gabrik/zenoh-flow-runtime -b dev-demo /root/zenoh-flow-runtime
RUN git clone https://github.com/eclipse-zenoh/zenoh-flow-python /root/zenoh-flow-python

#-b feat-typed-inputs-outputs

# build zenoh-flow-runtime
RUN bash -c "source /root/.cargo/env && cd /root/zenoh-flow-runtime && cargo build --release --all-targets"

# build zenoh-flow-python
RUN bash -c "source /root/.cargo/env && cd /root/zenoh-flow-python && cargo build --release --all-targets"

# python api build
FROM quay.io/pypa/manylinux2014_x86_64 as manylinuxbuild

RUN curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- --default-toolchain 1.66.0 -y

RUN git clone https://github.com/eclipse-zenoh/zenoh-flow-python /root/zenoh-flow-python
#-b feat-typed-inputs-outputs

# build zenoh-flow-python apis
RUN bash -c "source /root/.cargo/env && cd /root/zenoh-flow-python && python3.7 -m venv venv && source venv/bin/activate && cd zenoh-flow-python && pip3 install -r requirements-dev.txt && maturin build --release --compatibility manylinux2014"

# build stunt wheel
RUN git clone https://github.com/ZettaScaleLabs/STUNT
RUN cd STUNT/stunt-python && python3.7 setup.py bdist_wheel


FROM ubuntu:focal as data-processing
LABEL authors="Gabriele Baldoni"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install python3 python3-distutils curl libpython3-dev -y

RUN curl --proto "=https" --tlsv1.2 -sSf https://bootstrap.pypa.io/get-pip.py | python3

# Where configuration will reside
RUN mkdir -p /etc/zenoh-flow

# where python wrapper will reside
RUN mkdir -p /var/zenoh-flow/python/

# copy zenoh-flow runtime zenoh configuration and wrappers configuration
COPY etc/zenoh-runtime.json /etc/zenoh-flow/zenoh-runtime.json
COPY etc/py-loader.yaml /etc/zenoh-flow/py-loader.yaml

# exposing volumes
VOLUME ["/var/zenoh-flow/flows"]
VOLUME ["/var/zenoh-flow/nodes"]
VOLUME ["/etc/zenoh-flow"]

# copy the runtime into bin
COPY --from=build /root/zenoh-flow-runtime/target/release/runtime /usr/local/bin

# copy python wrappers
COPY --from=build /root/zenoh-flow-python/target/release/lib*.so /var/zenoh-flow/python/

# copy python api and stunt
COPY --from=manylinuxbuild /root/zenoh-flow-python/target/wheels/*.whl /root/
COPY --from=manylinuxbuild /STUNT/stunt-python/dist/*.whl /root/

RUN bash -c "pip3 install /root/*.whl"

RUN  DEBIAN_FRONTEND=noninteractive apt clean && apt autoclean

CMD bash -c "runtime -z /etc/zenoh-flow/zenoh-runtime.json -l /etc/zenoh-flow/py-loader.yaml -r processing -g /var/zenoh-flow/flows/distance-alert.yml"