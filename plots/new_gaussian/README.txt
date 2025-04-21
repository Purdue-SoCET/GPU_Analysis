===================================================================================================================================
"gaussian_out.txt" includes new useful information on the Gaussian workload located in the final section: "Core Wide Statistics"
===================================================================================================================================
    # "Avg. Divergence Duration (Cycles) Per Thread" 
        ## Contains the divergence duration of all threads averaged over all warps in order based off index.
            ### i.e. value at index 0 corresponds to thread 0
    ----------------------------------------------------------------------------------------------------------------
    # "Avg. Number of All 0s Thread Masks"
        ## Contains the number of times that the whole thread mask was all 0s averaged over all warps
    ----------------------------------------------------------------------------------------------------------------
    # "Total Thread Mask Scalarization Counts"
        ## Contains the (active_thread_mask, result_thread_mask) pairings in which the active thread mask and the 
           result thread mask are different, along with a counter of how many times that pairing showed up