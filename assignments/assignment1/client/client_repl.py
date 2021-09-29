import logging
import sys
import grpc
import replicator_pb2
import replicator_pb2_grpc
import json
import psycopg2
from psycopg2.extras import LogicalReplicationConnection
from google.protobuf.json_format import MessageToJson
from configparser import ConfigParser

def run():
    config_object = ConfigParser()
    config_object.read("client_config.ini")
    dbinfo = config_object["POSTGRES"]
    my_connection = psycopg2.connect(dbname = dbinfo["db"],  user = dbinfo["user"], password = dbinfo["password"], connection_factory = LogicalReplicationConnection)
    cur = my_connection.cursor()
    cur.drop_replication_slot(dbinfo["replica"])
    cur.create_replication_slot(dbinfo["replica"], output_plugin = 'wal2json')
    cur.start_replication(slot_name = dbinfo["replica"], options = {'pretty-print' : 1}, decode= True)
    cur.consume_stream(consume)

def consume(msg):
    try:
        with grpc.insecure_channel('localhost:50051') as channel:
            print("Replication Request:")
            print(msg.payload)
            stub = replicator_pb2_grpc.ReplicatorStub(channel)
            json_obj = json.loads(msg.payload)
            response = stub.ReplicateInMongoDB(replicator_pb2.PostgresDBRequest(message=msg.payload))
    except Exception as e: 
        print(e)

if __name__ == '__main__':
    logging.basicConfig()
    run()
