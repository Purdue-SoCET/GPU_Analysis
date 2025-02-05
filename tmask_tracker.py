"""Extracting tmask for workload analysis
"""
import re
import time


source_file  = open("../run.log", 'r', encoding="utf8")
# dest_file    = open("pc_tracker.log", 'w', encoding="utf8")
kernel_file  = open("../tests/regression/demo/kernel.dump", 'r', encoding="utf8")

tmask_dict = {}
tmask_types = []
opcode_divergence_dict = {}
list_of_opcode_divergence_dicts = []

num_threads  = 0
num_warps    = 0
num_cores    = 0
num_clusters = 0
socket_size  = 0

ideal_tmask = ""
vx_spawn_threads_addr = ""

global_ideal_tmask = 0
stream_ideal_tmask = []

global_divergence = 0
stream_divergence = []

old_opcode  = []
old_pc      = []
old_uuid    = []

diverge_opcode_pc = []

# Processing kernel.dump file
try:
    while True:
        vx_spawn_threads_addr = kernel_file.readline()
        if not vx_spawn_threads_addr:
            break


        pattern = r"([0-9]+) <vx_spawn_threads>:"

        match = re.search(pattern, vx_spawn_threads_addr)

        if not match:
            continue

        vx_spawn_threads_addr = match.group(1)
        break
finally:
    kernel_file.close



