import json
import matplotlib.pyplot as plt
import numpy as np
import sys

if __name__ == "__main__":
    source_file = sys.argv[1]
    dest_folder = sys.argv[2]
    expirements = {}

    num_scalar_idx              = 0
    theta_idx                   = 1
    avg_num_cycles_saved_idx    = 2
    avg_pct_cycles_saved_idx    = 3
    avg_speed_up_idx            = 4
    avg_rel_simd_efficiency_idx = 5
    avg_simd_efficiency_idx     = 6
    avg_pct_non_split_div_idx   = 7
    avg_max_ocp_idx             = 8
    avg_pct_max_cap_idx         = 9
    avg_num_scalarizations_idx  = 10
    avg_num_reconvergences_idx  = 11

    num_scalar_data = {}

    max_stats = {}

    max_stats["max_pct_cycles_saved"]           = [0,0,0]
    max_stats["max_speed_up"]                   = [0,0,0]
    max_stats["max_pct_delta_simd_efficiency"]  = [0,0,0]
    max_stats["max_num_scalarizations"]         = [0,0,0]

    colors = ['b', 'g', 'r', 'm', 'y', 'k', 'c', 'slategrey']

    with open(source_file, "r") as f:
        expirements = json.load(f)

    # Initializing data dict to allow accesses for each num_scalar (scalarization bandwidth)
    for key in expirements.keys():
        expirement = expirements[key]

        num_scalar = expirement[num_scalar_idx]
        
        
        if num_scalar not in num_scalar_data.keys():
            num_scalar_data[num_scalar] = []
        
        num_scalar_data[num_scalar].append(expirement[theta_idx:avg_num_reconvergences_idx])
    

    for num_scalar_idx, num_scalar in enumerate(num_scalar_data.keys()):
        data = num_scalar_data[num_scalar]

        thetas = [expr[theta_idx-1] for expr in data]
        avg_speed_ups = [(expr[avg_speed_up_idx-1]-1)*100 for expr in data]

        # Finding max statistics and configurations
        stats = [
            ("max_speed_up", avg_speed_ups)
        ]

        for idx in range(len(avg_speed_ups)):
            for stat_key, stat_values in stats:
                if stat_values[idx] > max_stats[stat_key][0]:
                    max_stats[stat_key][0] = stat_values[idx]
                    max_stats[stat_key][1] = num_scalar
                    max_stats[stat_key][2] = thetas[idx]

        plt.plot(thetas, avg_speed_ups, colors[num_scalar_idx], label=f'Scalarization Bandwidth: {num_scalar}')
        plt.xlabel("Saturation Limit")
        plt.ylabel("Speed Ups (%)")
        plt.title(f'Scalarization Bandwidth: 1-8')

    plt.legend()
    plt.savefig(f'{dest_folder}/avg_speed_ups.png')
    plt.close()

    for num_scalar_idx, num_scalar in enumerate(num_scalar_data.keys()):
        data = num_scalar_data[num_scalar]

        thetas = [expr[theta_idx-1] for expr in data]

        avg_rel_simd_efficiency = [expr[avg_rel_simd_efficiency_idx-1] for expr in data]
        avg_simd_efficiency = [expr[avg_simd_efficiency_idx-1] for expr in data]
        avg_pct_delta_simd_efficiency = [(avg_simd_efficiency[i] - avg_rel_simd_efficiency[i])*100/avg_rel_simd_efficiency[i] for i in range(len(avg_simd_efficiency))]


        # Finding max statistics and configurations
        stats = [
            ("max_pct_delta_simd_efficiency", avg_pct_delta_simd_efficiency)
        ]

        for idx in range(len(avg_speed_ups)):
            for stat_key, stat_values in stats:
                if stat_values[idx] > max_stats[stat_key][0]:
                    max_stats[stat_key][0] = stat_values[idx]
                    max_stats[stat_key][1] = num_scalar
                    max_stats[stat_key][2] = thetas[idx]


        plt.plot(thetas, avg_pct_delta_simd_efficiency, colors[num_scalar_idx], label=f'Scalarization Bandwidth: {num_scalar}')
        plt.xlabel("Saturation Limit")
        plt.ylabel("Change in SIMD Efficiency (%)")
        plt.title(f'Scalarization Bandwidth: 1-8')

    plt.legend()
    plt.savefig(f'{dest_folder}/avg_diff_simd_efficiency.png')
    plt.close()


    for num_scalar_idx, num_scalar in enumerate(num_scalar_data.keys()):
        data = num_scalar_data[num_scalar]

        thetas = [expr[theta_idx-1] for expr in data]

        avg_pct_cycles_saved = [expr[avg_pct_cycles_saved_idx-1] for expr in data]


        # Finding max statistics and configurations
        stats = [
            ("max_pct_cycles_saved", avg_pct_cycles_saved)
        ]

        for idx in range(len(avg_speed_ups)):
            for stat_key, stat_values in stats:
                if stat_values[idx] > max_stats[stat_key][0]:
                    max_stats[stat_key][0] = stat_values[idx]
                    max_stats[stat_key][1] = num_scalar
                    max_stats[stat_key][2] = thetas[idx]


        plt.plot(thetas, avg_pct_cycles_saved, colors[num_scalar_idx], label=f'Percentage Cycles Saved: {num_scalar}')
        plt.xlabel("Saturation Limit")
        plt.ylabel("Percentage Cycles Saved")
        plt.title(f'Scalarization Bandwidth: 1-8')

    plt.legend()
    plt.savefig(f'{dest_folder}/pct_cycles_saved.png')
    plt.close()
    

    for num_scalar_idx, num_scalar in enumerate(num_scalar_data.keys()):
        data = num_scalar_data[num_scalar]

        thetas = [expr[theta_idx-1] for expr in data]

        avg_num_scalarizations = [expr[avg_num_scalarizations_idx-1] for expr in data]


        # Finding max statistics and configurations
        stats = [
            ("max_num_scalarizations", avg_num_scalarizations)
        ]

        for idx in range(len(avg_speed_ups)):
            for stat_key, stat_values in stats:
                if stat_values[idx] > max_stats[stat_key][0]:
                    max_stats[stat_key][0] = stat_values[idx]
                    max_stats[stat_key][1] = num_scalar
                    max_stats[stat_key][2] = thetas[idx]


        plt.plot(thetas, avg_num_scalarizations, colors[num_scalar_idx], label=f'Number of Scalarizations: {num_scalar}')
        plt.xlabel("Saturation Limit")
        plt.ylabel("Number of Scalarizations")
        plt.title(f'Scalarization Bandwidth: 1-8')

    plt.legend()
    plt.savefig(f'{dest_folder}/num_scalarizations.png')
    plt.close()


    for num_scalar_idx, num_scalar in enumerate(num_scalar_data.keys()):
        data = num_scalar_data[num_scalar]

        thetas = [expr[theta_idx-1] for expr in data]

        avg_pct_non_split_div = [expr[avg_pct_non_split_div_idx-1] for expr in data]


        plt.plot(thetas, avg_pct_non_split_div, colors[num_scalar_idx], label=f'Percentage of Non-Split Dev: {num_scalar}')
        plt.xlabel("Saturation Limit")
        plt.ylabel("Percentage of Non-Split Dev")
        plt.title(f'Scalarization Bandwidth: 1-8')

    plt.legend()
    plt.savefig(f'{dest_folder}/pct_non_split_dev.png')
    plt.close()


    for num_scalar_idx, num_scalar in enumerate(num_scalar_data.keys()):
        data = num_scalar_data[num_scalar]

        thetas = [expr[theta_idx-1] for expr in data]

        avg_max_ocp = [expr[avg_max_ocp_idx-1] for expr in data]


        plt.plot(thetas, avg_max_ocp, colors[num_scalar_idx], label=f'Max Occupancy Reached: {num_scalar}')
        plt.xlabel("Saturation Limit")
        plt.ylabel("Occupancy")
        plt.title(f'Scalarization Bandwidth: 1-8')

    plt.legend()
    plt.savefig(f'{dest_folder}/max_ocp.png')
    plt.close()



    for num_scalar_idx, num_scalar in enumerate(num_scalar_data.keys()):
        data = num_scalar_data[num_scalar]

        thetas = [expr[theta_idx-1] for expr in data]

        avg_pct_max_cap = [expr[avg_pct_max_cap_idx-1] for expr in data]


        plt.plot(thetas, avg_pct_max_cap, colors[num_scalar_idx], label=f'Percentage of Max Capacity attempts: {num_scalar}')
        plt.xlabel("Saturation Limit")
        plt.ylabel("Percentage of Max Capacity")
        plt.title(f'Scalarization Bandwidth: 1-8')

    plt.legend()
    plt.savefig(f'{dest_folder}/pct_max_cap.png')
    plt.close()


    print("***********************")
    print("Max Statistics")
    for key in max_stats.keys():
        value = max_stats[key]
        print(f'{key:<30}: {value[0]:<10.3f} with num_scalar={value[1]} and theta={value[2]}')
    print("***********************")