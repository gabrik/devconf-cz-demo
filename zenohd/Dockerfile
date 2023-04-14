FROM messense/rust-musl-cross:x86_64-musl as build


# clone zenoh mqtt bridge
RUN git clone https://github.com/eclipse-zenoh/zenoh-plugin-mqtt -b 0.7.0-rc /root/zenoh-plugin-mqtt
RUN echo "1.66.0" > /root/zenoh-plugin-mqtt/rust-toolchain
RUN rustup install 1.66.0
RUN rustup target add --toolchain 1.66.0 x86_64-unknown-linux-musl
RUN cd /root/zenoh-plugin-mqtt && cargo build --release -p zplugin-mqtt


FROM eclipse/zenoh:0.7.0-rc as zenoh-alpine

EXPOSE 7447/udp
EXPOSE 1883/tcp

COPY --from=build /root/zenoh-plugin-mqtt/target/x86_64-unknown-linux-musl/release/libzplugin_mqtt.so /usr/lib
RUN echo '#!/bin/ash' > /entrypoint.sh
RUN echo 'echo " * Starting: /zenohd"' >> /entrypoint.sh
RUN echo 'exec /zenohd -c /config.json5' >> /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]