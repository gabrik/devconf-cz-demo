FROM eclipse/zenoh:0.7.0-rc

EXPOSE 7447/udp

RUN echo '#!/bin/ash' > /entrypoint.sh
RUN echo 'echo " * Starting: /zenohd $*"' >> /entrypoint.sh
RUN echo 'exec /zenohd --no-multicast-scouting -l udp/0.0.0.0:7447 -l tcp/0.0.0.0:7447' >> /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]