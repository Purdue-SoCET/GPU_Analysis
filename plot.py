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
    avg_div_dur_idx             = 12

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


    # # Plot average_div_dur as grouped bar chart per experiment
    # experiments = list(expirements.values())

    # # Assume all runs have same number of threads (based on first run)
    # num_threads = len(experiments[0][avg_div_dur_idx])
    # thread_ids = list(range(num_threads))
    # num_experiments = len(experiments)

    # # Set up bar width and x ticks for grouping
    # bar_width = 0.8 / num_experiments
    # x = np.arange(num_threads)

    # plt.figure(figsize=(16, 6))

    # for i, exp in enumerate(experiments):
    #     avg_div_dur = exp[avg_div_dur_idx]  # This is a list now
    #     durations = avg_div_dur  # Each index is the thread ID

    #     # Shift bars so they don't overlap (grouped style)
    #     plt.bar(x + i * bar_width, durations, width=bar_width, label=f'Run {i+1}')

    # plt.xlabel("Thread ID")
    # plt.ylabel("Average Divergence Duration (cycles)")
    # plt.title("Per-Thread Average Divergence Duration Across Runs")
    # plt.xticks(x + bar_width * (num_experiments / 2 - 0.5), thread_ids)
    # plt.legend()
    # plt.tight_layout()
    # plt.savefig(f'{dest_folder}/avg_div_dur_per_thread.png')
    # plt.close()

    # Plot average_div_dur as grouped bar chart per experiment
    experiments = list(expirements.values())
    num_experiments = len(experiments)

    # Assume all runs have same number of threads (based on first run)
    num_threads = len(experiments[0][avg_div_dur_idx])
    bar_width = 0.8 / num_experiments

    # Collect thread IDs that have at least one non-zero value across all runs
    valid_thread_ids = []
    for thread_id in range(num_threads):
        if any(exp[avg_div_dur_idx][thread_id] > 0 for exp in experiments):
            valid_thread_ids.append(thread_id)

    x = np.arange(len(valid_thread_ids))  # x positions for the filtered thread IDs

    plt.figure(figsize=(16, 6))

    for i, exp in enumerate(experiments):
        avg_div_dur = exp[avg_div_dur_idx]
        filtered_durations = [avg_div_dur[tid] for tid in valid_thread_ids]

        bars = plt.bar(x + i * bar_width, filtered_durations, width=bar_width, label=f'Scalarization Bandwidth: {exp[num_scalar_idx]}\nSaturation Limit: {exp[theta_idx]}', color=colors[i % len(colors)])

        # Annotate bars with their value if > 0
        for rect, value in zip(bars, filtered_durations):
            if value > 0:
                plt.text(
                    rect.get_x() + rect.get_width() / 2,
                    rect.get_height() + 0.5,
                    f'{value:.1f}',
                    ha='center',
                    va='bottom',
                    fontsize=8
                )

    plt.xlabel("Thread IDs (With Non-Zero Divergence Duration)")
    plt.ylabel("Average Divergence Duration (cycles)")
    plt.title("Per-Thread Average Divergence Duration Across Runs")
    plt.xticks(x + bar_width * (num_experiments / 2 - 0.5), valid_thread_ids)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{dest_folder}/avg_div_dur_per_thread.png')
    plt.close()


    print("***********************")
    print("Max Statistics")
    for key in max_stats.keys():
        value = max_stats[key]
        print(f'{key:<30}: {value[0]:<10.3f} with num_scalar={value[1]} and theta={value[2]}')
    print("***********************")