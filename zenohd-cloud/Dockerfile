FROM messense/rust-musl-cross:x86_64-musl as build


# clone zenoh mqtt bridge
RUN git clone https://github.com/eclipse-zenoh/zenoh-backend-influxdb -b 0.7.0-rc /root/zenoh-backend-influxdb
RUN echo "1.66.0" > /root/zenoh-backend-influxdb/rust-toolchain
RUN rustup install 1.66.0
RUN rustup target add --toolchain 1.66.0 x86_64-unknown-linux-musl
RUN cd /root/zenoh-backend-influxdb && cargo build --release


FROM eclipse/zenoh:0.7.0-rc as zenoh-alpine

EXPOSE 7447/udp
EXPOSE 1883/tcp

COPY --from=build /root/zenoh-backend-influxdb/target/x86_64-unknown-linux-musl/release/*.so /usr/lib
RUN echo '#!/bin/ash' > /entrypoint.sh
RUN echo 'echo " * Starting: /zenohd"' >> /entrypoint.sh
RUN echo 'exec /zenohd -c /config.json5' >> /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]