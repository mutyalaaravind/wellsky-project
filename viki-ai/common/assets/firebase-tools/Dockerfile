# Reason why we build this ourselves: https://github.com/firebase/firebase-tools/issues/5256#issuecomment-1383228506
# PR: https://github.com/AndreySenov/firebase-tools-docker/pull/37

# Even worse: https://github.com/firebase/firebase-tools/issues/5614#issuecomment-1508515106
# Every day, we stray further from God.
# Seriously, remember the times when you could just compile the app and run it?
# Now we've got Docker and stuff, and even though I love Docker, it still isolates the problems
# instead of solving them. That's our best bet in the world of shitty software. And we're the ones to blame.

FROM node:18.15-slim
ARG BUILD_DATE
ARG VERSION
ARG VCS_REF
LABEL org.label-schema.schema-version="1.0" \
      org.label-schema.name="firebase-tools" \
      org.label-schema.version=${VERSION} \
      org.label-schema.build-date=${BUILD_DATE} \
      org.label-schema.description="Firebase CLI on the NodeJS image" \
      org.label-schema.url="https://github.com/firebase/firebase-tools/" \
      org.label-schema.vcs-url="https://github.com/AndreySenov/firebase-tools-docker/" \
      org.label-schema.vcs-ref=${VCS_REF}
ENV FIREBASE_TOOLS_VERSION=${VERSION}
ENV HOME=/home/node
EXPOSE 4000
EXPOSE 5000
EXPOSE 5001
EXPOSE 8080
EXPOSE 8085
EXPOSE 9000
EXPOSE 9005
EXPOSE 9099
EXPOSE 9199
EXPOSE 9299
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y openjdk-11-jre bash && \
    yarn global add firebase-tools@${VERSION} && \
    yarn cache clean && \
    firebase setup:emulators:database && \
    firebase setup:emulators:firestore && \
    firebase setup:emulators:pubsub && \
    firebase setup:emulators:storage && \
    firebase -V && \
    java -version && \
    chown -R node:node $HOME && \
    apt-get install -y curl lsof && \
    apt-get clean
USER node
VOLUME $HOME/.cache
WORKDIR $HOME
CMD ["sh"]
