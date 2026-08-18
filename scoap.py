#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// File       : scoap.py
#// Language   : Python
#// Description: Combinational and Sequential SCOAP-based Controllability and Observability Computation
#//              Combinational Probablity-based Controllability and Observability Computation
#//              Generates CSV file containing the Controllability and Observability values for flip-flops
#// Author     : Sandesh Prabhakar
#// Created    : April 1, 2026
#// Modified   : August 17, 2026
#// Version    : 1.0
#//
#// Copyright (c) 2026 Sandesh Prabhakar
#// All rights reserved
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

import sys
import numpy as np
from enum import Enum
import copy

if len(sys.argv) <3:
	print("Error: Missing command-line arguments.")
	print("Usage: scoap.py <circuit-name> <none/clk/clk_rst")
	sys.exit(1)

#INFINITY = 9999999999999999
INFINITY = float("inf")

if sys.argv[2] == 'clk':
	CC0_CLK=1
	CC1_CLK=1
	SC0_CLK=0
	SC1_CLK=0
	CC1_R=0
	CC0_R=0
	SC0_R=0
	SC1_R=0
elif sys.argv[2] == 'clk_rst':
	CC0_CLK=1
	CC1_CLK=1
	SC0_CLK=0
	SC1_CLK=0
	CC1_R=1
	CC0_R=1
	SC0_R=0
	SC1_R=0
else:
	CC0_CLK=0
	CC1_CLK=0
	SC0_CLK=0
	SC1_CLK=0
	CC1_R=0
	CC0_R=0
	SC0_R=0
	SC1_R=0


def stem_observability(gate_src,fanout,fanoutlist,numDFFs,fanin_dict,combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output):
	list_fanout_obs_combo=[]
	list_fanout_obs_prob=[]
	list_fanout_obs_seq=[]

	for nn in range(0,int(fanout[gate_src])):
		temp_fanout=int(fanoutlist[gate_src][nn])
		temp_fanin=int(fanin_dict[temp_fanout][gate_src])
		#temp_obs=int(combo_scoap_input[temp_fanout][temp_fanin][2])
		temp_obs=combo_scoap_input[temp_fanout][int(temp_fanin)][2]
		list_fanout_obs_combo.append(temp_obs)
		temp_obs=combo_prob_scoap_input[temp_fanout][temp_fanin][2]
		list_fanout_obs_prob.append(temp_obs)
		if numDFFs > 0:
			#temp_obs=int(seq_scoap_input[temp_fanout][temp_fanin][2])
			temp_obs=seq_scoap_input[temp_fanout][temp_fanin][2]
			list_fanout_obs_seq.append(temp_obs)

	#combo_scoap_output[gate_src][2]=min(list_fanout_obs_combo)
	if min(list_fanout_obs_combo) != INFINITY:
		combo_scoap_output[gate_src][2]=int(min(list_fanout_obs_combo))
	else:
		combo_scoap_output[gate_src][2]=min(list_fanout_obs_combo)
	combo_prob_scoap_output[gate_src][2]=max(list_fanout_obs_prob)
	if numDFFs > 0:
		#seq_scoap_output[gate_src][2]=min(list_fanout_obs_seq)
		if min(list_fanout_obs_seq) != INFINITY:
			seq_scoap_output[gate_src][2]=int(min(list_fanout_obs_seq))
		else:
			seq_scoap_output[gate_src][2]=min(list_fanout_obs_seq)


def xor_xnor_observability(gate_src,fanin,numDFFs, combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output):

	for nn in range(0,int(fanin[gate_src])):
		temp_01_control_combo=[]
		temp_01_control_prob=[]
		temp_01_control_seq=[]
		for p in range(0,int(fanin[gate_src])):
			if nn != p:
				temp_01_control_combo.append(combo_scoap_input[gate_src][p][0])
				temp_01_control_combo.append(combo_scoap_input[gate_src][p][1])
				temp_01_control_prob.append(combo_prob_scoap_input[gate_src][p][0])
				temp_01_control_prob.append(combo_prob_scoap_input[gate_src][p][1])
				if numDFFs > 0:
					temp_01_control_seq.append(seq_scoap_input[gate_src][p][0])
					temp_01_control_seq.append(seq_scoap_input[gate_src][p][1])

		combo_scoap_input[gate_src][nn][2]=(min(temp_01_control_combo)+combo_scoap_output[gate_src][2])+1
		combo_prob_scoap_input[gate_src][nn][2]=(max(temp_01_control_prob)*combo_prob_scoap_output[gate_src][2])
		if numDFFs > 0:
			seq_scoap_input[gate_src][nn][2]=min(temp_01_control_seq)+seq_scoap_output[gate_src][2]


def and_nand_observability(gate_src,fanin,numDFFs, combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output):

	for nn in range(0,int(fanin[gate_src])):
		temp_1_control_combo=0
		temp_1_control_prob=1
		temp_1_control_seq=0
		for p in range(0,int(fanin[gate_src])):
			if nn != p:
				temp_1_control_combo=temp_1_control_combo+combo_scoap_input[gate_src][p][1]
				temp_1_control_prob=temp_1_control_prob*combo_prob_scoap_input[gate_src][p][1]
				if numDFFs > 0:
					temp_1_control_seq=temp_1_control_seq+seq_scoap_input[gate_src][p][1]


		combo_scoap_input[gate_src][nn][2]=(temp_1_control_combo+combo_scoap_output[gate_src][2])+1
		combo_prob_scoap_input[gate_src][nn][2]=(temp_1_control_prob*combo_prob_scoap_output[gate_src][2])
		if numDFFs > 0:
			seq_scoap_input[gate_src][nn][2]=temp_1_control_seq+seq_scoap_output[gate_src][2]


def or_nor_observability(gate_src,fanin,numDFFs, combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output):

	for nn in range(0,int(fanin[gate_src])):
		temp_0_control_combo=0
		temp_0_control_prob=1
		temp_0_control_seq=0
		for p in range(0,int(fanin[gate_src])):
			if nn != p:
				temp_0_control_combo=temp_0_control_combo+combo_scoap_input[gate_src][p][0]
				temp_0_control_prob=temp_0_control_prob*combo_prob_scoap_input[gate_src][p][0]
				if numDFFs > 0:
					temp_0_control_seq=temp_0_control_seq+seq_scoap_input[gate_src][p][0]


		combo_scoap_input[gate_src][nn][2]=(temp_0_control_combo+combo_scoap_output[gate_src][2])+1
		combo_prob_scoap_input[gate_src][nn][2]=(temp_0_control_prob*combo_prob_scoap_output[gate_src][2])
		if numDFFs > 0:
			seq_scoap_input[gate_src][nn][2]=temp_0_control_seq+seq_scoap_output[gate_src][2]


def buf_not_observability(gate_src,fanin,numDFFs, combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output):

	combo_scoap_input[gate_src][0][2]=combo_scoap_output[gate_src][2]+1
	combo_prob_scoap_input[gate_src][0][2]=	combo_prob_scoap_output[gate_src][2]
	if numDFFs > 0:
		seq_scoap_input[gate_src][0][2]=seq_scoap_output[gate_src][2]

def dff_observability(gate_src,fanin,numDFFs, combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output):

	combo_scoap_input[gate_src][0][2]=combo_scoap_output[gate_src][2] + CC0_CLK + CC1_CLK + CC0_R
	combo_prob_scoap_input[gate_src][0][2]=	combo_prob_scoap_output[gate_src][2]
	seq_scoap_input[gate_src][0][2]=seq_scoap_output[gate_src][2] +  SC0_CLK + SC1_CLK + SC0_R + 1


