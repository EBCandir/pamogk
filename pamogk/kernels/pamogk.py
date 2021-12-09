import networkx as nx

from pamogk.lib.sutils import *



def kernel(pat_ids, pathway, label_key, sigma, normalization=False):
    """
    Parameters
    ----------
    Histogram Kernel
    pat_ids:
        list of patient ids
    pathway:
        pathway networkx graph
    label_key: str
    sigma:sigma in the Gaussian RBF kernel
    normalization: {False} bool
        normalize the kernel matrix such that the diagonal is 1
    """

    num_pat = pat_ids.shape[0]
    pat_ind = {}
    for ind, pid in enumerate(pat_ids):
        pat_ind[pid] = ind
        maxlb = 0
        for idx, nid in enumerate(pathway.nodes):
            nd = pathway.nodes[nid]
            for pid, lb in nd[label_key].items():
                if pid in pat_ind.keys():
                    try:
                        lb = int(lb)
                    except ValueError:
                        _lb = 1
                    if _lb > maxlb:
                        maxlb=_lb

    # extract labels of nodes of graphs
    pat_vec = np.zeros([num_pat, maxlb], dtype=np.int) 
    for idx, nid in enumerate(pathway.nodes):
        nd = pathway.nodes[nid]
        for pid, lb in nd[label_key].items():

            if pid in pat_ind.keys():
                try:
                    _lb = int(lb)
                except ValueError:
                    _lb = 1
                pat_vec[pat_ind[pid], _lb] +=1 

    km = np.zeros((num_pat, num_pat))
    K=0
    for k in range(pat_vec.shape[0]-1): 
        for i in range(pat_vec.shape[0]-1): 
            for j in range(pat_vec.shape[1]-1): 

                K += (pat_vec[k][j] -  pat_vec[i][j]) * ((pat_vec[k][j] - pat_vec[i][j]))

            K = exp(-1.0 * K / (2.0 * sigma * sigma))
            km[k,i]=K 
# normalize the kernel matrix if normalization is true
    if normalization == True:
        km = normalize_kernel_matrix(km)
    return km
'''
def smooth(md, adj_m, alpha=0.5, epsilon=10 ** -6):
    """
    md: numpy array
        a numpy array of genes of patients indicating which one is mutated or not
    adj_m: numpy array
        the adjacency matrix of the pathway
    alpha: {0.5} float
        the smoothing parameter in range of 0-1
    epsilon: {1e-6} float
        smoothing converges if the change is lower than epsilon
    """
    # since alpha will be together with norm_adj_mat all the time multiply here
    alpha_norm_adj_mat = alpha * adj_m / np.sum(adj_m, axis=0)

    s_md = md
    pre_s_md = md + epsilon + 1

    while np.linalg.norm(s_md - pre_s_md) > epsilon:
        pre_s_md = s_md
        # alpha_norm_adj_mat already includes alpha multiplier
        s_md = (s_md @ alpha_norm_adj_mat) + (1 - alpha) * md

    return s_md

'''
def normalize_kernel_matrix(km):
    kmD = np.array(np.diag(km))
    kmD[kmD == 0] = 1
    D = np.diag(1 / np.sqrt(kmD))
    norm_km = np.linalg.multi_dot([D, km, D.T])  # K_ij / sqrt(K_ii * K_jj)
    return np.nan_to_num(norm_km)  # replace NaN with 0


def main():
    # Create a networkx graph object
    mg = nx.Graph()

    # Add edges to to the graph object
    # Each tuple represents an edge between two nodes
    mg.add_edges_from(
        [
            ("A", "B"),
            ("A", "C"),
            ("C", "D"),
            ("A", "E"),
            ("C", "E"),
            ("D", "B"),
            ("B", "C"),
            ("C", "X"),
        ]
    )

    mg2 = nx.Graph()
    mg2.add_edges_from(
        [
            ("A", "B"),
            ("A", "C"),
            ("C", "D"),
            ("A", "E"),
            ("C", "E"),
            ("D", "B"),
            ("B", "C"),
            ("C", "X"),
        ]
    )

    nx.set_node_attributes(
        mg, {"X": 0, "A": 1, "B": 0, "C": 0, "D": 1, "E": 0}, "label"
    )
    # nx.set_node_attributes(mg, {'X':'Protein', 'A':'Calcium', 'B':'Protein', 'C':'Protein', 'D':'Calcium', 'E':'Protein'}, 'type')
    nx.set_node_attributes(
        mg,
        {
            "X": "Protein",
            "A": "Protein",
            "B": "Protein",
            "C": "Protein",
            "D": "Protein",
            "E": "Protein",
        },
        "type",
    )

    nx.set_node_attributes(
        mg2, {"X": 1, "A": 1, "B": 0, "C": 0, "D": 1, "E": 0}, "label"
    )
    # nx.set_node_attributes(mg2, {'X':'Protein', 'A':'Calcium', 'B':'Protein', 'C':'Protein', 'D':'Calcium', 'E':'Protein'}, 'type')
    nx.set_node_attributes(
        mg2,
        {
            "X": "Protein",
            "A": "Protein",
            "B": "Protein",
            "C": "Protein",
            "D": "Protein",
            "E": "Protein",
        },
        "type",
    )

    # smoothing parameter for the kernel
    alpha = 0.1

    # calculate the kernel using PAMOGK
    # NOTE: this might not be working after some changes to the kernel method
    km = kernel(np.array([0, 1]), mg, alpha=alpha, label_key="label")

    # display the resulting kernel matrix
    print("Kernel matrix calculated by PAMOGK with alpha", alpha)
    print(km)


if __name__ == "__main__":
    main()
