import os

def set_az_pl_environment_variables(single_node=False, master_port=6105):
    if not single_node:
        master_node_params = os.environ["AZ_BATCH_MASTER_NODE"].split(":")
        os.environ["MASTER_ADDR"] = master_node_params[0]

        # Do not overwrite master port with that defined in AZ_BATCH_MASTER_NODE
        if "MASTER_PORT" not in os.environ:
            os.environ["MASTER_PORT"] = str(master_port)
    else:
        os.environ["MASTER_ADDR"] = os.environ["AZ_BATCHAI_MPI_MASTER_NODE"]
        os.environ["MASTER_PORT"] = "54965"

    os.environ["NCCL_SOCKET_IFNAME"] = "^docker0,lo"
    os.environ["NODE_RANK"] = os.environ["OMPI_COMM_WORLD_RANK"]
    
    # additional variables
    os.environ["MASTER_ADDRESS"] = os.environ["MASTER_ADDR"]
    os.environ["LOCAL_RANK"] = os.environ["OMPI_COMM_WORLD_LOCAL_RANK"]
    os.environ["WORLD_SIZE"] = os.environ["OMPI_COMM_WORLD_SIZE"]

    print("NODE_RANK = {}".format(os.environ["NODE_RANK"]))
    print("WORLD_SIZE = {}".format(os.environ["WORLD_SIZE"]))
    print("MASTER_ADDR = {}".format(os.environ["MASTER_ADDR"]))
    print("MASTER_PORT = {}".format(os.environ["MASTER_PORT"]))
    print("NCCL_SOCKET_IFNAME new value = {}".format(os.environ["NCCL_SOCKET_IFNAME"]))