def evaluate_observability (gate_src, gtype, fanin, faninlist, fanout, fanoutlist,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output,combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,fanin_dict,numDFFs ):
	#print("obser2 gate_src = ",gate_src)
	#print("obser2 gate_type = ",gtype[gate_src])
	match gtype[gate_src]:
		#INPUT
		case 1:

			stem_observability(gate_src,fanout,fanoutlist,numDFFs,fanin_dict,combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output)

		#NAND gate
		case 7:
			stem_observability(gate_src,fanout,fanoutlist,numDFFs,fanin_dict,combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output)

			and_nand_observability(gate_src,fanin,numDFFs, combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output)


		#AND gate
		case 6:
			stem_observability(gate_src,fanout,fanoutlist,numDFFs,fanin_dict,combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output)

			and_nand_observability(gate_src,fanin,numDFFs, combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output)

		#OR gate
		case 8:
			stem_observability(gate_src,fanout,fanoutlist,numDFFs,fanin_dict,combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output)

			or_nor_observability(gate_src,fanin,numDFFs, combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output)

		#NOR gate
		case 9:
			stem_observability(gate_src,fanout,fanoutlist,numDFFs,fanin_dict,combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output)

			or_nor_observability(gate_src,fanin,numDFFs, combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output)

		#XOR gate
		case 3:
			stem_observability(gate_src,fanout,fanoutlist,numDFFs,fanin_dict,combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output)
			xor_xnor_observability(gate_src,fanin,numDFFs, combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output)

		#XNOR gate
		case 4:
			stem_observability(gate_src,fanout,fanoutlist,numDFFs,fanin_dict,combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output)
			xor_xnor_observability(gate_src,fanin,numDFFs, combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output)

		#NOT gate
		case 10:
			stem_observability(gate_src,fanout,fanoutlist,numDFFs,fanin_dict,combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output)

			buf_not_observability(gate_src,fanin,numDFFs, combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output)


		#BUF gate
		case 11:
			stem_observability(gate_src,fanout,fanoutlist,numDFFs,fanin_dict,combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output)

			buf_not_observability(gate_src,fanin,numDFFs, combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output)

		#OUTPUT
		case 2:
			combo_scoap_input[gate_src][0][2]=0
			combo_prob_scoap_input[gate_src][0][2]=1
			if numDFFs > 0:
				seq_scoap_input[gate_src][0][2]=0

		#D_FF
		case 5:
			stem_observability(gate_src,fanout,fanoutlist,numDFFs,fanin_dict,combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output)
			dff_observability(gate_src,fanin,numDFFs, combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output)

	for k in range(0,int(fanin[gate_src])):
		if gtype[int(faninlist[gate_src][k])] ==  Gate.G_DFF.value:
			temp_dff=int(faninlist[gate_src][k])
			evaluate_observability (temp_dff, gtype, fanin, faninlist, fanout, fanoutlist,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output,combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,fanin_dict,numDFFs)


