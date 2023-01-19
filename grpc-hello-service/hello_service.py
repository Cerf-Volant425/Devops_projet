
from concurrent import futures
import logging

import grpc

import hello_pb2
import hello_pb2_grpc

class Hello(hello_pb2_grpc.HelloServicer):

    def sayHello(self, request, context):
        return hello_pb2.HelloReply(message='Hello, %s!' % request.name)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    hello_pb2_grpc.add_HelloServicer_to_server(Hello(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()
