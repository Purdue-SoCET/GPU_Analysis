##########################################################################
##########################################################################
## Purpose: To simulate runtime conditions of different divergence
## detection heuristics assuming a SIMT core architecture as the one 
## refrenced by Prof. Tim Rogers in the ECE 60827 lectures
## 
## Date: Nov 18, 2024
## Author: Hassan Al-alawi
##########################################################################
import re
import json
import sys

def count_active_threads(tmask):
	count = 0

	for bit in tmask:
		if bit == 1:
			count += 1

	return count

def conv_str_to_list(tmask):
	return [1 if char == '1' else 0 for char in tmask]

# Returns tid of all active threads in a thread mask
def get_tid(tmask, num_scalar):
	tids = [None] * num_scalar

	for i in range(num_scalar):
		if(1 in tmask):
			tids[i] = tmask.index(1)
			tmask[tids[i]] = 0
	return tids

# Checks if thread with tid is on in a given tmask
def is_tid_on(tmask, tid):
	tmask = conv_str_to_list(tmask)
	return tmask[tid]

# THIS FUNCTION IS RENDERED USELESS AFTER NEW UPDATES
# Finds most recent tmask where the scalarized thread has been active allowing only tmasks for SPLIT instructions
# def find_reconv_tmask(idx, tmasks, tmask, tid, instrs, div_instrs):

# 	reconverge_tmask = ""
# 	is_split		 = 0

# 	allowed_div_instr = ["SPLIT", "SPLIT.N"]
	
# 	while True:
# 		prev_tmask = tmasks[idx]

# 		if(prev_tmask != tmask):
# 			if(is_tid_on(prev_tmask, tid)):
# 				# split_instr = instrs[idx]

# 				# if split_instr not in div_instrs.keys():
# 				# 	new_dict_entry = {split_instr: 0}
# 				# 	div_instrs.update(new_dict_entry)
				
# 				# div_instrs[split_instr] += 1

# 				# if(split_instr in allowed_div_instr):
# 				reconverge_tmask = prev_tmask
# 				is_split = 1
# 				break
# 				# else:
# 				# 	break
			
# 			idx -= 1
		
# 		else:
# 			if(idx == 0):
# 				break
# 			idx -= 1
	
# 	return reconverge_tmask, is_split, div_instrs

# Reconverges all threads whose reconvergence tmask matches the current tmask
def reconverge(curr_instr_pc, scalar_mask, reconverge_pcs):
	num_reconv = 0

	for tid, scalarized in enumerate(scalar_mask):
		if(scalarized == 1):		
			if(reconverge_pcs[tid] == curr_instr_pc):	# should check if reconv pc == current pc
				scalar_mask[tid] = 0
				num_reconv += 1
	
	return num_reconv

# Returns 1 if there are active theads in the thread mask that arent scalarized
def and_scalar_mask(tmask, scalar_mask):
	tmask 		= conv_str_to_list(tmask)
	not_scalar_mask = [1 if bit==0 else 0 for bit in scalar_mask]
	result = [0]*len(tmask)
	num_act_threads = 0

	for i in range(len(tmask)):
		result[i] = not_scalar_mask[i] and tmask[i]
		if result[i]:
			num_act_threads += 1

	return 1 in result, num_act_threads, result

# Assummptions
# 1. Infinite thread transfer bandwidth 
# 2. Assume no stalls on SIMT Core end while waiting for scalar core to reconverge 
# 3. Assumes no stalls for requests to scalarization, such as in second level scheduler bottleneck

# Parameters
# 1. theta: Indicates sensitivity of the divergence detector. Sets a minimumn bound on
# number of divergent cycles that are counted for a given thread before the heuristic 
# elects to send the thread to the scalar core
#
# 2. num_threads: Number of threads per warp
#
# 3. tmasks: List of all the thread masks that are executed in one warp produced by
# baseline vortex GPU simulations
#
# 4. capacity: Is the maximumn capacity of the scalar core
#
# 5. num_scalar: Is the number of threads that the heuristic can send to the scalar core at any given cycle
#
# 6. scalarize_t0: True if we allow scalarization of thread 0 (typically the scheduler thread)