def evaluate_controllability (gate_src, gtype, fanin, faninlist, fanout, fanoutlist,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output,combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,numDFFs ):
	match gtype[gate_src]:
		#INPUT
		case 1:
			combo_scoap_output[gate_src][0]=1
			combo_scoap_output[gate_src][1]=1
			combo_scoap_output[gate_src][2]=INFINITY
			combo_prob_scoap_output[gate_src][0]=0.5
			combo_prob_scoap_output[gate_src][1]=0.5
			combo_prob_scoap_output[gate_src][2]=INFINITY
			if numDFFs > 0:
				seq_scoap_output[gate_src][0]=0
				seq_scoap_output[gate_src][1]=0
				seq_scoap_output[gate_src][2]=INFINITY


		#NAND gate
		case 7:
			list_combo_scoap0=[]
			list_prob_scoap0=[]
			list_seq_scoap0=[]
			list_combo_scoap1=[]
			list_prob_scoap1=[]
			list_seq_scoap1=[]
			for nn in range(0,int(fanin[gate_src])):
				temp_fanin=int(faninlist[gate_src][nn])
				combo_scoap_input[gate_src][nn][0]=combo_scoap_output[temp_fanin][0]
				list_combo_scoap0.append(combo_scoap_input[gate_src][nn][0])
				combo_scoap_input[gate_src][nn][1]=combo_scoap_output[temp_fanin][1]
				list_combo_scoap1.append(combo_scoap_input[gate_src][nn][1])
				combo_scoap_input[gate_src][nn][2]=INFINITY
				combo_prob_scoap_input[gate_src][nn][0]=combo_prob_scoap_output[temp_fanin][0]
				list_prob_scoap0.append(combo_prob_scoap_input[gate_src][nn][0])
				combo_prob_scoap_input[gate_src][nn][1]=combo_prob_scoap_output[temp_fanin][1]
				list_prob_scoap1.append(combo_prob_scoap_input[gate_src][nn][1])
				combo_prob_scoap_input[gate_src][nn][2]=INFINITY
				if numDFFs > 0:
					seq_scoap_input[gate_src][nn][0]=seq_scoap_output[temp_fanin][0]
					list_seq_scoap0.append(seq_scoap_input[gate_src][nn][0])
					seq_scoap_input[gate_src][nn][1]=seq_scoap_output[temp_fanin][1]
					list_seq_scoap1.append(seq_scoap_input[gate_src][nn][1])
					seq_scoap_input[gate_src][nn][2]=INFINITY

			if max(list_combo_scoap1) != INFINITY:
				combo_scoap_output[gate_src][0]=sum(list_combo_scoap1) + 1
			if min(list_combo_scoap0) != INFINITY:
				combo_scoap_output[gate_src][1]=min(list_combo_scoap0) + 1
			combo_scoap_output[gate_src][2]=INFINITY
			if max(list_prob_scoap1) != INFINITY:
				combo_prob_scoap_output[gate_src][0]=np.prod(list_prob_scoap1)
				combo_prob_scoap_output[gate_src][1]=1-(np.prod(list_prob_scoap1))
			combo_prob_scoap_output[gate_src][2]=INFINITY
			if numDFFs > 0:
				if max(list_seq_scoap1) != INFINITY:
					seq_scoap_output[gate_src][0]=sum(list_seq_scoap1)
				if min(list_seq_scoap0) != INFINITY:
					seq_scoap_output[gate_src][1]=min(list_seq_scoap0)
				seq_scoap_output[gate_src][2]=INFINITY

		#AND gate
		case 6:
			list_combo_scoap0=[]
			list_prob_scoap0=[]
			list_seq_scoap0=[]
			list_combo_scoap1=[]
			list_prob_scoap1=[]
			list_seq_scoap1=[]
			for nn in range(0,int(fanin[gate_src])):
				temp_fanin=int(faninlist[gate_src][nn])
				combo_scoap_input[gate_src][nn][0]=combo_scoap_output[temp_fanin][0]
				list_combo_scoap0.append(combo_scoap_input[gate_src][nn][0])
				combo_scoap_input[gate_src][nn][1]=combo_scoap_output[temp_fanin][1]
				list_combo_scoap1.append(combo_scoap_input[gate_src][nn][1])
				combo_scoap_input[gate_src][nn][2]=INFINITY
				combo_prob_scoap_input[gate_src][nn][0]=combo_prob_scoap_output[temp_fanin][0]
				list_prob_scoap0.append(combo_prob_scoap_input[gate_src][nn][0])
				combo_prob_scoap_input[gate_src][nn][1]=combo_prob_scoap_output[temp_fanin][1]
				list_prob_scoap1.append(combo_prob_scoap_input[gate_src][nn][1])
				combo_prob_scoap_input[gate_src][nn][2]=INFINITY
				if numDFFs > 0:
					seq_scoap_input[gate_src][nn][0]=seq_scoap_output[temp_fanin][0]
					list_seq_scoap0.append(seq_scoap_input[gate_src][nn][0])
					seq_scoap_input[gate_src][nn][1]=seq_scoap_output[temp_fanin][1]
					list_seq_scoap1.append(seq_scoap_input[gate_src][nn][1])
					seq_scoap_input[gate_src][nn][2]=INFINITY

			if min(list_combo_scoap0) != INFINITY:
				combo_scoap_output[gate_src][0]=min(list_combo_scoap0) + 1
			if max(list_combo_scoap1) != INFINITY:
				combo_scoap_output[gate_src][1]=sum(list_combo_scoap1) + 1
			combo_scoap_output[gate_src][2]=INFINITY
			if max(list_prob_scoap1) != INFINITY:
				combo_prob_scoap_output[gate_src][0]=1-(np.prod(list_prob_scoap1))
				combo_prob_scoap_output[gate_src][1]=np.prod(list_prob_scoap1)
			combo_prob_scoap_output[gate_src][2]=INFINITY
			if numDFFs > 0:
				if min(list_seq_scoap0) != INFINITY:
					seq_scoap_output[gate_src][0]=min(list_seq_scoap0)
				if max(list_seq_scoap1) != INFINITY:
					seq_scoap_output[gate_src][1]=sum(list_seq_scoap1)
				seq_scoap_output[gate_src][2]=INFINITY

		#OR gate
		case 8:
			list_combo_scoap0=[]
			list_prob_scoap0=[]
			list_seq_scoap0=[]
			list_combo_scoap1=[]
			list_prob_scoap1=[]
			list_seq_scoap1=[]
			for nn in range(0,int(fanin[gate_src])):
				temp_fanin=int(faninlist[gate_src][nn])
				combo_scoap_input[gate_src][nn][0]=combo_scoap_output[temp_fanin][0]
				list_combo_scoap0.append(combo_scoap_input[gate_src][nn][0])
				#print("list_combo_scoap0= ",combo_scoap_input[gate_src][nn][0])
				combo_scoap_input[gate_src][nn][1]=combo_scoap_output[temp_fanin][1]
				list_combo_scoap1.append(combo_scoap_input[gate_src][nn][1])
				#print("list_combo_scoap1= ",combo_scoap_input[gate_src][nn][1])
				combo_scoap_input[gate_src][nn][2]=INFINITY
				combo_prob_scoap_input[gate_src][nn][0]=combo_prob_scoap_output[temp_fanin][0]
				list_prob_scoap0.append(combo_prob_scoap_input[gate_src][nn][0])
				combo_prob_scoap_input[gate_src][nn][1]=combo_prob_scoap_output[temp_fanin][1]
				list_prob_scoap1.append(combo_prob_scoap_input[gate_src][nn][1])
				combo_prob_scoap_input[gate_src][nn][2]=INFINITY
				if numDFFs > 0:
					seq_scoap_input[gate_src][nn][0]=seq_scoap_output[temp_fanin][0]
					list_seq_scoap0.append(seq_scoap_input[gate_src][nn][0])
					seq_scoap_input[gate_src][nn][1]=seq_scoap_output[temp_fanin][1]
					list_seq_scoap1.append(seq_scoap_input[gate_src][nn][1])
					seq_scoap_input[gate_src][nn][2]=INFINITY

			if max(list_combo_scoap0) != INFINITY:
				combo_scoap_output[gate_src][0]=sum(list_combo_scoap0) + 1
			if min(list_combo_scoap1) != INFINITY:
				combo_scoap_output[gate_src][1]=min(list_combo_scoap1) + 1
			combo_scoap_output[gate_src][2]=INFINITY

			#print("max(list_prob_scoap0) = ",max(list_prob_scoap0))
			if max(list_prob_scoap0) != INFINITY:
				combo_prob_scoap_output[gate_src][0]=np.prod(list_prob_scoap0)
				combo_prob_scoap_output[gate_src][1]=1-(np.prod(list_prob_scoap0))
			combo_prob_scoap_output[gate_src][2]=INFINITY

			if numDFFs > 0:
				if max(list_seq_scoap0) != INFINITY:
					seq_scoap_output[gate_src][0]=sum(list_seq_scoap0)
				if min(list_seq_scoap1) != INFINITY:
					seq_scoap_output[gate_src][1]=min(list_seq_scoap1)
				seq_scoap_output[gate_src][2]=INFINITY

		#NOR gate
		case 9:
			list_combo_scoap0=[]
			list_prob_scoap0=[]
			list_seq_scoap0=[]
			list_combo_scoap1=[]
			list_prob_scoap1=[]
			list_seq_scoap1=[]
			for nn in range(0,int(fanin[gate_src])):
				temp_fanin=int(faninlist[gate_src][nn])
				combo_scoap_input[gate_src][nn][0]=combo_scoap_output[temp_fanin][0]
				list_combo_scoap0.append(combo_scoap_input[gate_src][nn][0])
				combo_scoap_input[gate_src][nn][1]=combo_scoap_output[temp_fanin][1]
				list_combo_scoap1.append(combo_scoap_input[gate_src][nn][1])
				combo_scoap_input[gate_src][nn][2]=INFINITY
				combo_prob_scoap_input[gate_src][nn][0]=combo_prob_scoap_output[temp_fanin][0]
				list_prob_scoap0.append(combo_prob_scoap_input[gate_src][nn][0])
				combo_prob_scoap_input[gate_src][nn][1]=combo_prob_scoap_output[temp_fanin][1]
				list_prob_scoap1.append(combo_prob_scoap_input[gate_src][nn][1])
				combo_prob_scoap_input[gate_src][nn][2]=INFINITY
				if numDFFs > 0:
					seq_scoap_input[gate_src][nn][0]=seq_scoap_output[temp_fanin][0]
					list_seq_scoap0.append(seq_scoap_input[gate_src][nn][0])
					seq_scoap_input[gate_src][nn][1]=seq_scoap_output[temp_fanin][1]
					list_seq_scoap1.append(seq_scoap_input[gate_src][nn][1])
					seq_scoap_input[gate_src][nn][2]=INFINITY

			if min(list_combo_scoap1) != INFINITY:
				combo_scoap_output[gate_src][0]=min(list_combo_scoap1) + 1
			if max(list_combo_scoap0) != INFINITY:
				combo_scoap_output[gate_src][1]=sum(list_combo_scoap0) + 1
			combo_scoap_output[gate_src][2]=INFINITY

			if max(list_prob_scoap0) != INFINITY:
				combo_prob_scoap_output[gate_src][0]=1-(np.prod(list_prob_scoap0))
				combo_prob_scoap_output[gate_src][1]=np.prod(list_prob_scoap0)
			combo_prob_scoap_output[gate_src][2]=INFINITY

			if numDFFs > 0:
				if min(list_seq_scoap1) != INFINITY:
					seq_scoap_output[gate_src][0]=min(list_seq_scoap1)
				if max(list_seq_scoap0) != INFINITY:
					seq_scoap_output[gate_src][1]=sum(list_seq_scoap0)
				seq_scoap_output[gate_src][2]=INFINITY
		#XOR gate
		case 3:
			list_combo_scoap0011=[]
			list_prob_scoap0011=[]
			list_seq_scoap0011=[]
			list_combo_scoap0101=[]
			list_prob_scoap0101=[]
			list_seq_scoap0101=[]

			temp_fanin0=int(faninlist[gate_src][0])
			temp_fanin1=int(faninlist[gate_src][1])

			combo_scoap_input[gate_src][0][0]=combo_scoap_output[temp_fanin0][0]
			combo_scoap_input[gate_src][0][1]=combo_scoap_output[temp_fanin0][1]
			combo_scoap_input[gate_src][0][2]=INFINITY

			combo_scoap_input[gate_src][1][0]=combo_scoap_output[temp_fanin1][0]
			combo_scoap_input[gate_src][1][1]=combo_scoap_output[temp_fanin1][1]
			combo_scoap_input[gate_src][1][2]=INFINITY

			if combo_scoap_input[gate_src][0][0] != INFINITY and combo_scoap_input[gate_src][1][0] !=INFINITY:
				list_combo_scoap0011.append(combo_scoap_input[gate_src][0][0]+combo_scoap_input[gate_src][1][0])
			else:
				list_combo_scoap0011.append(INFINITY)

			if combo_scoap_input[gate_src][0][1] != INFINITY and combo_scoap_input[gate_src][1][1] !=INFINITY:
				list_combo_scoap0011.append(combo_scoap_input[gate_src][0][1]+combo_scoap_input[gate_src][1][1])
			else:
				list_combo_scoap0011.append(INFINITY)
			if combo_scoap_input[gate_src][0][0] != INFINITY and combo_scoap_input[gate_src][1][1] != INFINITY:
				list_combo_scoap0101.append(combo_scoap_input[gate_src][0][0]+combo_scoap_input[gate_src][1][1])
			else:
				list_combo_scoap0101.append(INFINITY)
			if combo_scoap_input[gate_src][0][1] != INFINITY and combo_scoap_input[gate_src][1][0] != INFINITY:
				list_combo_scoap0101.append(combo_scoap_input[gate_src][0][1]+combo_scoap_input[gate_src][1][0])
			else:
				list_combo_scoap0101.append(INFINITY)

			combo_prob_scoap_input[gate_src][0][0]=combo_prob_scoap_output[temp_fanin0][0]
			combo_prob_scoap_input[gate_src][0][1]=combo_prob_scoap_output[temp_fanin0][1]
			combo_prob_scoap_input[gate_src][0][2]=INFINITY

			combo_prob_scoap_input[gate_src][1][0]=combo_prob_scoap_output[temp_fanin1][0]
			combo_prob_scoap_input[gate_src][1][1]=combo_prob_scoap_output[temp_fanin1][1]
			combo_prob_scoap_input[gate_src][1][2]=INFINITY


			if combo_prob_scoap_input[gate_src][0][0] != INFINITY and combo_prob_scoap_input[gate_src][1][0] !=INFINITY:
				list_prob_scoap0011.append(combo_prob_scoap_input[gate_src][0][0]*combo_prob_scoap_input[gate_src][1][0])
			else:
				list_prob_scoap0011.append(INFINITY)

			if combo_prob_scoap_input[gate_src][0][1] != INFINITY and combo_prob_scoap_input[gate_src][1][1] !=INFINITY:
				list_prob_scoap0011.append(combo_prob_scoap_input[gate_src][0][1]*combo_prob_scoap_input[gate_src][1][1])
			else:
				list_prob_scoap0011.append(INFINITY)
			if combo_prob_scoap_input[gate_src][0][0] != INFINITY and combo_prob_scoap_input[gate_src][1][1] != INFINITY:
				list_prob_scoap0101.append(combo_prob_scoap_input[gate_src][0][0]*combo_prob_scoap_input[gate_src][1][1])
			else:
				list_prob_scoap0101.append(INFINITY)
			if combo_prob_scoap_input[gate_src][0][1] != INFINITY and combo_prob_scoap_input[gate_src][1][0] != INFINITY:
				list_prob_scoap0101.append(combo_prob_scoap_input[gate_src][0][1]*combo_prob_scoap_input[gate_src][1][0])
			else:
				list_prob_scoap0101.append(INFINITY)

			if min(list_combo_scoap0011) != INFINITY:
				combo_scoap_output[gate_src][0]=min(list_combo_scoap0011) + 1
			if min(list_combo_scoap0101) != INFINITY:
				combo_scoap_output[gate_src][1]=min(list_combo_scoap0101) + 1
			combo_scoap_output[gate_src][2]=INFINITY

			if max(list_prob_scoap0101) != INFINITY:
				combo_prob_scoap_output[gate_src][0]=1-sum(list_prob_scoap0101)
				combo_prob_scoap_output[gate_src][1]=sum(list_prob_scoap0101)
			combo_prob_scoap_output[gate_src][2]=INFINITY

			if numDFFs > 0:
				seq_scoap_input[gate_src][0][0]=seq_scoap_output[temp_fanin0][0]
				seq_scoap_input[gate_src][0][1]=seq_scoap_output[temp_fanin0][1]
				seq_scoap_input[gate_src][0][2]=INFINITY

				seq_scoap_input[gate_src][1][0]=seq_scoap_output[temp_fanin1][0]
				seq_scoap_input[gate_src][1][1]=seq_scoap_output[temp_fanin1][1]
				seq_scoap_input[gate_src][1][2]=INFINITY

				if seq_scoap_input[gate_src][0][0] != INFINITY and seq_scoap_input[gate_src][1][0] !=INFINITY:
					list_seq_scoap0011.append(seq_scoap_input[gate_src][0][0]+seq_scoap_input[gate_src][1][0])
				else:
					list_seq_scoap0011.append(INFINITY)

				if seq_scoap_input[gate_src][0][1] != INFINITY and seq_scoap_input[gate_src][1][1] !=INFINITY:
					list_seq_scoap0011.append(seq_scoap_input[gate_src][0][1]+seq_scoap_input[gate_src][1][1])
				else:
					list_seq_scoap0011.append(INFINITY)
				if seq_scoap_input[gate_src][0][0] != INFINITY and seq_scoap_input[gate_src][1][1] != INFINITY:
					list_seq_scoap0101.append(seq_scoap_input[gate_src][0][0]+seq_scoap_input[gate_src][1][1])
				else:
					list_seq_scoap0101.append(INFINITY)
				if seq_scoap_input[gate_src][0][1] != INFINITY and seq_scoap_input[gate_src][1][0] != INFINITY:
					list_seq_scoap0101.append(seq_scoap_input[gate_src][0][1]+seq_scoap_input[gate_src][1][0])
				else:
					list_seq_scoap0101.append(INFINITY)

				if min(list_seq_scoap0011) != INFINITY:
					seq_scoap_output[gate_src][0]=min(list_seq_scoap0011)
				if min(list_seq_scoap0101) != INFINITY:
					seq_scoap_output[gate_src][1]=min(list_seq_scoap0101)
				seq_scoap_output[gate_src][2]=INFINITY
		#XNOR gate
		case 4:
			list_combo_scoap0011=[]
			list_prob_scoap0011=[]
			list_seq_scoap0011=[]
			list_combo_scoap0101=[]
			list_prob_scoap0101=[]
			list_seq_scoap0101=[]

			temp_fanin0=int(faninlist[gate_src][0])
			temp_fanin1=int(faninlist[gate_src][1])

			combo_scoap_input[gate_src][0][0]=combo_scoap_output[temp_fanin0][0]
			combo_scoap_input[gate_src][0][1]=combo_scoap_output[temp_fanin0][1]
			combo_scoap_input[gate_src][0][2]=INFINITY

			combo_scoap_input[gate_src][1][0]=combo_scoap_output[temp_fanin1][0]
			combo_scoap_input[gate_src][1][1]=combo_scoap_output[temp_fanin1][1]
			combo_scoap_input[gate_src][1][2]=INFINITY

			if combo_scoap_input[gate_src][0][0] != INFINITY and combo_scoap_input[gate_src][1][0] !=INFINITY:
				list_combo_scoap0011.append(combo_scoap_input[gate_src][0][0]+combo_scoap_input[gate_src][1][0])
			else:
				list_combo_scoap0011.append(INFINITY)

			if combo_scoap_input[gate_src][0][1] != INFINITY and combo_scoap_input[gate_src][1][1] !=INFINITY:
				list_combo_scoap0011.append(combo_scoap_input[gate_src][0][1]+combo_scoap_input[gate_src][1][1])
			else:
				list_combo_scoap0011.append(INFINITY)
			if combo_scoap_input[gate_src][0][0] != INFINITY and combo_scoap_input[gate_src][1][1] != INFINITY:
				list_combo_scoap0101.append(combo_scoap_input[gate_src][0][0]+combo_scoap_input[gate_src][1][1])
			else:
				list_combo_scoap0101.append(INFINITY)
			if combo_scoap_input[gate_src][0][1] != INFINITY and combo_scoap_input[gate_src][1][0] != INFINITY:
				list_combo_scoap0101.append(combo_scoap_input[gate_src][0][1]+combo_scoap_input[gate_src][1][0])
			else:
				list_combo_scoap0101.append(INFINITY)

			combo_prob_scoap_input[gate_src][0][0]=combo_prob_scoap_output[temp_fanin0][0]
			combo_prob_scoap_input[gate_src][0][1]=combo_prob_scoap_output[temp_fanin0][1]
			combo_prob_scoap_input[gate_src][0][2]=INFINITY

			combo_prob_scoap_input[gate_src][1][0]=combo_prob_scoap_output[temp_fanin1][0]
			combo_prob_scoap_input[gate_src][1][1]=combo_prob_scoap_output[temp_fanin1][1]
			combo_prob_scoap_input[gate_src][1][2]=INFINITY


			if combo_prob_scoap_input[gate_src][0][0] != INFINITY and combo_prob_scoap_input[gate_src][1][0] !=INFINITY:
				list_prob_scoap0011.append(combo_prob_scoap_input[gate_src][0][0]*combo_prob_scoap_input[gate_src][1][0])
			else:
				list_prob_scoap0011.append(INFINITY)

			if combo_prob_scoap_input[gate_src][0][1] != INFINITY and combo_prob_scoap_input[gate_src][1][1] !=INFINITY:
				list_prob_scoap0011.append(combo_prob_scoap_input[gate_src][0][1]*combo_prob_scoap_input[gate_src][1][1])
			else:
				list_prob_scoap0011.append(INFINITY)
			if combo_prob_scoap_input[gate_src][0][0] != INFINITY and combo_prob_scoap_input[gate_src][1][1] != INFINITY:
				list_prob_scoap0101.append(combo_prob_scoap_input[gate_src][0][0]*combo_prob_scoap_input[gate_src][1][1])
			else:
				list_prob_scoap0101.append(INFINITY)
			if combo_prob_scoap_input[gate_src][0][1] != INFINITY and combo_prob_scoap_input[gate_src][1][0] != INFINITY:
				list_prob_scoap0101.append(combo_prob_scoap_input[gate_src][0][1]*combo_prob_scoap_input[gate_src][1][0])
			else:
				list_prob_scoap0101.append(INFINITY)


			if min(list_combo_scoap0101) != INFINITY:
				combo_scoap_output[gate_src][0]=min(list_combo_scoap0101) + 1
			if min(list_combo_scoap0011) != INFINITY:
				combo_scoap_output[gate_src][1]=min(list_combo_scoap0011) + 1
			combo_scoap_output[gate_src][2]=INFINITY

			if max(list_prob_scoap0011) != INFINITY:
				combo_prob_scoap_output[gate_src][0]=1-sum(list_prob_scoap0011)
				combo_prob_scoap_output[gate_src][1]=sum(list_prob_scoap0011)
			combo_prob_scoap_output[gate_src][2]=INFINITY

			if numDFFs > 0:
				seq_scoap_input[gate_src][0][0]=seq_scoap_output[temp_fanin0][0]
				seq_scoap_input[gate_src][0][1]=seq_scoap_output[temp_fanin0][1]
				seq_scoap_input[gate_src][0][2]=INFINITY

				seq_scoap_input[gate_src][1][0]=seq_scoap_output[temp_fanin1][0]
				seq_scoap_input[gate_src][1][1]=seq_scoap_output[temp_fanin1][1]
				seq_scoap_input[gate_src][1][2]=INFINITY

				if seq_scoap_input[gate_src][0][0] != INFINITY and seq_scoap_input[gate_src][1][0] !=INFINITY:
					list_seq_scoap0011.append(seq_scoap_input[gate_src][0][0]+seq_scoap_input[gate_src][1][0])
				else:
					list_seq_scoap0011.append(INFINITY)

				if seq_scoap_input[gate_src][0][1] != INFINITY and seq_scoap_input[gate_src][1][1] !=INFINITY:
					list_seq_scoap0011.append(seq_scoap_input[gate_src][0][1]+seq_scoap_input[gate_src][1][1])
				else:
					list_seq_scoap0011.append(INFINITY)
				if seq_scoap_input[gate_src][0][0] != INFINITY and seq_scoap_input[gate_src][1][1] != INFINITY:
					list_seq_scoap0101.append(seq_scoap_input[gate_src][0][0]+seq_scoap_input[gate_src][1][1])
				else:
					list_seq_scoap0101.append(INFINITY)
				if seq_scoap_input[gate_src][0][1] != INFINITY and seq_scoap_input[gate_src][1][0] != INFINITY:
					list_seq_scoap0101.append(seq_scoap_input[gate_src][0][1]+seq_scoap_input[gate_src][1][0])
				else:
					list_seq_scoap0101.append(INFINITY)

				if min(list_seq_scoap0101) != INFINITY:
					seq_scoap_output[gate_src][0]=min(list_seq_scoap0101)
				if min(list_seq_scoap0011) != INFINITY:
					seq_scoap_output[gate_src][1]=min(list_seq_scoap0011)
				seq_scoap_output[gate_src][2]=INFINITY

		#NOT gate
		case 10:
			temp_fanin=int(faninlist[gate_src][0])
			combo_scoap_input[gate_src][0][0]=combo_scoap_output[temp_fanin][0]
			#print("inv combo_scoap_input0= ",combo_scoap_input[gate_src][0][0])
			combo_scoap_input[gate_src][0][1]=combo_scoap_output[temp_fanin][1]
			#print("inv combo_scoap_input1= ",combo_scoap_input[gate_src][0][1])
			combo_scoap_input[gate_src][0][2]=INFINITY
			combo_prob_scoap_input[gate_src][0][0]=combo_prob_scoap_output[temp_fanin][0]
			combo_prob_scoap_input[gate_src][0][1]=combo_prob_scoap_output[temp_fanin][1]
			combo_prob_scoap_input[gate_src][0][2]=INFINITY

			if combo_scoap_input[gate_src][0][1] != INFINITY:
				combo_scoap_output[gate_src][0]= combo_scoap_input[gate_src][0][1] + 1
			#print("inv combo_scoap_output0= ",combo_scoap_output[gate_src][0])
			if combo_scoap_input[gate_src][0][0] != INFINITY:
				combo_scoap_output[gate_src][1]= combo_scoap_input[gate_src][0][0] + 1
			#print("inv combo_scoap_output1= ",combo_scoap_output[gate_src][1])
			combo_scoap_output[gate_src][2]=INFINITY
			combo_prob_scoap_output[gate_src][0]=combo_prob_scoap_input[gate_src][0][1]
			combo_prob_scoap_output[gate_src][1]=combo_prob_scoap_input[gate_src][0][0]
			combo_prob_scoap_output[gate_src][2]=INFINITY

			if numDFFs > 0:
				seq_scoap_input[gate_src][0][0]=seq_scoap_output[temp_fanin][0]
				seq_scoap_input[gate_src][0][1]=seq_scoap_output[temp_fanin][1]
				seq_scoap_input[gate_src][0][2]=INFINITY

				seq_scoap_output[gate_src][0]=seq_scoap_input[gate_src][0][1]
				seq_scoap_output[gate_src][1]=seq_scoap_input[gate_src][0][0]
				seq_scoap_output[gate_src][2]=INFINITY


		#BUF gate
		case 11:
			temp_fanin=int(faninlist[gate_src][0])
			combo_scoap_input[gate_src][0][0]=combo_scoap_output[temp_fanin][0]
			combo_scoap_input[gate_src][0][1]=combo_scoap_output[temp_fanin][1]
			combo_scoap_input[gate_src][0][2]=INFINITY
			combo_prob_scoap_input[gate_src][0][0]=combo_prob_scoap_output[temp_fanin][0]
			combo_prob_scoap_input[gate_src][0][1]=combo_prob_scoap_output[temp_fanin][1]
			combo_prob_scoap_input[gate_src][0][2]=INFINITY

			if combo_scoap_input[gate_src][0][0] != INFINITY:
				combo_scoap_output[gate_src][0]= combo_scoap_input[gate_src][0][0] + 1
			if combo_scoap_input[gate_src][0][1] != INFINITY:
				combo_scoap_output[gate_src][1]= combo_scoap_input[gate_src][0][1] + 1
			combo_scoap_output[gate_src][2]=INFINITY
			combo_prob_scoap_output[gate_src][0]=combo_prob_scoap_input[gate_src][0][0]
			combo_prob_scoap_output[gate_src][1]=combo_prob_scoap_input[gate_src][0][1]
			combo_prob_scoap_output[gate_src][2]=INFINITY

			if numDFFs > 0:
				seq_scoap_input[gate_src][0][0]=seq_scoap_output[temp_fanin][0]
				seq_scoap_input[gate_src][0][1]=seq_scoap_output[temp_fanin][1]
				seq_scoap_input[gate_src][0][2]=INFINITY

				seq_scoap_output[gate_src][0]=seq_scoap_input[gate_src][0][0]
				seq_scoap_output[gate_src][1]=seq_scoap_input[gate_src][0][1]
				seq_scoap_output[gate_src][2]=INFINITY

		#OUTPUT
		case 2:
			temp_fanin=int(faninlist[gate_src][0])
			combo_scoap_input[gate_src][0][0]=combo_scoap_output[temp_fanin][0]
			combo_scoap_input[gate_src][0][1]=combo_scoap_output[temp_fanin][1]
			combo_scoap_input[gate_src][0][2]=INFINITY
			combo_prob_scoap_input[gate_src][0][0]=combo_prob_scoap_output[temp_fanin][0]
			combo_prob_scoap_input[gate_src][0][1]=combo_prob_scoap_output[temp_fanin][1]
			combo_prob_scoap_input[gate_src][0][2]=INFINITY

			if numDFFs > 0:
				seq_scoap_input[gate_src][0][0]=seq_scoap_output[temp_fanin][0]
				seq_scoap_input[gate_src][0][1]=seq_scoap_output[temp_fanin][1]
				seq_scoap_input[gate_src][0][2]=INFINITY

		#D_FF
		case 5:
			temp_fanin=int(faninlist[gate_src][0])
			combo_scoap_input[gate_src][0][0]=combo_scoap_output[temp_fanin][0]
			combo_scoap_input[gate_src][0][1]=combo_scoap_output[temp_fanin][1]
			combo_scoap_input[gate_src][0][2]=INFINITY
			combo_prob_scoap_input[gate_src][0][0]=combo_prob_scoap_output[temp_fanin][0]
			combo_prob_scoap_input[gate_src][0][1]=combo_prob_scoap_output[temp_fanin][1]
			combo_prob_scoap_input[gate_src][0][2]=INFINITY

			list0=[]
			list0.append(combo_scoap_input[gate_src][0][0] + CC0_CLK + CC1_CLK + CC0_R)
			if CC1_R > 0:
				list0.append(CC1_R + CC0_CLK)
			#combo_scoap_output[gate_src][0]= combo_scoap_input[gate_src][0][0] + CLOCK_PULSES
			combo_scoap_output[gate_src][0] = min(list0)
			combo_scoap_output[gate_src][1]= combo_scoap_input[gate_src][0][1] + CC0_CLK + CC1_CLK + CC0_R 
			#print("dff combo_scoap_output0= ",combo_scoap_output[gate_src][0])
			#print("dff combo_scoap_output1= ",combo_scoap_output[gate_src][1])

			combo_scoap_output[gate_src][2]=INFINITY
			combo_prob_scoap_output[gate_src][0]=combo_prob_scoap_input[gate_src][0][0]
			combo_prob_scoap_output[gate_src][1]=combo_prob_scoap_input[gate_src][0][1]
			combo_prob_scoap_output[gate_src][2]=INFINITY

			seq_scoap_input[gate_src][0][0]=seq_scoap_output[temp_fanin][0]
			seq_scoap_input[gate_src][0][1]=seq_scoap_output[temp_fanin][1]
			seq_scoap_input[gate_src][0][2]=INFINITY

			if seq_scoap_input[gate_src][0][0] != INFINITY:
				list0=[]
				list0.append(seq_scoap_input[gate_src][0][0] + SC0_CLK + SC1_CLK + SC0_R + 1)
				if SC1_R > 0:
					list0.append(SC1_R + SC0_CLK)
				#seq_scoap_output[gate_src][0]=seq_scoap_input[gate_src][0][0] + 1
				seq_scoap_output[gate_src][0]=min(list0)
			if seq_scoap_input[gate_src][0][1] != INFINITY:
				seq_scoap_output[gate_src][1]=seq_scoap_input[gate_src][0][1] + SC0_CLK + SC1_CLK + SC0_R + 1
			seq_scoap_output[gate_src][2]=INFINITY
	#print("outside MATCH gate_src= ",gate_src)
	#print("outside MATCH fanout[gate_src]= ",int(fanout[gate_src]))
	for k in range(0,int(fanout[gate_src])):
		#print("outside MATCH fanoutlist[gate_src][k]= ",int(fanoutlist[gate_src][k]))
		if gtype[int(fanoutlist[gate_src][k])] ==  Gate.G_DFF.value:
			temp_dff=int(fanoutlist[gate_src][k])
			evaluate_controllability (temp_dff, gtype, fanin, faninlist, fanout, fanoutlist,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output,combo_scoap_input,combo_prob_scoap_input,seq_scoap_input,numDFFs)

				