try:
    while True:
        # Read two lines
        # Pattern:
        # DEBUG Fetch
        # DEBUG Instr

        line1 = source_file.readline()
        line2 = source_file.readline()

        if line1 == '' and line2 == '':
            # Clean up
            for core in range(num_cores):
                for warp in range(num_warps):
                    if stream_divergence[core][warp] != 0: # Diverge until EOF
                        opcode_pc_tuple = diverge_opcode_pc[core][warp]
                        list_of_opcode_divergence_dicts[core][warp][opcode_pc_tuple] = stream_divergence[core][warp]

                    stream_divergence[core][warp] = 0

            break

        # ---------------------------------------------------------------------
        # READING CONFIGS FOR THREAD MASK
        if line1.startswith("CONFIGS") or line2.startswith("CONFIGS"):
            pattern = r"num_threads=(\d+), num_warps=(\d+), num_cores=(\d+), num_clusters=(\d+), socket_size=(\d+), *"

            match = re.search(pattern, line1)
            if not match:
                match = re.search(pattern, line2)

            if not match:
                print(line1)
                print(line2)
                raise Exception("something wrong with CONFIGS") 

            num_threads  = int(match.group(1))
            num_warps    = int(match.group(2))
            num_cores    = int(match.group(3))
            num_clusters = int(match.group(4))
            socket_size  = int(match.group(5))

            ideal_tmask = num_threads * "1"
            list_of_opcode_divergence_dicts = [[{} for _ in range(num_warps)] for _ in range(num_cores)]
            stream_ideal_tmask  = [[ 0 for _ in range(num_warps)] for _ in range(num_cores)]
            stream_divergence   = [[ 0 for _ in range(num_warps)] for _ in range(num_cores)]
            old_opcode          = [["" for _ in range(num_warps)] for _ in range(num_cores)]
            old_pc              = [["" for _ in range(num_warps)] for _ in range(num_cores)]
            old_uuid            = [["" for _ in range(num_warps)] for _ in range(num_cores)]
            diverge_opcode_pc   = [[() for _ in range(num_warps)] for _ in range(num_cores)]
        # -------------------------------------------------------------------


        # ---------------------------------------------------------------------
        # READING FETCH AND INSTR AT THE SAME TIME
        if line2.startswith("DEBUG Fetch"): 
            # Making sure that line1 is fetch and line2 is instr
            line1 = line2
            line2 = source_file.readline()

        if not line1.startswith("DEBUG"):
            continue

        if not line1.startswith("DEBUG Fetch"):
            print(line1)
            print("faulty script for Fetch")

        if not line2.startswith("DEBUG Instr"):
            print(line2)
            print("faulty script for Instr")
        # ---------------------------------------------------------------------


        # ---------------------------------------------------------------------
        # EXTRACTING IMPORTANT DATA
        opcode_key = ""

        # Fetch
        pattern = r"cid=(\d+), wid=(\d+), tmask=(\d+), PC=(0x[0-9a-fA-F]+) \((\#[0-9]+)\)"
        match = re.search(pattern, line1)

        if match:
            curr_coreID = int(match.group(1))
            curr_warpID = int(match.group(2))
            curr_tmask  = str(match.group(3))
            curr_pc     = str(match.group(4))
            uuid        = str(match.group(5))

        else:
            print(line1)
            raise Exception("something wrong with DEBUG Fetch") 

        # Instruction
        
        # 2nd line
        pattern = r"0x[0-9a-fA-f]+: ([a-zA-Z\.]+) .*"
        match = re.search(pattern, line2)

        if match:
            extracted_opcode = match.group(1)
        else:
            print(line2)
            raise Exception("something wrong with DEBUG Instr") 
        # ---------------------------------------------------------------------

        # DEBUGGING PURPOSE - Split out certaint coreID and warpID
        # if curr_coreID == 0 and curr_warpID == 1:
        #     print(line1.rstrip('\n'))
        #     print(line2.rstrip('\n'))

        # ---------------------------------------------------------------------
        # DATA ANALYSIS
        if curr_tmask == ideal_tmask:
            if stream_divergence[curr_coreID][curr_warpID] != 0: # Start of converge
                opcode_pc_tuple = diverge_opcode_pc[curr_coreID][curr_warpID]
                list_of_opcode_divergence_dicts[curr_coreID][curr_warpID][opcode_pc_tuple] = stream_divergence[curr_coreID][curr_warpID]

            stream_ideal_tmask[curr_coreID][curr_warpID] += 1
            global_ideal_tmask += 1
            stream_divergence[curr_coreID][curr_warpID] = 0
        else:
            if stream_ideal_tmask[curr_coreID][curr_warpID] != 0: # The start of divergence
                diverge_opcode_pc[curr_coreID][curr_warpID] = (old_opcode[curr_coreID][curr_warpID], old_pc[curr_coreID][curr_warpID], old_uuid[curr_coreID][curr_warpID])
                opcode_pc_tuple = diverge_opcode_pc[curr_coreID][curr_warpID]

                if opcode_pc_tuple not in list_of_opcode_divergence_dicts[curr_coreID][curr_warpID].keys():
                    list_of_opcode_divergence_dicts[curr_coreID][curr_warpID][opcode_pc_tuple] = 1

                else:
                    list_of_opcode_divergence_dicts[curr_coreID][curr_warpID][opcode_pc_tuple] += 1 # shouldn't happen anyway

            stream_divergence[curr_coreID][curr_warpID] += 1
            global_divergence += 1
            stream_ideal_tmask[curr_coreID][curr_warpID] = 0

        if curr_tmask not in tmask_dict.keys():
            tmask_dict[curr_tmask] = 1

        else:
            tmask_dict[curr_tmask] += 1
        
        old_opcode[curr_coreID][curr_warpID] = extracted_opcode
        old_pc[curr_coreID][curr_warpID] = curr_pc
        old_uuid[curr_coreID][curr_warpID] = uuid
        # ---------------------------------------------------------------------
    
    print("------------------------------")
    print(f"num_threads  = {num_threads }")
    print(f"num_warps    = {num_warps   }")
    print(f"num_cores    = {num_cores   }")
    print(f"num_clusters = {num_clusters}")
    print(f"socket_size  = {socket_size }")
    print("------------------------------")

    for key in tmask_dict.keys():
        print(f"{key} : {tmask_dict[key]}")

    print("------------------------------")

    for core in range(num_cores):
        for warp in range(num_warps):
            print("------------------------------")
            print(f"Core {core} warp {warp}")

            for key in list_of_opcode_divergence_dicts[core][warp].keys():
                print(f"{key} : {list_of_opcode_divergence_dicts[core][warp][key]}")

            print("------------------------------")

    # print(f"Core {0} warp {1}")
    # for key in list_of_opcode_divergence_dicts[0][1].keys():
    #     print(f"{key} : {list_of_opcode_divergence_dicts[0][1][key]}")

    print(f"global_ideal_tmask = {global_ideal_tmask}")
    print(f"global_divergence = {global_divergence}")

    
finally:
    source_file.close()

