#!/bin/bash

#    Install everything automatically.
#    You must first install https://github.com/Pelochus/ezrknpu

# Change to your paths here if necessary.
# This should be correct if you installed ezrknpu on Ubuntu.
sharedlib='/usr/lib/librkllmrt.so'
libs='/usr/lib'

# Check if user is running this as sudoer.
if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root (sudo)"
    exit 1
fi

# Check existence of rkllm shared library, exit if not found.
if [ -f "$sharedlib" ]; then
    echo "File exists: $sharedlib"
else
    echo "Error: $sharedlib does not exist." >&2
    echo "Please install https://github.com/Pelochus/ezrknpu or if it is installed, then please change the path of librkllmrt.so in this script." >&2
    exit 1
fi

# Install dependencies if not already installed.
echo "Checking dependencies..."
if ! dpkg -s libboost-all-dev libcpprest-dev &> /dev/null; then
    echo "Installing dependencies..."
    sudo apt install -y libboost-all-dev libcpprest-dev
    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies" >&2
        exit 1
    fi
    echo "Dependencies installed successfully"
else
    echo "Dependencies already installed"
fi

# Create boost test file.
echo "Creating boost test file..."
cat << EOF > boost_version.cpp
#include <iostream>
#include <boost/version.hpp>

int main() {
    std::cout << "Using Boost " << BOOST_VERSION / 100000 << "."  // major version
              << BOOST_VERSION / 100 % 1000 << "."  // minor version
              << BOOST_VERSION % 100  // patch level
              << std::endl;
    return 0;
}
EOF

# Compile test file.
echo "Compiling test file..."
g++ boost_version.cpp -o boost_version
if [ $? -ne 0 ]; then
    echo "Compilation failed!" >&2
    exit 1
fi

# Test boost.
echo "Running boost test file..."
boostversion=$(./boost_version)
if [[ "${boostversion:0:11}" == "Using Boost" ]]; then
    echo "Boost test completed successfully!"
else
    echo "Boost test failed." >&2
    exit 1
fi

# Fetch the server script.
echo "Downloading the server source..."
curl https://raw.githubusercontent.com/av1d/rk3588_npu_llm_server/main/server.cpp --output server.cpp
if [ $? -ne 0 ]; then
    echo "Failed to download server source" >&2
    exit 1
fi

# Build the server. Assumes libs are in /usr/lib. Change if needed.
echo "Compiling server..."
g++ server.cpp -o server -std=c++11 -lcpprest -lcrypto -L${libs} -lrkllmrt
if [ $? -ne 0 ]; then
    echo "Compilation failed!" >&2
    echo "removing temporary files..."
    rm -f server.cpp
    exit 1
fi

# Clean up temporary file.
echo "removing temporary files..."
rm -f server.cpp

# Success:
echo "Compilation successful!"
echo "You can now start the server with something like:"
echo "./server 192.168.0.196 31337 ../qwen-1_8B-rk3588/qwen-chat-1_8B.rkllm"
echo "./server [ip] [port] [model_path]"