def copy_array(combo_scoap_input_copy,combo_scoap_input, combo_prob_scoap_input_copy,combo_prob_scoap_input,combo_scoap_output_copy, combo_scoap_output, combo_prob_scoap_output_copy, combo_prob_scoap_output, seq_scoap_input_copy, seq_scoap_input, seq_scoap_output_copy, seq_scoap_output, numDFFs,count,fanin,fanout):
	for i in range(1,count):
		if fanin[i] > 0:
			for j in range(0,int(fanin[i])):
				for k in range(0,3):
					combo_scoap_input_copy[i][j][k]=combo_scoap_input[i][j][k]
					combo_prob_scoap_input_copy[i][j][k]=combo_prob_scoap_input[i][j][k]
					if numDFFs > 0:
						seq_scoap_input_copy[i][j][k]=seq_scoap_input[i][j][k]
		if fanout[i] > 0:
			for k in range(0,3):
				combo_scoap_output_copy[i][k]=combo_scoap_output[i][k]
				combo_prob_scoap_output_copy[i][k]=combo_prob_scoap_output[i][k]
				if numDFFs > 0:
					seq_scoap_output_copy[i][k]=seq_scoap_output[i][k]

def compare_arrays(combo_scoap_input_copy,combo_scoap_input, combo_prob_scoap_input_copy,combo_prob_scoap_input,combo_scoap_output_copy, combo_scoap_output, combo_prob_scoap_output_copy, combo_prob_scoap_output, seq_scoap_input_copy, seq_scoap_input, seq_scoap_output_copy, seq_scoap_output, numDFFs, count, fanin, fanout,flag):
	#print("flag1= ",flag)
	for i in range(1,count):
		if fanin[i] > 0:
			for j in range(0,int(fanin[i])):
				for k in range(0,3):
					#print(combo_scoap_input_copy[i][j][k])
					#print(combo_scoap_input[i][j][k])
					
					if combo_scoap_input_copy[i][j][k]!=combo_scoap_input[i][j][k]:
						#print("check1")
						flag=1
						break
					#if combo_prob_scoap_input_copy[i][j][k]!=combo_prob_scoap_input[i][j][k] or combo_prob_scoap_input[i][j][0] == INFINITY or combo_prob_scoap_input[i][j][1] == INFINITY:
						#print("check2")
					#	flag=1
					#	break
					if numDFFs > 0:
						if seq_scoap_input_copy[i][j][k]!=seq_scoap_input[i][j][k]:
							#print("check3")
							flag=1
							break
		if flag==1:
			break

		if fanout[i] > 0:
			for k in range(0,3):
				#print("combo_scoap_output_copy= ",combo_scoap_output_copy[i][k])
				#print("combo_scoap_output= ",combo_scoap_output[i][k])

				if combo_scoap_output_copy[i][k]!=combo_scoap_output[i][k]:
					#print("check4")
					flag=1
					break
				#if combo_prob_scoap_output_copy[i][k]!=combo_prob_scoap_output[i][k] or combo_prob_scoap_output[i][0] == INFINITY or combo_prob_scoap_output[i][1] == INFINITY:
					#print("check5")
				#	flag=1
				#	break
				if numDFFs > 0:
					if seq_scoap_output_copy[i][k]!=seq_scoap_output[i][k]:
						#print("check6")
						flag=1
						break
		if flag==1:
			break
	
	return flag


