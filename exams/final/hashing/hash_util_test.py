import hashlib

from hash_util import Node
from hash_util import DefaultHash
from hash_util import ConsistentHash
from hash_util import HRWHash

NODES = [
    Node(name='Alex', host='1.2.3.1', port=80, hrw_weight=100, keys=[]),
    Node(name='Bob', host='1.2.3.2', port=80, hrw_weight=100, keys=[]),
    Node(name='Cody', host='1.2.3.3',port=80, hrw_weight=100, keys=[])
]
MAX_KEYS = 100

def print_nodes():
    for n in NODES:
        keys_on_node = len(n.keys)
        distribution = (len(n.keys) / MAX_KEYS) * 100
        print(f'{n.name} has total keys = {keys_on_node} ({distribution:.0f}%)')

def clear_keys():
    for n in NODES:
        n.keys.clear()          

def distribute_keys(hash_interface):
    for k in range(1, MAX_KEYS + 1):
        hashed_k = hashlib.sha256(str(k).encode()).hexdigest()
        node = hash_interface.get_node(hashed_k)
        node.keys.append(k)
    
    print_nodes()
    
    
def test_default_hash():
    print('#### Naive default hashing ####')
    clear_keys()
    distribute_keys(DefaultHash(NODES)) 

def test_hrw_hash():
    print('\n#### Rendezvous hashing (HRW) ####')
    clear_keys()
    distribute_keys(HRWHash(NODES))

def test_consistent_hash():
    print('\n#### Consistent hashing ####')
    clear_keys()
    distribute_keys(ConsistentHash(NODES))


if __name__ == "__main__":
    test_default_hash()
    test_hrw_hash()
    test_consistent_hash()

    