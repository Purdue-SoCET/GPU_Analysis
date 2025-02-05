import json
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    source_file = "expirements.json"
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
        # avg_pct_cycles_saved = [expr[avg_pct_cycles_saved_idx-1] for expr in data]

        # avg_rel_simd_efficiency = [expr[avg_rel_simd_efficiency_idx-1] for expr in data]
        # avg_simd_efficiency = [expr[avg_simd_efficiency_idx-1] for expr in data]
        # avg_pct_delta_simd_efficiency = [(avg_simd_efficiency[i] - avg_rel_simd_efficiency[i])*100/avg_rel_simd_efficiency[i] for i in range(len(avg_simd_efficiency))]

        # avg_pct_non_split_div = [expr[avg_pct_non_split_div_idx-1] for expr in data]
        # avg_max_ocp = [expr[avg_max_ocp_idx-1] for expr in data]
        # avg_pct_max_cap = [expr[avg_pct_max_cap_idx-1] for expr in data]
        # avg_num_scalarizations = [expr[avg_num_scalarizations_idx-1] for expr in data]

        # Checking for errors in statistics
        # for i in range(len(thetas)):
        #     if avg_pct_non_split_div[i] > 100:
        #         print(f'Percentage of Non-Split Divergence too high = {avg_pct_non_split_div[i]} for theta = {thetas[i]} and num_scalar = {num_scalar}')

        #     if avg_max_ocp[i] > 16:
        #         print(f'Max Occupancy too high = {avg_max_ocp[i]} for theta = {thetas[i]} and num_scalar = {num_scalar}')

        #     if avg_pct_max_cap[i] > 100:
        #         print(f'Percentage of Max Capacity = {avg_pct_max_cap[i]} too high for theta = {thetas[i]} and num_scalar = {num_scalar}')


        # Finding max statistics and configurations
        stats = [
            ("max_speed_up", avg_speed_ups)#,
            # ("max_pct_cycles_saved", avg_pct_cycles_saved),
            # ("max_pct_delta_simd_efficiency", avg_pct_delta_simd_efficiency),
            # ("max_num_scalarizations", avg_num_scalarizations),
        ]

        for idx in range(len(avg_speed_ups)):
            for stat_key, stat_values in stats:
                if stat_values[idx] > max_stats[stat_key][0]:
                    max_stats[stat_key][0] = stat_values[idx]
                    max_stats[stat_key][1] = num_scalar
                    max_stats[stat_key][2] = thetas[idx]


        # Finding knee in the graph
        min_pct_chg = 0.8

        speed_up_knee            = avg_speed_ups[0]
        # pct_cycles_saved_knee    = avg_pct_cycles_saved[0]
        # simd_efficiency_knee     = avg_pct_delta_simd_efficiency[0]
        # num_scalarization_knee   = avg_num_scalarizations[0]

        knee_list = [
            [speed_up_knee, 0]#,
            # [pct_cycles_saved_knee, 0],
            # [simd_efficiency_knee,0],
            # [num_scalarization_knee,0]
        ]

        for idx in range(len(thetas)):
            for stats_idx, tup in enumerate(stats):
                 _ , data = tup
                 dy = np.gradient(data, thetas)
                 ddy = np.gradient(dy, thetas)
                 knee_idx = np.argmin(ddy)
                 knee_list[stats_idx] = [data[knee_idx], thetas[knee_idx]]

        colors = ['b', 'g', 'r', 'm', 'y', 'k', 'c', 'slategrey']

        plt.plot(thetas, avg_speed_ups, colors[num_scalar_idx], label=f'Scalarization Bandwidth: {num_scalar}')
        plt.xlabel("Saturation Limit")
        plt.ylabel("Speed Ups (%)")
        plt.title(f'Scalarization Bandwidth: 1-8')
        # plt.plot(knee_list[0][1], knee_list[0][0], 'ro')
        # plt.text(knee_list[0][1], knee_list[0][0], f'({knee_list[0][1]}, {knee_list[0][0]:.2f})')

    plt.legend()
    plt.savefig(f'plots/avg_speed_ups.png')
    plt.close()



    for num_scalar_idx, num_scalar in enumerate(num_scalar_data.keys()):
        data = num_scalar_data[num_scalar]

        thetas = [expr[theta_idx-1] for expr in data]
        # avg_speed_ups = [(expr[avg_speed_up_idx-1]-1)*100 for expr in data]
        # avg_pct_cycles_saved = [expr[avg_pct_cycles_saved_idx-1] for expr in data]

        avg_rel_simd_efficiency = [expr[avg_rel_simd_efficiency_idx-1] for expr in data]
        avg_simd_efficiency = [expr[avg_simd_efficiency_idx-1] for expr in data]
        avg_pct_delta_simd_efficiency = [(avg_simd_efficiency[i] - avg_rel_simd_efficiency[i])*100/avg_rel_simd_efficiency[i] for i in range(len(avg_simd_efficiency))]

        # avg_pct_non_split_div = [expr[avg_pct_non_split_div_idx-1] for expr in data]
        # avg_max_ocp = [expr[avg_max_ocp_idx-1] for expr in data]
        # avg_pct_max_cap = [expr[avg_pct_max_cap_idx-1] for expr in data]
        # avg_num_scalarizations = [expr[avg_num_scalarizations_idx-1] for expr in data]

        # Checking for errors in statistics
        # for i in range(len(thetas)):
        #     if avg_pct_non_split_div[i] > 100:
        #         print(f'Percentage of Non-Split Divergence too high = {avg_pct_non_split_div[i]} for theta = {thetas[i]} and num_scalar = {num_scalar}')

        #     if avg_max_ocp[i] > 16:
        #         print(f'Max Occupancy too high = {avg_max_ocp[i]} for theta = {thetas[i]} and num_scalar = {num_scalar}')

        #     if avg_pct_max_cap[i] > 100:
        #         print(f'Percentage of Max Capacity = {avg_pct_max_cap[i]} too high for theta = {thetas[i]} and num_scalar = {num_scalar}')


        # Finding max statistics and configurations
        stats = [
            # ("max_speed_up", avg_speed_ups),
            # ("max_pct_cycles_saved", avg_pct_cycles_saved),
            ("max_pct_delta_simd_efficiency", avg_pct_delta_simd_efficiency)#,
            # ("max_num_scalarizations", avg_num_scalarizations),
        ]

        for idx in range(len(avg_speed_ups)):
            for stat_key, stat_values in stats:
                if stat_values[idx] > max_stats[stat_key][0]:
                    max_stats[stat_key][0] = stat_values[idx]
                    max_stats[stat_key][1] = num_scalar
                    max_stats[stat_key][2] = thetas[idx]


        # Finding knee in the graph
        min_pct_chg = 0.8

        # speed_up_knee            = avg_speed_ups[0]
        # pct_cycles_saved_knee    = avg_pct_cycles_saved[0]
        simd_efficiency_knee     = avg_pct_delta_simd_efficiency[0]
        # num_scalarization_knee   = avg_num_scalarizations[0]

        knee_list = [
            # [speed_up_knee, 0],
            # [pct_cycles_saved_knee, 0],
            [simd_efficiency_knee,0]#,
            # [num_scalarization_knee,0]
        ]

        for idx in range(len(thetas)):
            for stats_idx, tup in enumerate(stats):
                 _ , data = tup
                 dy = np.gradient(data, thetas)
                 ddy = np.gradient(dy, thetas)
                 knee_idx = np.argmin(ddy)
                 knee_list[stats_idx] = [data[knee_idx], thetas[knee_idx]]

        colors = ['b', 'g', 'r', 'm', 'y', 'k', 'c', 'slategrey']

        plt.plot(thetas, avg_pct_delta_simd_efficiency, colors[num_scalar_idx], label=f'Scalarization Bandwidth: {num_scalar}')
        plt.xlabel("Saturation Limit")
        plt.ylabel("Change in SIMD Efficiency (%)")
        plt.title(f'Scalarization Bandwidth: 1-8')
        # plt.plot(knee_list[0][1], knee_list[0][0], 'ro')
        # plt.text(knee_list[0][1], knee_list[0][0], f'({knee_list[0][1]}, {knee_list[0][0]:.2f})')

    plt.legend()
    plt.savefig(f'plots/avg_diff_simd_efficiency.png')
    plt.close()

    for num_scalar in num_scalar_data.keys():
        data = num_scalar_data[num_scalar]

        thetas = [expr[theta_idx-1] for expr in data]
        # avg_speed_ups = [(expr[avg_speed_up_idx-1]-1)*100 for expr in data]
        avg_pct_cycles_saved = [expr[avg_pct_cycles_saved_idx-1] for expr in data]

        # avg_rel_simd_efficiency = [expr[avg_rel_simd_efficiency_idx-1] for expr in data]
        # avg_simd_efficiency = [expr[avg_simd_efficiency_idx-1] for expr in data]
        # avg_pct_delta_simd_efficiency = [(avg_simd_efficiency[i] - avg_rel_simd_efficiency[i])*100/avg_rel_simd_efficiency[i] for i in range(len(avg_simd_efficiency))]

        avg_pct_non_split_div = [expr[avg_pct_non_split_div_idx-1] for expr in data]
        avg_max_ocp = [expr[avg_max_ocp_idx-1] for expr in data]
        avg_pct_max_cap = [expr[avg_pct_max_cap_idx-1] for expr in data]
        avg_num_scalarizations = [expr[avg_num_scalarizations_idx-1] for expr in data]

        # Checking for errors in statistics
        # for i in range(len(thetas)):
        #     if avg_pct_non_split_div[i] > 100:
        #         print(f'Percentage of Non-Split Divergence too high = {avg_pct_non_split_div[i]} for theta = {thetas[i]} and num_scalar = {num_scalar}')

        #     if avg_max_ocp[i] > 16:
        #         print(f'Max Occupancy too high = {avg_max_ocp[i]} for theta = {thetas[i]} and num_scalar = {num_scalar}')

        #     if avg_pct_max_cap[i] > 100:
        #         print(f'Percentage of Max Capacity = {avg_pct_max_cap[i]} too high for theta = {thetas[i]} and num_scalar = {num_scalar}')


        # Finding max statistics and configurations
        stats = [
            # ("max_speed_up", avg_speed_ups),
            ("max_pct_cycles_saved", avg_pct_cycles_saved),
            # ("max_pct_delta_simd_efficiency", avg_pct_delta_simd_efficiency),
            ("max_num_scalarizations", avg_num_scalarizations)
        ]

        for idx in range(len(avg_speed_ups)):
            for stat_key, stat_values in stats:
                if stat_values[idx] > max_stats[stat_key][0]:
                    max_stats[stat_key][0] = stat_values[idx]
                    max_stats[stat_key][1] = num_scalar
                    max_stats[stat_key][2] = thetas[idx]


        # Finding knee in the graph
        min_pct_chg = 0.8

        # speed_up_knee            = avg_speed_ups[0]
        pct_cycles_saved_knee    = avg_pct_cycles_saved[0]
        # simd_efficiency_knee     = avg_pct_delta_simd_efficiency[0]
        num_scalarization_knee   = avg_num_scalarizations[0]

        knee_list = [
            # [speed_up_knee, 0],
            [pct_cycles_saved_knee, 0],
            # [simd_efficiency_knee,0],
            [num_scalarization_knee,0]
        ]

        for idx in range(len(thetas)):
            for stats_idx, tup in enumerate(stats):
                 _ , data = tup
                 dy = np.gradient(data, thetas)
                 ddy = np.gradient(dy, thetas)
                 knee_idx = np.argmin(ddy)
                 knee_list[stats_idx] = [data[knee_idx], thetas[knee_idx]]

        plt.plot(thetas, avg_pct_cycles_saved)
        plt.xlabel("Saturation Limit")
        plt.ylabel("Percentage Cycles Saved")
        plt.title(f'Scalarization Bandwidth: {num_scalar}')
        plt.plot(knee_list[0][1], knee_list[0][0], 'ro')
        plt.text(knee_list[0][1], knee_list[0][0], f'({knee_list[0][1]}, {knee_list[0][0]:.2f})')
        plt.savefig(f'plots/avg_pct_cycles_saved_{num_scalar}.png')
        plt.close()


        plt.plot(thetas, avg_pct_non_split_div)
        plt.xlabel("Saturation Limit")
        plt.ylabel("Percentage of Non-Split Divergence")
        plt.title(f'Scalarization Bandwidth: {num_scalar}')
        plt.savefig(f'plots/avg_pct_non_split_div_{num_scalar}.png')
        plt.close()

        plt.plot(thetas, avg_max_ocp)
        plt.xlabel("Saturation Limit")
        plt.ylabel("Max Occupancy")
        plt.title(f'Scalarization Bandwidth: {num_scalar}')
        plt.savefig(f'plots/avg_max_ocp_{num_scalar}.png')
        plt.close()

        plt.plot(thetas, avg_pct_max_cap)
        plt.xlabel("Saturation Limit")
        plt.ylabel("Percentage of Max Capacity Reached")
        plt.title(f'Scalarization Bandwidth: {num_scalar}')
        plt.savefig(f'plots/avg_pct_max_cap_{num_scalar}.png')
        plt.close()

        plt.plot(thetas, avg_num_scalarizations)
        plt.xlabel("Saturation Limit")
        plt.ylabel("Number of Scalarizations")
        plt.title(f'Scalarization Bandwidth: {num_scalar}')
        plt.plot(knee_list[1][1], knee_list[1][0], 'ro')
        plt.text(knee_list[1][1], knee_list[1][0], f'({knee_list[1][1]}, {knee_list[1][0]:.2f})')
        plt.savefig(f'plots/avg_num_scalarizations_{num_scalar}.png')
        plt.close()

    print("***********************")
    print("Max Statistics")
    for key in max_stats.keys():
        value = max_stats[key]
        print(f'{key:<30}: {value[0]:<10.3f} with num_scalar={value[1]} and theta={value[2]}')
    print("***********************")