def write_outfiles(combo_scoap_input, combo_prob_scoap_input,combo_scoap_output, combo_prob_scoap_output, seq_scoap_input, seq_scoap_output, numDFFs, count, fanin, fanout,gtype):

	out_file_combo_scoap=sys.argv[1] + "." + sys.argv[2] + ".combo.scoap"
	out_file_prob_scoap=sys.argv[1] + "." + sys.argv[2] + ".prob.scoap"

	if numDFFs > 0:
		out_file_seq_scoap=sys.argv[1] + "." + sys.argv[2] +".seq.scoap"
		out_file_seq_csv=sys.argv[1] + "." + sys.argv[2] +".seq.csv"
		o_file_seq_scoap = open(out_file_seq_scoap,"w")
		o_file_seq_scoap.write(str(count)+"\n")
		o_file_seq_csv = open(out_file_seq_csv,"w")
		o_file_seq_csv.write("ff_id,"+"num_fanout,"+"CC0,"+"CC1,"+"CO,"+"SC0,"+"SC1,"+"SO"+"\n")

	o_file_combo_scoap = open(out_file_combo_scoap,"w")
	o_file_combo_scoap.write(str(count)+"\n")

	o_file_prob_scoap = open(out_file_prob_scoap,"w")
	o_file_prob_scoap.write(str(count)+"\n")

	for i in range(1,count):
		o_file_combo_scoap.write(str(i)+" "+str(int(gtype[i]))+" "+str(int(fanin[i]))+" ")
		o_file_prob_scoap.write(str(i)+" "+str(int(gtype[i]))+" "+str(int(fanin[i]))+" ")
		if numDFFs > 0:
			o_file_seq_scoap.write(str(i)+" "+str(int(gtype[i]))+" "+str(int(fanin[i]))+" ")
			if (gtype[i]==5):
				o_file_seq_csv.write(str(i)+","+str(int(fanout[i]))+",")

		if fanin[i] > 0:
			for j in range(0,int(fanin[i])):
				o_file_combo_scoap.write("("+str(combo_scoap_input[i][j][0])+"/"+str(combo_scoap_input[i][j][1])+"/"+str(combo_scoap_input[i][j][2])+")"+" ")
				o_file_prob_scoap.write("("+str(combo_prob_scoap_input[i][j][0])+"/"+str(combo_prob_scoap_input[i][j][1])+"/"+str(combo_prob_scoap_input[i][j][2])+")"+" ")
				if numDFFs > 0:
					o_file_seq_scoap.write("("+str(seq_scoap_input[i][j][0])+"/"+str(seq_scoap_input[i][j][1])+"/"+str(seq_scoap_input[i][j][2])+")"+" ")
					if (gtype[i]==5):
						o_file_seq_csv.write(str(seq_scoap_input[i][j][0])+","+str(seq_scoap_input[i][j][1])+","+str(seq_scoap_input[i][j][2])+",")

			
		if fanout[i] > 0:
			o_file_combo_scoap.write(str(int(fanout[i]))+" "+"("+str(combo_scoap_output[i][0])+"/"+str(combo_scoap_output[i][1])+"/"+str(combo_scoap_output[i][2])+")"+"\n")
			o_file_prob_scoap.write(str(int(fanout[i]))+" "+"("+str(combo_prob_scoap_output[i][0])+"/"+str(combo_prob_scoap_output[i][1])+"/"+str(combo_prob_scoap_output[i][2])+")"+"\n")
			if numDFFs > 0:
				o_file_seq_scoap.write(str(int(fanout[i]))+" "+"("+str(seq_scoap_output[i][0])+"/"+str(seq_scoap_output[i][1])+"/"+str(seq_scoap_output[i][2])+")"+"\n")
				if (gtype[i]==5):
					o_file_seq_csv.write(str(seq_scoap_output[i][0])+","+str(seq_scoap_output[i][1])+","+str(seq_scoap_output[i][2])+"\n")
		else:
			o_file_combo_scoap.write(str(int(fanout[i]))+"\n")
			o_file_prob_scoap.write(str(int(fanout[i]))+"\n")
			if numDFFs > 0:
				o_file_seq_scoap.write(str(int(fanout[i]))+"\n")


	o_file_combo_scoap.close()
	o_file_prob_scoap.close()
	if numDFFs > 0:
		o_file_seq_scoap.close()
		o_file_seq_csv.close()

