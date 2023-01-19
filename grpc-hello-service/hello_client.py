
from __future__ import print_function
import logging

import grpc

import hello_pb2
import hello_pb2_grpc


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = hello_pb2_grpc.HelloStub(channel)
        response = stub.sayHello(hello_pb2.HelloRequest(name='you'))
    print("Hello client received: " + response.message)

if __name__ == '__main__':
    logging.basicConfig()
    run()