# Outputs
# 1. speed_up: Total Number of baseline vortex cycles / Simulated cycles with scalarization guided by the heuristic
# 
# 2. scalarized_threads: Dictionary of thread_masks, and indirectly threads, that were scalarized with the value being the number of times that they were scalarized, meaning sent and recomverged to SIMT core
#
# 3. max_occupancy: The max number of threads that were living on the scalar core during the simulation
#
# 4. num_reconv: The number of times a scalarized thread has been sent back to the SIMT core
#
# 5. cycles_saved: The difference in total cycles and simulated cycles
#
# 6. per_thread_count: The number of times each individual thread has been sent to the scalar core
#
# 7. simd_efficiency: The Percentage of the SIMD pipeline on the SIMT core that is utilized in simulation
#
# 8. frac_pred: The fraction of valid attempts at scalarization that were caused by non SPLIT instructions (e.g. TMC, PRED.N)
#
# 9. frac_ocp_full: The fraction of threads who met the scalarization conditons but the scalar core was full at the time so they were not allowed to be sent to the scalar core
#
# 10. div_instrs: Dictionary of instructions associated with a possible reconvergence tmask for a given thread. (e.g. want to scalarize a thread but the last tmask where it was active had instr PRED.N so we don't scalarize it but increment the PRED.N entry in the dictionary)

def sat_counters(tmasks, instrs, scalarize_t0, scalarize_pcs, theta=1000, num_threads=32, capacity=32, num_scalar=1):
	# Baseline number of cycles executed on vortex GPU
	total_cycles         = len(tmasks)
	sim_cycles			 = 0

	occupancy			 = 0 # Indicates number of threads on the scalar core 
	max_occupancy 	     = 0 # Indicates the maximumn occupancy value seen
	num_reconv 			 = 0 # Holds value of threads that reconverged in a sim given cycle

	simd_efficiency		 = 0
	total_active_threads = 0

	attempts_at_scalarization = 0
	failed_pred_scalarization = 0

	num_occupancy_full = 0
	num_check_occupancy = 0

	# For Debugging
	check_tmasks 		 = 0
	check_tmasks_list 	 = []
	check_reconv_tmask	 = ""

	div_instrs 			 = {}
	
	speed_up	 		 = 0
	scalarized_threads 	 = {}
	scalar_mask 		 = [0]*num_threads
	average_div_dur 	 = [0]*num_threads
	per_thread_count     = [0]*num_threads
	sat_counters		 = [0]*num_threads
	reconverge_pcs  	 = [0]*num_threads
	
	for idx, tmask in enumerate(tmasks):
		
		# debugging only
		if(check_tmasks):
			check_tmasks_list.append(tmask)	
		# Check if tmask is on the scalar core or not

		# count number of cycles a thread is on the scalar mask (how many cycles it's divergent for)
		for idxs, bit in enumerate(scalar_mask):
			if (bit):
				average_div_dur[idxs] += 1

		tmask_on_simt, active_threads, result_tmask = and_scalar_mask(tmask, scalar_mask)
		total_active_threads += active_threads

		current_instr_pc = instrs[idx]

		if tmask_on_simt == True:
			## If not on the scalar cores
			## Check if tmask count is in the range of numbers from 0-scalar_threads (T)
			
			# tmask_vector = conv_str_to_list(tmask) # Turn tmask string into bit vector
			tmask_vector = result_tmask
			acceptable_num_scalar = list(range(1,num_scalar+1))

			if(count_active_threads(tmask_vector) in acceptable_num_scalar):
				### If so increment the coresponding thread's saturating counter 
				tids = get_tid(tmask_vector, num_scalar)
				
				for tid in tids:
					if(tid != None):
						sat_counters[tid] += 1

						# New 'should_scalarize' condition: check if current PC is in scalarize_pcs dict - Shrey
						should_scalarize = False
						for start_end, pcs in scalarize_pcs.items():
							for pc in pcs:
								if current_instr_pc in pcs:
									reconvergence_pc = start_end[1]	# reconvergence pc
									should_scalarize = True
									# attempts_at_scalarization += 1
									reconverge_pcs[tid] = reconvergence_pc
									break

						### Check if count of the threads sat_counter reached threshold (theta)
						### If so check the capacity 
						if(sat_counters[tid] >= theta and (scalarize_t0 or (not scalarize_t0 and not(tid == 0)))):
							num_check_occupancy += 1

						if(sat_counters[tid] >= theta and occupancy >= capacity and (scalarize_t0 or (not scalarize_t0 and not(tid == 0)))):
							num_occupancy_full += 1

						# MODIFIED SCALARIZATION CONDITION - Shrey
						if(should_scalarize and sat_counters[tid] >= theta and occupancy < capacity and (scalarize_t0 or (not scalarize_t0 and not(tid == 0)))):
							##### If we have capacity AND instruction PC is in the scalarize_pcs dict (should_scalarize), set the tmasks status to on the scalar core and reset the counter

							# reconverge_tmask[tid], is_split, div_instrs = find_reconv_tmask(idx, tmasks, tmask, tid, instrs, div_instrs)	# repurpose reconvergence_tmask to reconvergence_pc and use it to index reconvergence pc (post dominator pc)

							# if(is_split):
							sat_counters[tid] = 0

							occupancy += 1
							attempts_at_scalarization += 1

							if(occupancy > max_occupancy):
								max_occupancy = occupancy

							if tmask not in scalarized_threads.keys():
								scalarized_threads[tmask] = 0

							scalarized_threads[tmask] += 1
							per_thread_count[tid]     += 1
							scalar_mask[tid]		   = 1
							
						elif(sat_counters[tid] >= theta and occupancy < capacity and (scalarize_t0 or (not scalarize_t0 and not(tid == 0)))):
							failed_pred_scalarization += 1
							attempts_at_scalarization += 1


			## Check if the tmask is a reconvergence tmask for any of the threads
			reconv_threads = 0 # Refers to the number of threads that have reconverged in this cycle

			reconv_threads = reconverge(current_instr_pc, scalar_mask, reconverge_pcs) # modified reconverge function to check if the reconvergence pc matches the current instr pc - Shrey

			occupancy -= reconv_threads
			num_reconv += reconv_threads

			## Increment sim_cycles
			sim_cycles += 1

		## If on the scalar core don't increment sim cycles as it is running in parallel with the other tmasks
		else:
			pass

	speed_up		= total_cycles/sim_cycles
	cycles_saved 	= total_cycles - sim_cycles
	simd_efficiency = total_active_threads*100/(sim_cycles*32)
	frac_pred 		= 0
	if(attempts_at_scalarization != 0):
		frac_pred   	= failed_pred_scalarization / attempts_at_scalarization

	frac_ocp_full = 0
	if(num_check_occupancy != 0):
		frac_ocp_full	= num_occupancy_full / num_check_occupancy

	for idx in range(len(average_div_dur)):
		if(per_thread_count[idx] > 0):
			average_div_dur[idx] /= per_thread_count[idx]

	return speed_up, scalarized_threads, max_occupancy, num_reconv, cycles_saved, per_thread_count, simd_efficiency, frac_pred, frac_ocp_full, div_instrs, average_div_dur


			