class Gate(Enum):
	G_JUNK   =  0
	G_INPUT  =  1
	G_OUTPUT =  2
	G_XOR    =  3
	G_XNOR   =  4
	G_DFF    =  5
	G_AND    =  6
	G_NAND   =  7
	G_OR	 =  8
	G_NOR    =  9
	G_NOT    =  10
	G_BUF    =  11
	G_TIE1   =  12
	G_TIE0   =  13
	G_PSI    =  14
	G_PSO    =  15


lev_file=sys.argv[1] + ".lev"
vec_file=sys.argv[1] + ".vec"

try:
	with open(lev_file, "r") as file:
		content = file.read()
		print("File",lev_file," found")
		#print(content)
except FileNotFoundError:
	print("Error: The file ",lev_file," was not found.")


line_number=0
gate_count=0
numInputs=0
numOutputs=0
numDFFs=0
maxlevels=0
numgates=0
with open(lev_file, "r") as f:
	for line in f:
		line_number=line_number+1
		# Assuming space-separated values
		parts = line.split() 
		if line_number==1:
			count=int(parts[0])
			gate_count=count-1
			gtype=np.empty(count*2)
			fanin=np.empty(count*2)
			fanout=np.empty(count*2)
			levelNum=np.empty(count*2)
			dff=np.empty(count)
			pout=np.empty(count)
			pin=np.empty(count)
			faninlist=np.empty((count*2,count))
			fanoutlist=np.empty((count*2,count))
			gate_at_level=np.empty((5000,count*2))
			EventList=np.empty((5000,count*2))
			num_gate_per_level=np.zeros(5000,dtype=int)
			value=np.empty(count*2,dtype=object)

			
		if line_number>2:
			if line_number < count+2:
				numgates += 1
				gatenum=int(parts[0])
				f1=int(parts[1])
				f2=int(parts[2])
				f3=int(parts[3])

				gtype[gatenum]=f1
				if gtype[gatenum] > 13:
					print("gate ",gatenum," is an unimplemented gate type")
				elif gtype[gatenum] == Gate.G_INPUT.value :
					numInputs += 1
					pin[numInputs]=gatenum
				elif gtype[gatenum] == Gate.G_OUTPUT.value :
					numOutputs += 1
					pout[numOutputs]=gatenum
					#print("Level of PO ",gatenum," = ",f2)
				elif gtype[gatenum] == Gate.G_DFF.value :
					numDFFs += 1
					dff[numDFFs]=gatenum


				#levenNum[gatenum]= (f2+5)/5;
				levelNum[gatenum] = f2

				if f2 >= maxlevels:
					maxlevels=f2 + 5; 

				fanin[gatenum]=f3

				f4=int(parts[3+(2*f3)+1])
				fanout[gatenum]=f4

