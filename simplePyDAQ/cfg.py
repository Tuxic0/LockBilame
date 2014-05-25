'''
Created on 21 mai 2014

@author: Thibaut
'''

from PyDAQmx import *

DEF_BUFF=int(1e3)#"buffer"
DEF_NAME=""#"name"
DEF_FS=1e3#"freq_smpl"
DEF_ACQ=DAQmx_Val_ContSamps#"acq_mode"
DEF_MIN=-10.#"min_val"
DEF_Max=10.#"max_val"
DEF_CLK=""#"clk"
DEF_EDGE=DAQmx_Val_Rising
DEF_TERM_CFG=DAQmx_Val_Cfg_Default

DEF_CHASSIS="cDAQ9184-COM"
DEF_MOD="Mod4"
DEF_CHAN=("ao0",)

DEF_CHASSIS_TEST="cDAQ1"
DEF_MOD_TEST="Mod4"
DEF_CHAN_TEST=("ao0",)

DEF_CHASSIS_IN="cDAQ9184-COM"
DEF_MOD_IN="Mod1"
DEF_CHAN_IN=("ai0","ai1", "ai2")

DEF_CHASSIS_IN_TEST="cDAQ1"
DEF_MOD_IN_TEST="Mod1"
DEF_CHAN_IN_TEST=("ai0","ai1", "ai2")