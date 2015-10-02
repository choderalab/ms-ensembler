import os
import shutil
import tempfile
import numpy as np
import pandas as pd
import mdtraj
import seaborn as sns

srcdir_src = '../../../data/models/SRC_HUMAN_D0'
srcdir_abl = '../../../data/models/ABL1_HUMAN_D0'

df_src = pd.read_csv(os.path.join(srcdir_src, 'traj-refine_implicit_md-data.csv'))
df_abl = pd.read_csv(os.path.join(srcdir_abl, 'traj-refine_implicit_md-data.csv'))

traj_src = mdtraj.load(os.path.join(srcdir_src, 'traj-refine_implicit_md.xtc'), top=os.path.join(srcdir_src, 'topol-renumbered-implicit.pdb'))
traj_abl = mdtraj.load(os.path.join(srcdir_abl, 'traj-refine_implicit_md.xtc'), top=os.path.join(srcdir_abl, 'topol-renumbered-implicit.pdb'))

inactive_structure = mdtraj.load('../src/2SRC.pdb')
active_structure = mdtraj.load('../src/1Y57.pdb')

# hSrc cSrc
# K298 K295 = 29
# E313 E310 = 44
# R412 R409 = 143

# Abl
# K271 = 30
# E286 = 45
# R386 = 145

resSeqs_hsrc = [298, 313, 412]
resSeqs_csrc = [295, 310, 409]
resSeqs_abl = [271, 286, 386]
residue_indices_src = [r for r, resi in enumerate(traj_src.topology.residues) if resi.resSeq in resSeqs_hsrc]
residue_indices_abl = [r for r, resi in enumerate(traj_abl.topology.residues) if resi.resSeq in resSeqs_abl]
residue_indices_src_inactive = [r for r, resi in enumerate(inactive_structure.topology.residues) if resi.resSeq in resSeqs_csrc]
residue_indices_src_active = [r for r, resi in enumerate(active_structure.topology.residues) if resi.resSeq in resSeqs_csrc]

traj_residue_pair_indices_src = np.array([residue_indices_src[0:2], residue_indices_src[1:3]])
traj_residue_pair_indices_abl = np.array([residue_indices_abl[0:2], residue_indices_abl[1:3]])
inactive_structure_residue_pair_indices = np.array([residue_indices_src_inactive[0:2], residue_indices_src_inactive[1:3]])
active_structure_residue_pair_indices = np.array([residue_indices_src_active[0:2], residue_indices_src_active[1:3]])


pairs_csrc = [('K295', 'E310'), ('E310', 'R409')]
pairs_abl = [('K271', 'E286'), ('E286', 'R386')]

contacts_src = mdtraj.compute_contacts(traj_src, contacts=traj_residue_pair_indices_src)[0].T
contacts_abl = mdtraj.compute_contacts(traj_abl, contacts=traj_residue_pair_indices_abl)[0].T
inactive_structure_contacts = mdtraj.compute_contacts(inactive_structure, contacts=inactive_structure_residue_pair_indices)[0].T
active_structure_contacts = mdtraj.compute_contacts(active_structure, contacts=active_structure_residue_pair_indices)[0].T


# ====
# plot
# ====

sns.set_context('paper', font_scale=0.8)
sns.set_style('whitegrid')
# fig = sns.plt.figure(figsize=(7.25,2.625))
# ax1 = sns.plt.subplot(1,2,1)
figsize=(7.25,2.625)
fig, (ax1, ax2) = sns.plt.subplots(1, 2, figsize=figsize)

seqids_src = df_src.seqid
seqids_abl = df_abl.seqid

ax_models = ax1.scatter(contacts_src[0][::-1], contacts_src[1][::-1], c=seqids_src[::-1], cmap=sns.plt.cm.coolwarm_r, marker='o', alpha=0.7, vmin=0, vmax=100, s=15.)

ax1.scatter(active_structure_contacts[0], active_structure_contacts[1], facecolor='g', marker='*', s=80., linewidth=0.5, label='1Y57 (SRC, active)')
ax1.scatter(inactive_structure_contacts[0], inactive_structure_contacts[1], facecolor='r', marker='*', s=80., linewidth=0.5, label='2SRC (SRC, inactive)')

ax1.set_xlabel('-'.join(pairs_csrc[0]) + ' (nm)')
ax1.set_ylabel('-'.join(pairs_csrc[1]) + ' (nm)')
ax1.legend(fontsize=6.)
ax1.set_xlim(0,5)
ax1.set_ylim(0,5)
ax1.set_aspect('equal')

ax_models = ax2.scatter(contacts_abl[0][::-1], contacts_abl[1][::-1], c=seqids_abl[::-1], cmap=sns.plt.cm.coolwarm_r, marker='o', alpha=0.7, vmin=0, vmax=100, s=15.)
# ax2.set_aspect('equal')

ax2.scatter(active_structure_contacts[0], active_structure_contacts[1], facecolor='g', marker='*', s=80., linewidth=0.5, label='1Y57 (SRC, active)')
ax2.scatter(inactive_structure_contacts[0], inactive_structure_contacts[1], facecolor='r', marker='*', s=80., linewidth=0.5, label='2SRC (SRC, inactive)')
ax2.set_xlabel('-'.join(pairs_abl[0]) + ' (nm)')
ax2.set_ylabel('-'.join(pairs_abl[1]) + ' (nm)')
ax2.legend(fontsize=6.)
ax2.set_xlim(0,5)
ax2.set_ylim(0,5)
# ax1.set_aspect('equal')
ax2.set_aspect('equal')

cbaxes = fig.add_axes([0.9, 0.1, 0.02, 0.8])
cbar = sns.plt.colorbar(mappable=ax_models, cax=cbaxes, label='sequence identity (%)')
# Various failed attempts to get a smooth colorbar:
# cbar.set_alpha=1
# cbar.solids.set_rasterized(True) 
# cbar.solids.set_edgecolor("face")

fig.subplots_adjust(hspace=0)
# sns.plt.tight_layout()

sns.plt.savefig('distances_combined.pdf', bbox_inches='tight')
sns.plt.savefig('distances_combined.png', bbox_inches='tight', dpi=300)
# sns.plt.savefig('distances.png', dpi=300)