total_levels = int(maxlevels/5)

fanin_dict=np.empty((count,count))
fanout_dict=np.empty((count,count))
combo_scoap_input=np.empty((count,1000,3))
combo_scoap_output=np.empty((count,3))
combo_prob_scoap_input=np.empty((count,1000,3))
combo_prob_scoap_output=np.empty((count,3))

#combo_scoap_input_copy=np.empty((count,count,3))
#combo_scoap_output_copy=np.empty((count,3))
#combo_prob_scoap_input_copy=np.empty((count,count,3))
#combo_prob_scoap_output_copy=np.empty((count,3))

#if numDFFs > 0:
seq_scoap_input=np.empty((count,1000,3))
seq_scoap_output=np.empty((count,3))

#seq_scoap_input_copy=np.empty((count,count,3))
#seq_scoap_output_copy=np.empty((count,3))

combo_scoap_input_copy=copy.deepcopy(combo_scoap_input)
combo_prob_scoap_input_copy=copy.deepcopy(combo_prob_scoap_input)
combo_scoap_output_copy=copy.deepcopy(combo_scoap_output)
combo_prob_scoap_output_copy=copy.deepcopy(combo_prob_scoap_output)
seq_scoap_input_copy=copy.deepcopy(seq_scoap_input)
seq_scoap_output_copy=copy.deepcopy(seq_scoap_output)


