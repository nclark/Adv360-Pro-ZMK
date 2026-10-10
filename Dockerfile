FROM docker.io/zmkfirmware/zmk-build-arm:stable

WORKDIR /app

COPY config/west.yml config/west.yml

# West Init
RUN west init -l config
# West Update
RUN west update
# West Zephyr export
RUN west zephyr-export

# Local patches to the Kinesis ZMK fork (see patches/README.md)
COPY patches/ patches/
RUN cd zmk && git apply --verbose ../patches/*.patch

COPY bin/build.sh ./

CMD ["./build.sh"]