if __name__ == "__main__":
	# Get all Thread Masks from run.log
	source_file = sys.argv[1]
	results_file = sys.argv[2]

	warps_tmasks   = {}
	warps_instrs   = {}
	warps_ids	   = {}
	warps_stats	   = {}
	num_threads    = 32
	warps_to_probe = {}
	instr_pcs	   = []	# list of all PCs - Shrey

	# needed for IPDOM analysis - Shrey
	ipdom_analysis = {}	# list of divergent and reconvergence PCs - Shrey
	pc_pairs       = []	# list of divergent and reconvergence PC pairs - Shrey
	scalarize_pcs  = {}	# list of PCs that need to be scalarized (fall in divergence range) - Shrey
	temp_branch_pc = None

	convergent_mask = "" 
	in_kernel = 1

	# Read from run.log
	try:
		with open(source_file, 'r', errors="ignore") as file:
		
			while True:
				line = file.readline()
			
				config_pattern = r"-gpgpu_shader_core_pipeline              ([0-9]+):([0-9]+)"
				warp_num_pattern = r"Start warp ([0-9]+) and end warp ([0-9]+)"
				# tmask_pattern = r"warp_id=([0-9]+), core_id=([0-9]+), active_mask=((0|1)+)"
				tmask_pattern = r"warp_id=([0-9]+), core_id=([0-9]+), pc=(0x[0-9a-fA-F]+), active_mask=([01]+)"	# regex for instruction PC - Shrey
				end_pattern = r"GPGPU-Sim: \*\*\* exit detected \*\*\*"
				
				# this messed everything up
				# ipdom_pattern1 = r"\(potential\) branch divergence @  PC=0x([0-9a-fA-F]+)"		# regex for branch divergence PC - Shrey
				# ipdom_pattern2 = r"immediate post dominator      @  PC=0x([0-9a-fA-F]+)"		# regex for ipdom PC - Shrey
				ipdom_pattern1 = r"\(potential\) branch divergence @  PC=(0x[0-9a-fA-F]+)"		# regex for branch divergence PC - Shrey
				ipdom_pattern2 = r"immediate post dominator      @  PC=(0x[0-9a-fA-F]+)"		# regex for ipdom PC - Shrey

				if(re.search(config_pattern,line)):
					total_num_threads = int(re.search(config_pattern,line).group(1))
					num_threads = int(re.search(config_pattern,line).group(2))
			
					for i in range(num_threads):
						convergent_mask += "1"

				if(re.search(warp_num_pattern,line)):
					start_warp = int(re.search(warp_num_pattern,line).group(1))
					end_warp = int(re.search(warp_num_pattern,line).group(2))
					
					# warps_to_probe = ["0" for _ in range(start_warp,end_warp+1)]
					for i in range(start_warp,end_warp+1):
						warps_to_probe[i] = str(i)
						if(warps_to_probe[i] not in warps_tmasks.keys()):
							warps_tmasks[warps_to_probe[i]] = []
							warps_instrs[warps_to_probe[i]] = []
							warps_ids[warps_to_probe[i]] 	= []
							warps_stats[warps_to_probe[i]] 	= []

				if(re.search(tmask_pattern,line)):
					warp_id  = re.search(tmask_pattern,line).group(1)
					core_id  = re.search(tmask_pattern,line).group(2)
					instr_pc = re.search(tmask_pattern,line).group(3)		# grab instruction PC - Shrey
					tmask    = re.search(tmask_pattern,line).group(4)

					instr_pcs.append(instr_pc)	# add instruction PC to list - Shrey

					# ids1  = re.search(tmask_pattern,line).group(5)
					
					# instr_line = file.readline()
					# instr = re.search(instr_pattern,instr_line).group(2)
					
					# Once we see a mask with all 1s, then we have entered the kernel
					# if(tmask == convergent_mask and core_id == "0" and warp_id == "0"):
					# 	in_kernel = 1

					# End of kernel and return to scheduler (Not applicable to kernels that use TMC, like BFS)
					# if(instr == "TMC"): 
					# 	in_kernel = 0

					if(core_id == "0"):
						warps_tmasks[warp_id].append(tmask)
						# warps_instrs[warp_id].append(instr)
						# warps_ids[warp_id].append(ids1)

				# creates a list of pairs of divergent and reconvergence PCs using the IPDOM section of the log - Shrey
				if(re.search(ipdom_pattern1,line)):
					match_branch_div_pc = re.search(ipdom_pattern1,line)
					if (match_branch_div_pc):
						temp_branch_pc = match_branch_div_pc.group(1)			# store branch divergence PC temporarily - Shrey

				if(re.search(ipdom_pattern2,line)):
					match_dominator_pc = re.search(ipdom_pattern2,line)
					if (match_dominator_pc) and (temp_branch_pc is not None):
						dominator_pc = match_dominator_pc.group(1)				# grab ipdom reconvergence PC - Shrey
						pc_pairs.append((temp_branch_pc, dominator_pc))			# add branch divergence and reconvergence PC pair to list - Shrey
						temp_branch_pc = None									# reset temp_branch_pc - Shrey

				# creates a dictionary of divergent and reconvergence PCs that map to PCs that fall within their range - Shrey
				if 'instr_pc' in locals() and instr_pc is not None: 				# Ensure instr_pc exists before using it - Shrey
					for start, end in pc_pairs:
						if int(start, 16) <= int(instr_pc, 16) <= int(end, 16):		# check if instr_pc falls within divergent region / 16 is for hex -> decimal
							if (start, end) not in scalarize_pcs:
								scalarize_pcs[(start, end)] = set()  			# Use a set to store unique PCs - Shrey
							scalarize_pcs[(start, end)].add(instr_pc)  			# Add ensures uniqueness - Shrey

				if(re.search(end_pattern,line)):
					break
		
		# TESTING PURPOSES ONLY - Shrey --------------------------------
		# print("Scalarize PCs:")
		# for key, value in scalarize_pcs.items():
		# 	print(f"Branch PC: {key[0]}, Reconvergence PC: {key[1]}")
		# 	print("PCs to Scalarize:")
		# 	for pc in value:
		# 		print(f"  {pc}")
		# --------------------------------------------------------------

	except ValueError:
		print(line)
		print(instr_line)
		print("Error opening the log file f'{source}")

	num_warps = len(warps_to_probe.keys())

	thetas = range(10, 2000, 100)
	num_scalars = range(1, 9)
	capacity = 16
	
	expirement = {}
	number_of_expirements_done = 0
	progress = 0
	num_expirements = len(thetas)*len(num_scalars)

	print("Number of Expirements to be ran:", num_expirements)

	for num_scalar in num_scalars:

		for theta in thetas:
			avg_speed_up = 0
			avg_num_cycles_saved = 0
			avg_pct_cycles_saved = 0
			avg_rel_simd_efficiency = 0
			avg_simd_efficiency = 0
			avg_pct_non_split_div= 0
			avg_max_ocp = 0
			avg_pct_max_cap = 0
			avg_num_scalarizations = 0
			avg_num_reconvergences = 0

			for warp_id in warps_to_probe.values():

				tmask_profile = [0]*num_threads

				total_active_threads = 0

				tmasks = warps_tmasks[warp_id]
				instrs = warps_instrs[warp_id]
				ids    = warps_ids[warp_id]

				for tmask in tmasks:
					tmask = conv_str_to_list(tmask)
					num_act_threads = count_active_threads(tmask)
					total_active_threads += num_act_threads
					tmask_profile[num_act_threads-1] += 1

				tmask_percentages = [num*100/len(tmasks) for num in tmask_profile]
				rel_simd_efficiency  = total_active_threads*100 / (len(tmasks)*32)

				if(number_of_expirements_done == 0):
					print(f'\nWarp {warp_id} Statistics')
					print("Number of Thread Masks Processed:", len(tmasks))
					print("Thread Mask Profile")
					print("Number of Active Threads | Percentage of Thread Masks")
					print("-------------------------------------------------")
					for thread_num, percent in enumerate(tmask_percentages):
						if(percent > 0):
							print(f'{thread_num+1:<4}                     | {percent:.2f}')

				if(warp_id != "0"):
					scalarize_t0 = 1

				else:
					scalarize_t0 = 1

				speed_up, scalarized_threads, max_occupancy, num_reconv, cycles_saved, per_thread_count, simd_efficiency, frac_pred, frac_ocp_full, div_instrs, average_div_dur = sat_counters(tmasks, instr_pcs, scalarize_t0, scalarize_pcs, theta=theta, num_threads=num_threads, capacity=capacity, num_scalar=num_scalar)
				num_scalarizations = 0

				for scalar_tmask in scalarized_threads.keys():
					num_scalarizations += scalarized_threads[scalar_tmask]

				
				warps_stats[warp_id].append(cycles_saved)
				warps_stats[warp_id].append(speed_up)
				warps_stats[warp_id].append(rel_simd_efficiency)
				warps_stats[warp_id].append(simd_efficiency)
				warps_stats[warp_id].append(frac_pred)
				warps_stats[warp_id].append(frac_ocp_full)
				warps_stats[warp_id].append(max_occupancy)
				warps_stats[warp_id].append(num_scalarizations)
				warps_stats[warp_id].append(num_reconv)
				warps_stats[warp_id].append(scalarized_threads)
				warps_stats[warp_id].append(per_thread_count)
				warps_stats[warp_id].append(div_instrs)
				warps_stats[warp_id].append(average_div_dur)

				avg_speed_up 			+= speed_up
				avg_num_cycles_saved 	+= cycles_saved
				avg_pct_cycles_saved 	+= cycles_saved*100/len(tmasks)
				avg_rel_simd_efficiency += rel_simd_efficiency
				avg_simd_efficiency 	+= simd_efficiency
				avg_pct_non_split_div 	+= frac_pred*100
				avg_max_ocp 			+= max_occupancy
				avg_pct_max_cap 		+= frac_ocp_full*100
				avg_num_scalarizations  += num_scalarizations
				avg_num_reconvergences  += num_reconv

				if(number_of_expirements_done == 0):
					print("\n******************************************")
					print(f'Saturating Counters: Theta={theta}, Capacity={capacity}, Thread Scalarization Bandwidth={num_scalar}')
					print(f'Number of Cycles Saved:           {cycles_saved}')
					print(f'Percentage of Total Cycles Saved: {cycles_saved*100/len(tmasks):.2f}')
					print(f'Speed Up (%): 		          {(speed_up-1)*100:.3f}')
					print(f'Rel SIMD Eff:                     {rel_simd_efficiency:.3f}')
					print(f'Sim SIMD Eff:	                  {simd_efficiency:.3f}')
					print(f'Percentage of Not SPLIT Div:	  {frac_pred*100:.3f}')
					print(f'Max Occupancy:		          {max_occupancy}')
					print(f'Percentage of Max Capacity:	  {frac_ocp_full*100:.3f}')
					print(f'Number of Scalarizations: 	  {num_scalarizations}')
					print(f'Number of Reconvergences:         {num_reconv}')
					print(f'\nScalarized Thread Masks:')
					print("Thread Mask           	         | Number of Times Caused Scalarization")
					print("------------------------------------------------------------------------")
					for tmask in scalarized_threads.keys():
						print(f'{tmask:<32} | {scalarized_threads[tmask]}')
					print(f'\nThread Scalarization:')
					print("Thread Number | Number of Times Thread Scalarized | Average Divergence Duration")
					print("-------------------------------------------------------------------------------")
					for tid in range(len(per_thread_count)):
						if per_thread_count[tid] > 0:
							print(f'{tid:<4}          | {per_thread_count[tid]:<4}                              | {average_div_dur[tid]:.1f}')
					print("*******************************************************************************")

			avg_speed_up 			/= num_warps
			avg_num_cycles_saved 	/= num_warps
			avg_pct_cycles_saved 	/= num_warps
			avg_rel_simd_efficiency /= num_warps
			avg_simd_efficiency 	/= num_warps
			avg_pct_non_split_div 	/= num_warps
			avg_max_ocp 			/= num_warps
			avg_pct_max_cap 	    /= num_warps
			avg_num_scalarizations  /= num_warps
			avg_num_reconvergences  /= num_warps

			expirement[str((num_scalar,theta))] = [num_scalar,theta,avg_num_cycles_saved,avg_pct_cycles_saved,avg_speed_up,avg_rel_simd_efficiency,avg_simd_efficiency,avg_pct_non_split_div,avg_max_ocp,avg_pct_max_cap,avg_num_scalarizations,avg_num_reconvergences]

			if(number_of_expirements_done == 0):
				print("\n******************************************")
				print("Core Wide Statistics")
				print(f'Saturating Counters: Theta={theta}, Capacity={capacity}, Thread Scalarization Bandwidth={num_scalar}')
				print(f'Avg. Number of Cycles Saved:           {avg_num_cycles_saved}')
				print(f'Avg. Percentage of Total Cycles Saved: {avg_pct_cycles_saved:.2f}')
				print(f'Avg. Speed Up (%): 		       {(avg_speed_up-1)*100:.3f}')
				print(f'Avg. Rel SIMD Eff:                     {avg_rel_simd_efficiency:.3f}')
				print(f'Avg. Sim SIMD Eff:	               {avg_simd_efficiency:.3f}')
				print(f'Avg. Percentage of Not SPLIT Div:      {avg_pct_non_split_div:.3f}')
				print(f'Avg. Max Occupancy:		       {avg_max_ocp}')
				print(f'Avg. Percentage of Max Capacity:       {avg_pct_max_cap:.3f}')
				print(f'Avg. Number of Scalarizations: 	       {avg_num_scalarizations}')
				print(f'Avg. Number of Reconvergences:         {avg_num_reconvergences}')
				print("******************************************")

			number_of_expirements_done += 1
			progress = number_of_expirements_done / num_expirements
			print(f"\rExpirement Progress: {progress*100:.0f}%", end="")

	# exit()
	print("") # Just to add seperation from expirement progress bar and terminal prefix
	with open(results_file, "w") as f:
		json.dump(expirement, f)