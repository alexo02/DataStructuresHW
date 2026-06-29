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

plt.figure(figsize=(10, 6))

for exp in experiments:
    df = pd.read_excel(exp['file'])

    n_values = df[x_column_name].tolist()
    time_values = df[y_column_name].tolist()

    plt.plot(n_values, time_values, marker=exp['marker'], linestyle='-', label=exp['label'])


plt.title("השוואת זמני ריצה עבור ארבעת הניסויים(שאלה 4)", fontsize=14)
plt.xlabel("גודל העץ (n)", fontsize=12)
plt.ylabel("זמן ריצה (מילישניות)", fontsize=12)

plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()

# plt.show()

plt.savefig(f"{exp['label']} (שאלה 4).pdf")