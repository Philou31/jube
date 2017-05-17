#!/usr/bin/env python
###################################################################
#                create_tex.py                                    #
#  Author:                                                        #
#    - Matthieu Haefele                                           #
#      matthieu.haefele@maisondelasimulation.fr                   #
#      Maison de la Simulation USR3441                            #
#    - Sebastian Luehrs                                           #
#      s.luehrs@fz-juelich.de                                     #
#      Forschungszentrum Juelich GmbH                             #
#                                                                 #
#  Generates a Tex tabular out of JSON metric files               #
###################################################################

import argparse
import json

def load_dic(file_name):
  f = open(file_name, "r")
  d = json.loads(f.read())
  f.close()
  return d

def write_group(group_name, group, experiment, to_write):
  to_write = ''
  nb_item = len(group)
  first = True
  for m in group:
    if first:
      to_write += "\\multirow{%d}{*}{\\rotatebox{90}{%s}} & %s "%(nb_item, group_name, m.replace("%","\%"))
      first = False
    else:
      to_write += " & %s "%(m.replace("%","\%"))

    for e in experiment:
      if m in e and e[m] is not None:
        if type(e[m]) == float:
          to_write += '& %.2f '%e[m]
        elif type(e[m]) == int:
          to_write += '& %d '%e[m]
        else:
          to_write += '& %s '%str(e[m])
      else:
        to_write += '& N.A. '
    to_write += '\\\\\n\\cline{2-%d}\n'%(len(experiment)+2)
  return to_write

def build_final_metrics(metrics):
  result={}
  result['Total Time (s)'] = metrics.get('time_ref',None)
  result['Time IO (s)'] = metrics.get('io_time',None)
  result['Time MPI (s)'] = metrics.get('time_mpi_no_mpiio',None)
  result["Memory vs Compute Bound"] = metrics.get('mem_vs_cmp',None)
  result['Load Imbalance (%)'] = metrics.get('critical_path_imbalance_ratio',None)
  if result['Load Imbalance (%)'] is not None:
    result['Load Imbalance (%)'] *= 100
  result["IO Volume (MB)"] = metrics.get('io_volume',None)
  result["Calls (nb)"] = metrics.get('io_calls',None)
  result["Throughput (MB/s)"] = metrics.get('io_throughput',None)
  result["Individual IO Access (kB)"] = metrics.get('avg_io_ac_size',None)
  if result["Individual IO Access (kB)"] is not None:
    result["Individual IO Access (kB)"] /= 1024.
  result['P2P Calls (nb)'] = metrics.get('num_p2p_calls',None)
  result['P2P Calls (s)'] = metrics.get('p2p_comm_time',None)
  result['P2P Calls Message Size (kB)'] = metrics.get('p2p_message_size',None)
  if result["P2P Calls Message Size (kB)"] is not None:
    result["P2P Calls Message Size (kB)"] /= 1024
  result['Collective Calls (nb)'] = metrics.get('num_coll_calls',None)
  result['Collective Calls (s)'] = metrics.get('coll_comm_time',None)
  result['Coll. Calls Message Size (kB)'] = metrics.get('coll_message_size',None)
  if result['Coll. Calls Message Size (kB)'] is not None:
    result['Coll. Calls Message Size (kB)'] /= 1024
  result['Synchro / Wait MPI (s)'] = metrics.get('time_delay_mpi',None)
  result['Ratio Synchro / Wait MPI (%)'] = metrics.get('delay_mpi_ratio',None)
  if result['Ratio Synchro / Wait MPI (%)'] is not None:
    result['Ratio Synchro / Wait MPI (%)'] *= 100
  result['Time OpenMP (s)'] = metrics.get('time_omp',None)
  result['Ratio OpenMP (%)'] = metrics.get('omp_ratio',None)
  if result['Ratio OpenMP (%)'] is not None:
    result['Ratio OpenMP (%)'] *= 100
  result['Synchro / Wait OpenMP (s)'] = metrics.get('time_delay_omp',None)
  result['Ratio Synchro / Wait OpenMP (%)'] = metrics.get('delay_omp_ratio',None)
  if result['Ratio Synchro / Wait OpenMP (%)'] is not None:
    result['Ratio Synchro / Wait OpenMP (%)'] *= 100
  result["Memory Footprint"] = metrics.get('mem',None)
  result["Cache Usage Intensity"] = metrics.get('PAPI_L3_TCH_RATIO',None)
  result["IPC"] = metrics.get('PAPI_TOT_INS_RATIO',None)
  result["Runtime without vectorisation (s)"] = metrics.get('time_no-vec',None)
  result["Runtime without FMA (s)"] = metrics.get('time_no-fma',None)
  result["Vectorisation efficiency"] = metrics.get('vec_eff',None)
  result["FMA efficiency"] = metrics.get('fma_eff',None)
  return result

def tex(args):
  global_metrics=["Global", "Total Time (s)", "Time IO (s)", "Time MPI (s)", "Memory vs Compute Bound", "Load Imbalance (%)"]

  io_metrics=["IO", "IO Volume (MB)", "Calls (nb)", "Throughput (MB/s)", "Individual IO Access (kB)"]
  mpi_mterics=["MPI", "P2P Calls (nb)", "P2P Calls (s)", "P2P Calls Message Size (kB)", "Collective Calls (nb)", "Collective Calls (s)", "Coll. Calls Message Size (kB)", "Synchro / Wait MPI (s)", "Ratio Synchro / Wait MPI (%)"]

  node_metrics=["Node", "Time OpenMP (s)", "Ratio OpenMP (%)", "Synchro / Wait OpenMP (s)", "Ratio Synchro / Wait OpenMP (%)"]

  memory_metrics=["Mem", "Memory Footprint", "Cache Usage Intensity"]
 
  cpu_metrics=["Core", "IPC", "Runtime without vectorisation (s)", "Vectorisation efficiency", "Runtime without FMA (s)", "FMA efficiency"]

  to_write = '\\begin{tabular}{|l|c|'
  for i in range(len(args.json_file)):
    to_write += 'c|'
  to_write += '}\n'
  to_write += "\\hline\n & Metric name "
  experiment = []
  for f_name in args.json_file:
    to_write += '& ' + f_name.replace("_","\_") + ' '
    experiment.append(build_final_metrics(load_dic(f_name)))
  to_write += '\\\\\n\\hline\n'

  #to_write += write_group(global_metrics, experiment, to_write)
  for g in [global_metrics, io_metrics, mpi_mterics, node_metrics, memory_metrics, cpu_metrics]:
    to_write += write_group(g[0], g[1:], experiment, to_write)
    to_write += '\n\\hline\n'

  to_write += '\\end{tabular}\n'
  f = open(args.output, "w")
  f.write(to_write)
  f.close()

def build_parser():
  parser = argparse.ArgumentParser()
  parser.add_argument('-o','--output', default="out.tex", help='name of the output file (default out.tex)')
  parser.add_argument('json_file', nargs='+', help='json files to put in the table')
  parser.set_defaults(func=tex)
  return parser

if __name__ == '__main__':
  p =  build_parser()
  args = p.parse_args()
  args.func(args)

