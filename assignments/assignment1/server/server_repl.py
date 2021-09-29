from concurrent import futures
import logging
import grpc
import replicator_pb2
import replicator_pb2_grpc
import json
from pymongo import MongoClient
from configparser import ConfigParser

class Replicator(replicator_pb2_grpc.ReplicatorServicer):

    def ReplicateInMongoDB(self, request, context):

        config_object = ConfigParser()
        config_object.read("server_config.ini")
        dbinfo = config_object["MONGODB"]

        client = MongoClient(dbinfo["connectionstring"])

        db = client.college
 
        payload = json.loads(request.message)
        
        changes = payload["change"]
        
        for change in changes:
            table = change["table"]

            collection = db[table]
            
            if change["kind"] == "insert":
                data_map = {}
                for data in zip(change["columnnames"],change["columnvalues"]):
                    data_map[data[0]] = data[1]

                collection.insert_one(data_map)

                print("Successfully Inserted:")
                print(data_map)
            
            elif change["kind"] == "update":
                old_data_map = {}
                for data in zip(change["oldkeys"]["keynames"],change["oldkeys"]["keyvalues"]):
                    old_data_map[data[0]] = data[1]

                new_data_map = {}
                data_map = {}
                for data in zip(change["columnnames"],change["columnvalues"]):
                    data_map[data[0]] = data[1]
                new_data_map["$set"] = data_map
                
                collection.update_one(old_data_map,new_data_map)
            
                print("Successfully Updated")
                print(new_data_map)

            elif change["kind"] == "delete":
                data_map = {}
                for data in zip(change["oldkeys"]["keynames"],change["oldkeys"]["keyvalues"]):
                    data_map[data[0]] = data[1]

                collection.delete_one(data_map)

                print("Successfully Deleted")
                print(data_map)
 
        return replicator_pb2.MongoDBReply(message='Received')

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    replicator_pb2_grpc.add_ReplicatorServicer_to_server(Replicator(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
