import random
import time
from AVLTree import *
import pandas as pd

class Ex:
    def run_ex(self,is_AVL ,is_perm ,i, number_of_iter):
        size = (300*(2**i))
        array = [i for i in range(1, size + 1)]
        tree_height = []
        num_of_rotations = []
        num_of_height_change = []
        amount_of_search_time = []
        run_time = []

        for n in range(1,number_of_iter+1):
            sum_search_time, sum_rotations, sum_height_changes = 0, 0, 0

            new_tree = AVLTree(is_AVL)
            if is_perm:
                random.shuffle(array)
            start_time = time.perf_counter()
            for val in array:
                new_node, search_time, rotations, height_changes = new_tree.insert(val, val)
                sum_search_time += search_time
                sum_rotations += rotations
                sum_height_changes += height_changes

            end_time = time.perf_counter()
            execution_time = end_time - start_time

            tree_height.append(new_tree.get_height())
            num_of_rotations.append(sum_rotations)
            num_of_height_change.append(sum_height_changes)
            amount_of_search_time.append(sum_search_time)
            run_time.append(execution_time)
        return (size,
                (sum(tree_height)/len(tree_height)),
                (sum(num_of_rotations)/len(num_of_rotations)),
                sum(num_of_height_change)/len(num_of_height_change),
                sum(amount_of_search_time)/len(amount_of_search_time),
                sum(run_time)/len(run_time)
                )
    def run_all(self,i_array,number_of_iter=20 ):
        result1 = []
        result2 = []
        result3 = []
        result4 = []

        for i in range(1,6):
            result1.append(self.run_ex(False, False, i, 4))

        for i in i_array:
            result2.append(self.run_ex(True, False, i, 4))
            result3.append(self.run_ex(False, True, i, number_of_iter))
            result4.append(self.run_ex(True, True, i, number_of_iter))

        return(
        result1,
        result2,
        result3,
        result4
        )



if __name__ == "__main__":
    i_array = [i for i in range(1, 11)]
    my_experiment = Ex()
    ex1, ex2, ex3, ex4 = my_experiment.run_all(i_array, 20)
    df = pd.DataFrame(ex1[0:], columns= ["size", "tree_height", "num_of_rotations", "num_of_height_change", "amount_of_search_time" , "run_time"    ] )
    df.to_excel("experiment_results1.xlsx", index=False)
    df = pd.DataFrame(ex2[0:], columns=["size", "tree_height", "num_of_rotations", "num_of_height_change",
                                        "amount_of_search_time", "run_time"])
    df.to_excel("experiment_results2.xlsx", index=False)
    df = pd.DataFrame(ex3[0:], columns=["size", "tree_height", "num_of_rotations", "num_of_height_change",
                                        "amount_of_search_time", "run_time"])
    df.to_excel("experiment_results3.xlsx", index=False)
    df = pd.DataFrame(ex4[0:], columns=["size", "tree_height", "num_of_rotations", "num_of_height_change",
                                        "amount_of_search_time", "run_time"])
    df.to_excel("experiment_results4.xlsx", index=False)