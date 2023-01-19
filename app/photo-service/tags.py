import grpc
from typing import List
import tags_pb2_grpc, tags_pb2

class TagsClient:
    def __init__(self):
        self.channel = None
        self.stub = None

    def connect(self, service_host):
        self.channel = grpc.insecure_channel(service_host)
        self.stub = tags_pb2_grpc.TagsStub(self.channel)

