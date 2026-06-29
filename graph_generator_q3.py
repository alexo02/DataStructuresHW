import pandas as pd
import matplotlib.pyplot as plt

experiments = [
    {'file': 'ex_res_1_after_fix.xlsx', 'label': 'ניסוי 1: BST (ממוין)', 'marker': 'o'},
    {'file': 'ex_res_2_after_fix.xlsx', 'label': 'ניסוי 2: AVL (ממוין)', 'marker': 's'},
    {'file': 'ex_res_3_after_fix.xlsx', 'label': 'ניסוי 3: BST (אקראי)', 'marker': '^'},
    {'file': 'ex_res_4_after_fix.xlsx', 'label': 'ניסוי 4: AVL (אקראי)', 'marker': 'd'}
]

x_column_name = 'size'
y_column_name = 'run_time (seconds)'

for exp in experiments:
    df = pd.read_excel(exp['file'])
    
    n_values = df[x_column_name].tolist()
    time_values = df[y_column_name].tolist()
    
    plt.figure(figsize=(8, 5))
    
    plt.plot(n_values, time_values, marker=exp['marker'], linestyle='-', label=exp['label'])
    
    plt.title(f"{exp['label']} (שאלה 3)", fontsize=18)
    plt.xlabel("גודל העץ (n)", fontsize=12)
    plt.ylabel("זמן ריצה (מילישניות)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    
    #plt.show()

    plt.savefig(f"{exp['label']} (שאלה 3).pdf")
        
       