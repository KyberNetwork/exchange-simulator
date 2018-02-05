FROM golang

LABEL Name=kyber_dev_chain_wrapper Version=0.0.1

# Copy the local package files to the container's workspace.
ADD . /go/src/github.com/KyberNetwork/wrapper

# Build the outyet command inside the container.
# (You may fetch or manage dependencies here,
# either manually or with a tool like "godep".)
RUN go install github.com/KyberNetwork/wrapper

# Run the outyet command by default when the container starts.
ENTRYPOINT /go/bin/wrapper

# Document that the service listens on port 8080.
# EXPOSE 8540