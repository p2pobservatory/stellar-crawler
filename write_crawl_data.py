# take the results from the crawl and write to the right directories

from datetime import datetime
import json
import os
import sys

datadir = sys.argv[1] if len(sys.argv) > 1 else './data'
if not datadir.endswith('/'):
    datadir += '/'
dirpath  = datadir + 'stellar/'

current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%Y%m%d %H")
formatted_date = formatted_datetime.split(' ')[0]


# make main directory if it doesn't exist
if not os.path.exists(dirpath):
    # Create the directory
    os.makedirs(dirpath)
    print(f"Directory '{dirpath}' created.")


# all discovered nodes
save_folder = dirpath+'discovered/'
if not os.path.exists(save_folder):
    # Create the directory
    os.makedirs(save_folder)
    print(f"Directory '{save_folder}' created.")


f_in = './js-stellar-node-crawler/crawler/crawl_result/all_nodes.json'
with open(f_in,'r') as f:
    data = json.loads(f.readline())


save_dir = dirpath+'discovered/'+formatted_date+'/'
if not os.path.exists(save_dir):
    # Create the directory
    os.makedirs(save_dir)
    print(f"Directory '{save_dir}' created.")

f_disc = 'stellar_discovered_'+ formatted_datetime+'.json'
with open(save_dir+f_disc, "w") as f:
    for ip in sorted(data):
        f.write(f'{ip}\n')


# crawl info
save_folder = dirpath+'crawl_data/'
if not os.path.exists(save_folder):
    # Create the directory
    os.makedirs(save_folder)
    print(f"Directory '{save_folder}' created.")
save_dir = dirpath+'crawl_data/'+formatted_date+'/'
if not os.path.exists(save_dir):
    # Create the directory
    os.makedirs(save_dir)
    print(f"Directory '{save_dir}' created.")

f_out = open(save_dir+'stellar_crawl_log_'+formatted_datetime+'.json','w')

f_in = './js-stellar-node-crawler/crawler/crawl_result/stellar_crawl.json'
node_peers = {} # to store the peers we learned from this node
with open(f_in,'r') as f:
    for line in f.readlines():
        f_out.write(line)
        if 'peers received' in line:
            line_data = json.loads(line)
            peer = line_data['peer']
            data = line_data['msg'].split(':')[-1].split(',')
            addrs = [data[i]+':'+data[i+1] for i in range(0,len(data)-1,2)]
            node_peers[peer] = sorted(addrs)

# node info
save_folder = dirpath+'responded_peerList/'
if not os.path.exists(save_folder):
    # Create the directory
    os.makedirs(save_folder)
    print(f"Directory '{save_folder}' created.")
save_dir = dirpath+'responded_peerList/'+formatted_date+'/'
if not os.path.exists(save_dir):
    # Create the directory
    os.makedirs(save_dir)
    print(f"Directory '{save_dir}' created.")

f_in = './js-stellar-node-crawler/crawler/crawl_result/nodes.json'
with open(f_in,'r') as f:
    node_info = json.loads(f.readline())

updated_nodes = []
ip_ports = []
for node in node_info:
    try:
        peers =  node_peers[node['publicKey']]
    except:
        peers = []
    node['peers'] = peers
    updated_nodes.append(node)
    try:
        ip_ports.append(node['ip']+':'+str(node['port']))
    except:
        continue

f_node_data = 'stellar_node_responses_'+formatted_datetime+'.json'
with open(save_dir+f_node_data, "w") as f:
    for node in updated_nodes:
        f.write(json.dumps(node)+'\n')

save_folder = dirpath+'active/'
if not os.path.exists(save_folder):
    # Create the directory
    os.makedirs(save_folder)
    print(f"Directory '{save_folder}' created.")
save_dir = dirpath+'active/'+formatted_date+'/'
if not os.path.exists(save_dir):
    # Create the directory
    os.makedirs(save_dir)
    print(f"Directory '{save_dir}' created.")

f_disc = 'stellar_active_'+ formatted_datetime+'.json'
with open(save_dir+f_disc, "w") as f:
    for ip in sorted(ip_ports):
        f.write(f'{ip}\n')


# update the seed list
f_in = './js-stellar-node-crawler/crawler/seed.json'
with open(f_in,'r') as f:
    seed_template = json.load(f)

seeds = []
for addr in ip_ports[:50]:
    ip = addr.split(':')[0]
    node = seed_template[0].copy()
    node['ip'] = ip
    seeds.append(node)

f_out = './js-stellar-node-crawler/crawler/nodes.json'
with open(f_out,'w') as f:
    json.dump(seeds,f)