line_number=0
#numDFFs=0
#numInputs=0
#numOutputs=0
with open(lev_file, "r") as f:
	for line in f:
		line_number=line_number+1
		# Assuming space-separated values
		parts = line.split() 

		if line_number>2:
			if line_number < count+2:
				gatenum=int(parts[0])
				f1=int(parts[1])
				f2=int(parts[2])
				f3=int(parts[3])
				gtype[gatenum]=f1
				if gtype[gatenum] > 13:
					print("gate ",gatenum," is an unimplemented gate type")
				elif gtype[gatenum] == Gate.G_INPUT.value :
					#numInputs += 1
					combo_scoap_output[gatenum][0]=1
					combo_scoap_output[gatenum][1]=1
					combo_scoap_output[gatenum][2]=INFINITY
					combo_prob_scoap_output[gatenum][0]=0.5
					combo_prob_scoap_output[gatenum][1]=0.5
					combo_prob_scoap_output[gatenum][2]=INFINITY
					if numDFFs > 0:
						seq_scoap_output[gatenum][0]=0
						seq_scoap_output[gatenum][1]=0
						seq_scoap_output[gatenum][2]=INFINITY
				elif gtype[gatenum] == Gate.G_OUTPUT.value :
					combo_scoap_input[gatenum][0][0]=0
					combo_scoap_input[gatenum][0][1]=0
					combo_scoap_input[gatenum][0][2]=INFINITY
					combo_prob_scoap_input[gatenum][0][0]=1
					combo_prob_scoap_input[gatenum][0][1]=1
					combo_prob_scoap_input[gatenum][0][2]=INFINITY
					if numDFFs > 0:
						seq_scoap_input[gatenum][0][0]=0
						seq_scoap_input[gatenum][0][1]=0
						seq_scoap_input[gatenum][0][2]=INFINITY
					#numOutputs += 1
					#pout[numOutputs]=gatenum
				#elif gtype[gatenum] == Gate.G_DFF.value :
					#numDFFs += 1
					#dff[numDFFs]=gatenum

				#levenNum[gatenum]= (f2+5)/5;
				levelNum[gatenum] = f2
				#levelNum[count-1+numDFFs] = int(maxlevels-5)

				num_gate_per_level[f2] = num_gate_per_level[f2] + 1
				gate_at_level[f2][num_gate_per_level[f2]] = gatenum;
				fanin[gatenum]=f3
				f4=int(parts[3+(2*f3)+1])
				fanout[gatenum]=f4

				for i in range(0,f3):
					faninlist[gatenum][i]=int(parts[3+(i+1)])
					fanin_dict[gatenum][int(faninlist[gatenum][i])]=i
					if gtype[gatenum] != Gate.G_OUTPUT.value:
						combo_scoap_input[gatenum][i][0]=INFINITY
						combo_scoap_input[gatenum][i][1]=INFINITY
						combo_scoap_input[gatenum][i][2]=INFINITY
						combo_prob_scoap_input[gatenum][i][0]=INFINITY
						combo_prob_scoap_input[gatenum][i][1]=INFINITY
						combo_prob_scoap_input[gatenum][i][2]=INFINITY
						if numDFFs > 0:
							seq_scoap_input[gatenum][i][0]=INFINITY
							seq_scoap_input[gatenum][i][1]=INFINITY
							seq_scoap_input[gatenum][i][2]=INFINITY

			
				for i in range(0,f4):
					fanoutlist[gatenum][i]=int(parts[3+(2*f3)+1+(i+1)])
					fanout_dict[gatenum][int(fanoutlist[gatenum][i])]=i
					if gtype[gatenum] != Gate.G_INPUT.value:
						combo_scoap_output[gatenum][0]=INFINITY
						combo_scoap_output[gatenum][1]=INFINITY
						combo_scoap_output[gatenum][2]=INFINITY
						combo_prob_scoap_output[gatenum][0]=INFINITY
						combo_prob_scoap_output[gatenum][1]=INFINITY
						combo_prob_scoap_output[gatenum][2]=INFINITY
						if numDFFs > 0:
							seq_scoap_output[gatenum][0]=INFINITY
							seq_scoap_output[gatenum][1]=INFINITY
							seq_scoap_output[gatenum][2]=INFINITY



print("Successfully read in circuit:")
print(numInputs," PIs.")
print(numOutputs," POs.")
print(numDFFs," DFFs.")
print(numgates," total number of gates.")
print(total_levels," levels in the circuit.")
print("\n")

#polevel = int(maxlevels -5)

#line_number=0

flag=1
iteration=0
while flag==1:
#while iteration < 16:
	flag=0
	iteration += 1
	print("Iteration ",iteration)

	copy_array(combo_scoap_input_copy,combo_scoap_input, combo_prob_scoap_input_copy,combo_prob_scoap_input,combo_scoap_output_copy, combo_scoap_output, combo_prob_scoap_output_copy, combo_prob_scoap_output, seq_scoap_input_copy, seq_scoap_input, seq_scoap_output_copy, seq_scoap_output, numDFFs, count, fanin, fanout)

	print("Calculating the SCOAP Controllability numbers")
	for i in range(0,maxlevels,5):
		for js in range(1,num_gate_per_level[i]+1):
			j=int(gate_at_level[i][js])
			if gtype[j] != Gate.G_DFF.value:
				evaluate_controllability (j, gtype, fanin, faninlist, fanout, fanoutlist,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output,combo_scoap_input,combo_prob_scoap_input,seq_scoap_input, numDFFs)
				
	flag=compare_arrays(combo_scoap_input_copy,combo_scoap_input, combo_prob_scoap_input_copy,combo_prob_scoap_input,combo_scoap_output_copy, combo_scoap_output, combo_prob_scoap_output_copy, combo_prob_scoap_output, seq_scoap_input_copy, seq_scoap_input, seq_scoap_output_copy, seq_scoap_output, numDFFs, count, fanin, fanout,flag)
	


flag=1
iteration=0
while flag==1:
#while iteration < 16:
	flag=0
	iteration += 1
	print("Iteration ",iteration)

	copy_array(combo_scoap_input_copy,combo_scoap_input, combo_prob_scoap_input_copy,combo_prob_scoap_input,combo_scoap_output_copy, combo_scoap_output, combo_prob_scoap_output_copy, combo_prob_scoap_output, seq_scoap_input_copy, seq_scoap_input, seq_scoap_output_copy, seq_scoap_output, numDFFs, count, fanin, fanout)

	print("Calculating the SCOAP Observability numbers")
	level=int(maxlevels-5)
	while level >= 0:
		for js in range(1,num_gate_per_level[level]+1):
			j=int(gate_at_level[level][js])
			if gtype[j] != Gate.G_DFF.value:
				#print("obser gate_src = ",j)
				#print("obser gate_type = ",gtype[j])
				evaluate_observability (j, gtype, fanin, faninlist, fanout, fanoutlist,combo_scoap_output,combo_prob_scoap_output,seq_scoap_output,combo_scoap_input,combo_prob_scoap_input,seq_scoap_input, fanin_dict, numDFFs)

		level=level-5


	flag=compare_arrays(combo_scoap_input_copy,combo_scoap_input, combo_prob_scoap_input_copy,combo_prob_scoap_input,combo_scoap_output_copy, combo_scoap_output, combo_prob_scoap_output_copy, combo_prob_scoap_output, seq_scoap_input_copy, seq_scoap_input, seq_scoap_output_copy, seq_scoap_output, numDFFs, count, fanin, fanout,flag)

	#print("flag2= ",flag)


write_outfiles(combo_scoap_input, combo_prob_scoap_input,combo_scoap_output, combo_prob_scoap_output, seq_scoap_input, seq_scoap_output, numDFFs, count, fanin, fanout,gtype)
