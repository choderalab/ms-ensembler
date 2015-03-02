import os
import shutil
import tempfile
import numpy as np
import pandas as pd
import mdtraj
import seaborn as sns

srcdir = '../../data/models/SRC_HUMAN_D0'

df = pd.read_csv(os.path.join(srcdir, 'traj-refine_implicit_md-data.csv'))

traj = mdtraj.load(os.path.join(srcdir, 'traj-refine_implicit_md.xtc'), top=os.path.join(srcdir, 'traj-refine_implicit_md-topol.pdb'))

active_structure = mdtraj.load('2SRC.pdb')
inactive_structure = mdtraj.load('1Y57.pdb')

# K295 = 29
# E310 = 44
# R409 = 143
residue_labels = ['K295', 'E310', 'R409']
# traj_resids = [29, 44, 143]
# ref_structure_residue_ids = [295, 310, 409]
traj_residue_selections = [
    'residue 29 and (name NZ or name CD or name CE)',
    'residue 44 and (name "OE1" or name CD or name "OE2")',
    'residue 143 and (name "NH1" or name CZ or name "NH2")',
]
ref_residue_selections = [
    'residue 295 and (name NZ or name CD or name CE)',
    'residue 310 and (name "OE1" or name CD or name "OE2")',
    'residue 409 and (name "NH1" or name CZ or name "NH2")',
]
data_dict = {label: {'traj_residue_selection': traj_residue_selections[i], 'ref_residue_selection': ref_residue_selections[i]} for i, label in enumerate(residue_labels)}

for label in residue_labels:
    residue_dict = data_dict[label]
    traj_residue_selection = residue_dict['traj_residue_selection']
    ref_residue_selection = residue_dict['ref_residue_selection']
    # TODO work out which atom indices you want to keep - prob the last three
    residue_dict['indices'] = traj.top.select(traj_residue_selection)

    residue_dict['atom_slice_traj'] = traj.atom_slice(residue_dict['indices'])

    residue_dict['com'] = mdtraj.compute_center_of_mass(residue_dict['atom_slice_traj'])

    residue_dict['ref_indices_active'] = active_structure.top.select(ref_residue_selection)
    residue_dict['ref_indices_inactive'] = active_structure.top.select(ref_residue_selection)
    residue_dict['ref_atom_slice_active'] = active_structure.atom_slice(residue_dict['ref_indices_active'])
    residue_dict['ref_atom_slice_inactive'] = inactive_structure.atom_slice(residue_dict['ref_indices_inactive'])
    residue_dict['ref_com_active'] = mdtraj.compute_center_of_mass(residue_dict['ref_atom_slice_active'])
    residue_dict['ref_com_inactive'] = mdtraj.compute_center_of_mass(residue_dict['ref_atom_slice_inactive'])

pairs = [('K295', 'E310'), ('E310', 'R409')]

pairs_dict = {pair: {} for pair in pairs}

for pair in pairs:
    residue0 = data_dict[pair[0]]
    residue1 = data_dict[pair[1]]

    pairs_dict[pair]['distances'] = np.linalg.norm(residue0['com'] - residue1['com'], axis=1)

    pairs_dict[pair]['ref_distance_active'] = np.linalg.norm(residue0['ref_com_active'] - residue1['ref_com_active'], axis=1)
    pairs_dict[pair]['ref_distance_inactive'] = np.linalg.norm(residue0['ref_com_inactive'] - residue1['ref_com_inactive'], axis=1)

# plot

palette = sns.color_palette('RdBu', len(pairs_dict[pairs[0]]['distances']))

sns.plt.scatter(pairs_dict[pairs[0]]['distances'][::-1], pairs_dict[pairs[1]]['distances'][::-1], c=palette[::-1], marker='o', alpha=0.7)
sns.plt.scatter(pairs_dict[pairs[0]]['ref_distance_active'], pairs_dict[pairs[1]]['ref_distance_active'], facecolor='g', marker='*', s=200., linewidth=1., label='2SRC (active)')
sns.plt.scatter(pairs_dict[pairs[0]]['ref_distance_inactive'], pairs_dict[pairs[1]]['ref_distance_inactive'], facecolor='r', marker='*', s=200., linewidth=1., label='1Y57 (inactive)')

sns.plt.xlabel('-'.join(pairs[0]) + ' (nm)')
sns.plt.ylabel('-'.join(pairs[1]) + ' (nm)')
sns.plt.legend()

sns.plt.savefig('distances.png')
