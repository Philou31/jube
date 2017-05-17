#!/usr/bin/env python
###################################################################/
#                extract_metrics.py                               #
#                                                                 #
#  Author:                                                        #
#     - Matthieu Haefele                                          #
#       matthieu.haefele@maisondelasimulation.fr                  #
#       Maison de la Simulation USR3441                           #
#     - Sebastian Luehrs                                          #
#       s.luehrs@fz-juelich.de                                    #
#       Forschungszentrum Juelich GmbH                            #
#  Allow the extraction of metrics from different types of        #
#  trace and log files                                            #
#  Created in the context of EoCoE                                #
###################################################################

from __future__ import (print_function)

import os
import subprocess
import re
import math
import json
import argparse

def get_output(cmd, stdout=True):
  lines=[]
  if stdout:
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for m in proc.stdout:
      lines.append(m[:-1])
  else:
    proc= subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    for m in proc.stderr:
      lines.append(m[:-1])
  return lines


def is_number(s):
  """Checks weather the given string can be converted into a float value."""
  try:
    float(s)
    return True
  except ValueError:
    return False

def avg_non_zero(array):
  return avg([i for i in array if i != 0])

def avg(array):
  """Average calculation function"""
  if len(array) > 0:
    return sum(array)/len(array)
  else: 
    return None

def extract_cube(filename, cube_name, combination_option, res_type=float):
  """Extract cube dump data"""
  cmd = 'cube_dump -m {0} -x {1} -c roots -z incl {2}'.format(cube_name, combination_option, filename)
  answer = get_output(cmd)
  result = None
  for s in answer:
    if re.search(r"\(id=\d+\)",s):
      new_result = map(res_type,[i for i in re.split('\s+',s)[1:] if i != "" and is_number(i)])
      if result is None:
        result = new_result
      else:
        result = [i[0] + i[1] for i in zip(result,new_result)]
  return result

def extract_metrics_papi(args):
  """Extract papi metrics"""

  metrics = {'PAPI_L3_TCA' : ['PAPI_L3_TCA','incl',int,avg_non_zero],
             'PAPI_L3_TCM' : ['PAPI_L3_TCM','incl',int,avg_non_zero],
             'PAPI_TOT_INS' : ['PAPI_TOT_INS','incl',int,avg_non_zero],
             'PAPI_TOT_CYC' : ['PAPI_TOT_CYC','incl',int,avg_non_zero]
             }

  combined_metrics = {'PAPI_L3_TCH_RATIO': [('PAPI_L3_TCA','PAPI_L3_TCM'),float,avg_non_zero],
                      'PAPI_TOT_INS_RATIO': [('PAPI_TOT_INS','PAPI_TOT_CYC'),float,avg_non_zero]}

  result = dict()

  #Extraction
  for metric in metrics:
    result[metric] = extract_cube(args.profile_file,metrics[metric][0],metrics[metric][1],metrics[metric][2])

  #Combination
  for metric in combined_metrics:
    result[metric] = None
    for other_metric in combined_metrics[metric][0]:
      if result[other_metric] is None:
        break;
      else:
        if metric == 'PAPI_L3_TCH_RATIO':
          result[metric] = [1 - (1.*b) / a if a != 0 and b != 0 else 0 for a,b in zip(result['PAPI_L3_TCA'],
                                                                                      result['PAPI_L3_TCM'])]
        if metric == 'PAPI_TOT_INS_RATIO':
          result[metric] = [(1.*a) / b if a != 0 and b != 0 else 0 for a,b in zip(result['PAPI_TOT_INS'],
                                                                                  result['PAPI_TOT_CYC'])]

  # Aggregation
  for metric in metrics:
    aggregation = metrics[metric][3]
    datatype = metrics[metric][2]
    if result[metric] is not None:
      result[metric] = datatype(aggregation(result[metric]))
  for metric in combined_metrics:
    aggregation = combined_metrics[metric][2]
    datatype = combined_metrics[metric][1]
    if result[metric] is not None:
      result[metric] = datatype(aggregation(result[metric]))

  dump_json(dict([(tagged_metric(key,args),value) for key,value in result.items()]),args.output)

def extract_metrics_scalasca(args):
  """Extract scalasca MPI and OMP metrics"""

  metrics = {'total_time_scalasca'     : ['time','incl',float,max],
             'time_mpi'                : ['mpi','incl',float,avg],
             'time_mpiio_scalasca'     : ['mpi_io','incl',float,avg],
             'critical_path'           : ['critical_path','incl',float,sum],
             'critical_path_imbalance' : ['critical_path_imbalance','incl',float,sum],
             'num_p2p_calls'           : ['comms_p2p','incl',int,avg],
             'num_coll_calls'          : ['comms_coll','incl',int,avg],
             'p2p_comm_time'           : ['mpi_point2point','incl',float,avg],
             'coll_comm_time'          : ['mpi_collective','incl',float,avg],
             'total_coll_message_size' : ['bytes_coll','incl',int,avg],
             'total_p2p_message_size'  : ['bytes_p2p','incl',int,avg],
             'time_mpi_barrier_wait'   : ['mpi_barrier_wait','incl',float,avg],
             'time_mpi_latesender'     : ['mpi_latesender','incl',float,avg],
             'time_mpi_latereceiver'   : ['mpi_latereceiver','incl',float,avg],
             'time_mpi_latebroadcast'  : ['mpi_latebroadcast','incl',float,avg],
             'time_mpi_wait_nxn'       : ['mpi_wait_nxn','incl',float,avg],
             'time_omp_idle_threads'   : ['omp_idle_threads','incl',float,avg],
             'time_delay_omp'          : ['omp_time','incl',float,avg]
            }

  combined_metrics_order=['time_mpi_no_mpiio','coll_message_size','p2p_message_size','time_delay_mpi',
                          'delay_mpi_ratio','time_omp','delay_omp_ratio','omp_ratio']
  combined_metrics = {'time_mpi_no_mpiio': [('time_mpi','time_mpiio_scalasca'),float,avg],
                      'coll_message_size': [('total_coll_message_size','num_coll_calls'),int,avg],
                      'p2p_message_size' : [('total_p2p_message_size','num_p2p_calls'),int,avg],
                      'time_delay_mpi'   : [('time_mpi_barrier_wait','time_mpi_latesender',
                                             'time_mpi_latereceiver','time_mpi_latebroadcast',
                                             'time_mpi_wait_nxn'),float,avg],
                      'delay_mpi_ratio'  : [('time_delay_mpi','time_mpi'),float,avg],
                      'time_omp'         : [('total_time_scalasca','time_omp_idle_threads'),float,avg],
                      'delay_omp_ratio'  : [('time_delay_omp','time_omp'),float,avg],
                      'omp_ratio'        : [('total_time_scalasca','time_omp'),float,avg]
                     }

  combined_metrics_agg = {'critical_path_imbalance_ratio': ('critical_path','critical_path_imbalance')}

  result = dict()

  # Extraction
  for metric in metrics:
    result[metric] = extract_cube(args.trace_file,metrics[metric][0],metrics[metric][1],metrics[metric][2])

  #Combination (element wise)
  for metric in combined_metrics_order:
    result[metric] = None
    for other_metric in combined_metrics[metric][0]:
      if result[other_metric] is None:
        break;
    else:
      if metric == 'time_mpi_no_mpiio':
        result[metric] = [a - b for a,b in zip(result['time_mpi'],result['time_mpiio_scalasca'])]
      elif metric == 'coll_message_size':
        result[metric] = [a / b if b != 0 else 0 for a,b in zip(result['total_coll_message_size'],
                                                                result['num_coll_calls'])]
      elif metric == 'p2p_message_size':
        result[metric] = [a / b if b != 0 else 0 for a,b in zip(result['total_p2p_message_size'],
                                                                result['num_p2p_calls'])]
      elif metric == 'time_delay_mpi':
        result[metric] = [sum(a) for a in zip(result['time_mpi_barrier_wait'],
                                              result['time_mpi_latesender'],
                                              result['time_mpi_latereceiver'],
                                              result['time_mpi_latebroadcast'],
                                              result['time_mpi_wait_nxn'])]
      elif metric == 'delay_mpi_ratio':
        result[metric] = [a / b if abs(b) > 1e-8 else 0 for a,b in zip(result['time_delay_mpi'],result['time_mpi'])]
      elif metric == 'time_omp':
        result[metric] = [a - b for a,b in zip(result['total_time_scalasca'],result['time_omp_idle_threads'])]
      elif metric == 'delay_omp_ratio':
        result[metric] = [a / b if abs(b) > 1e-8 else 0 for a,b in zip(result['time_delay_omp'],result['time_omp'])]
      elif metric == 'omp_ratio':
        result[metric] = [a / b if abs(b) > 1e-8 else 0 for a,b in zip(result['time_omp'],result['total_time_scalasca'])]

  # Aggregation
  for metric in metrics:
    aggregation = metrics[metric][3]
    datatype = metrics[metric][2]
    if result[metric] is not None:
      result[metric] = datatype(aggregation(result[metric]))
  for metric in combined_metrics:
    aggregation = combined_metrics[metric][2]
    datatype = combined_metrics[metric][1]
    if result[metric] is not None:
      result[metric] = datatype(aggregation(result[metric]))

  # Combination of aggregated values
  for metric in combined_metrics_agg:
    result[metric] = None
    for other_metric in combined_metrics_agg[metric]:
      if result[other_metric] is None:
        break;
    else:
      if metric == 'critical_path_imbalance_ratio':
        result[metric] = result['critical_path_imbalance'] / result['critical_path'] if abs(result['critical_path']) > 1e-8 else None

  dump_json(dict([(tagged_metric(key,args),value) for key,value in result.items()]),args.output)

def extract_time(args):
   """Extract time information format"""
   key = tagged_metric("time",args)
   result = {key: None}
   file_handle = open(args.stderr_file, 'r')
   lines = file_handle.readlines()
   file_handle.close()

   if args.format == "cmd": #time command format
     pattern = re.compile('real\s+((?P<hours>[0-9]+)h)?(?P<minutes>[0-9]+)m(?P<seconds>[0-9]+)[.,][0-9]*s')
   elif args.format == "libmem": #libmem time format
     pattern = re.compile('IdrisMemMPI.*?elapsed.*?=.*?(\S+).*?s')
   elif args.format == "usr": #/usr/bin/time format
     pattern = re.compile('Elapsed \(wall clock\) time \(h:mm:ss or m:ss\):\s*((?P<hours>[0-9]+):)?'+
                          '(?P<minutes>[0-9]+):(?P<seconds>[0-9]+)[.,][0-9]*')

   match = None
   for line in reversed(lines):
     match = pattern.search(line)
     if match is not None:
       break

   if match is not None:
     if args.format == "cmd":
       result[key] = int(match.groupdict()['hours'] or 0)*3600 + int(match.groupdict()['minutes'])*60 + \
                     int(match.groupdict()['seconds'])
     elif args.format == "libmem":
       result[key] = int(float(match.group(1)))
     elif args.format == "usr":
       result[key] = int(match.groupdict()['hours'] or 0)*3600 + int(match.groupdict()['minutes'])*60 + \
                     int(match.groupdict()['seconds'])

   if result[key] is None:
     print('Warning: No timing information')
   dump_json(result, args.output)

def keys_here(keys_to_check, dic):
  for k in keys_to_check:
    if k not in dic:
      return False
    elif dic[k] is None:
      return False
  return True

def combine(args):
  # Combine all metrics
  metrics={}
  for f_name in args.json_file:
    f = open(f_name, "r")
    metrics.update(json.loads(f.read()))
    f.close()

  # Calculate derived metric values
  metrics["fma_eff"] = None
  if keys_here(["time_no-fma","time_ref"], metrics):
    metrics["fma_eff"] = 1.0 * metrics["time_no-fma"] / metrics["time_ref"]

  metrics["vec_eff"] = None
  if keys_here(["time_no-vec","time_ref"], metrics):
    metrics["vec_eff"] = 1.0 * metrics["time_no-vec"] / metrics["time_ref"]

  metrics["mem_vs_cmp"] = None
  if keys_here(["time_compact","time_scatter"], metrics):
    metrics["mem_vs_cmp"] = 1.0 * metrics["time_compact"] / metrics["time_scatter"]

  dump_json(dict([(tagged_metric(key,args),value) for key,value in metrics.items()]),args.output)

def extract_mem(args):
  """Extract memory information in "libmem" format"""
  key = tagged_metric("mem",args)
  result = {key: None}
  file_handle = open(args.stderr_file, 'r')
  lines = file_handle.readlines()
  file_handle.close()

  if args.format == "usr": #/usr/bin/time format
    pattern = re.compile('Maximum resident set size \(kbytes\):\s*(?P<kbytes>[0-9]+)')
  elif args.format == "libmem": #libmem format
    pattern = re.compile('IdrisMemMPI.*?RSSMax.*?=\s(.+?)\son')
  elif args.format == "slurm": #slurm format
    pattern = re.compile('Submitted batch job (\d+)')

  match = None
  for line in reversed(lines):
    match = pattern.search(line)
    if match is not None:
      break

  if match is not None:
    if args.format == "usr":
      result[key] = match.groupdict()['kbytes'] + "kB"
    elif args.format == "libmem":
      result[key] = match.group(1)
    elif args.format == "slurm":
      jobid = match.group(1)
      mem_infos = list()
      for mem_info in get_output("sacct -j "+jobid+" --format MaxRSS"):
        match = re.match("\s*(\d+)K\s*",mem_info)
        if match is not None:
          mem_infos.append(int(match.group(1)))
      if len(mem_infos) > 0:
        result[key] = str(max(mem_infos)) + "kB"

  if result[key] is None:
    print('Warning: No memory information')
  dump_json(result, args.output)

def extract_metrics_darshan(args):
  """Extract darshan information"""
  from darshanparser import extract_darshan_metrics
  darshan_output = extract_darshan_metrics(args.darshan_log)
  pattern = {"total_mb_read" : (re.compile(r'Total MB read: (.+?)\s*$',re.M),float),
             "total_mb_written" : (re.compile(r'Total MB written: (.+?)\s*$',re.M),float),
             "read_calls" : (re.compile(r'posix calls: (.+?) '),int),
             "write_calls" : (re.compile(r'posix calls: (?:.+? ){1}(.+?) '),int),
             "open_calls" : (re.compile(r'posix calls: (?:.+? ){2}(.+?) '),int),
             "stat_calls" : (re.compile(r'posix calls: (?:.+? ){3}(.+?) '),int),
             "seek_calls" : (re.compile(r'posix calls: (?:.+? ){4}(.+?) '),int),
             "mmap_calls" : (re.compile(r'posix calls: (?:.+? ){5}(.+?) '),int),
             "fsync_calls" : (re.compile(r'posix calls: (?:.+? ){6}(.+?)\s*$',re.M),int),
             "ind_read_time" : (re.compile(r'cumul_avg_io_time: (.+?) '),float),
             "ind_write_time" : (re.compile(r'cumul_avg_io_time: (?:.+? ){1}(.+?) '),float),
             "ind_meta_time" : (re.compile(r'cumul_avg_io_time: (?:.+? ){2}(.+?) '),float),
             "sh_read_time" : (re.compile(r'cumul_avg_io_time: (?:.+? ){3}(.+?) '),float),
             "sh_write_time" : (re.compile(r'cumul_avg_io_time: (?:.+? ){4}(.+?) '),float),
             "sh_meta_time" : (re.compile(r'cumul_avg_io_time: (?:.+? ){5}(.+?)\s*$',re.M),float),
             "io_time" : (re.compile(r'io_time: (.+?)\s*$',re.M),float),
             "avg_io_ac_size" : (re.compile(r'avg_io_ac_size: (.+?)\s*$',re.M),float)
             }
  
  combined_metrics_order=['io_volume','io_calls','io_throughput']
  combined_metrics = {'io_volume': (('total_mb_read','total_mb_written'),float),
                      'io_calls': (('read_calls','write_calls','open_calls','stat_calls','seek_calls','mmap_calls','fsync_calls'),int),
                      'io_throughput': (('io_volume','io_time'),float)
                     }

  result = dict()
  for pat in pattern:
    result[pat] = None
    match = pattern[pat][0].search(darshan_output)
    if match is not None:
      result[pat] = pattern[pat][1](match.group(1))

  #Combination
  for metric in combined_metrics_order:
    result[metric] = None
    for other_metric in combined_metrics[metric][0]:
      if result[other_metric] is None:
        break;
      else:
        if metric == 'io_volume':
          result[metric] = result['total_mb_read'] + result['total_mb_written']
        elif metric == 'io_calls':
          result[metric] = result['read_calls'] + result['write_calls'] + result['open_calls'] + result['stat_calls'] + result['seek_calls'] + result['mmap_calls'] + result['fsync_calls']
        elif metric == 'io_throughput':
          if abs(result['io_time']) > 1e-8:
            result[metric] = result['io_volume'] / result['io_time']
          else:
            result[metric] = 0
        result[metric] = combined_metrics[metric][1](result[metric])

  dump_json(dict([(tagged_metric(key,args),value) for key,value in result.items()]), args.output)

def dump_json(dic, file_name):
  """Dump given dictionary to file using JSON format"""
  to_write = json.dumps(dic)
  f = open(file_name, "w")
  f.write(to_write)
  f.close()

def build_parser():
  # create the top-level parser
  parser = argparse.ArgumentParser(prog='extract_metrics')
  parser.add_argument('-o','--output', default="metrics.json",
                      help='name of the output file (default metrics.json)')
  parser.add_argument('-t','--tag',
                      help='Tag added to a metric name to differentiate the context it has been obtained')
  subparsers = parser.add_subparsers(dest="subparser", help='sub-command help')

  # create the parser for the scalasca metrics
  parser_sca = subparsers.add_parser('scalasca', help='Extracts metrics from the trace file from scoreP')
  parser_sca.add_argument('trace_file', help='ScoreP trace file')
  parser_sca.set_defaults(func=extract_metrics_scalasca)

  # create the parser for the papi metrics
  parser_papi = subparsers.add_parser('papi', help='Extracts papi metrics from the profile file from scoreP')
  parser_papi.add_argument('profile_file', help='ScoreP profile file')
  parser_papi.set_defaults(func=extract_metrics_papi)

  # create the parser for the darshan metrics
  parser_da = subparsers.add_parser('darshan', help='Extracts metrics from the darshan metric file')
  parser_da.add_argument('darshan_log', help='Darshan log file')
  parser_da.set_defaults(func=extract_metrics_darshan)

  # create the parser for the time metric
  parser_time = subparsers.add_parser('time',
                                      help='Extracts time from the std.err file, using the time command format')
  parser_time.add_argument('-f','--format', choices=['cmd','usr','libmem'], default="cmd",
                           help='Select the format of the time extraction (cmd: time command [default], usr: ' +
                                '/usr/bin/time, libmem: libmem library)')
  parser_time.add_argument('stderr_file', help='stderr file')
  parser_time.set_defaults(func=extract_time)

  # create the parser for the mem metric
  parser_mem = subparsers.add_parser('mem', help='Extracts memory ffotprint from the std.err file')
  parser_mem.add_argument('-f','--format', choices=['libmem','usr','slurm'], default="libmem",
                          help='Select the format of the mem extraction (usr: ' +
                               '/usr/bin/time, libmem: libmem library [default], slurm: via sacct (provide stdout file which contains the jobid))')
  parser_mem.add_argument('stderr_file', help='stderr file')
  parser_mem.set_defaults(func=extract_mem)


  # create the parser for the combine command
  parser_agg = subparsers.add_parser('combine', help='combine all json files passed in parameter')
  parser_agg.add_argument('json_file', nargs='+', help='json files to combine')
  parser_agg.set_defaults(func=combine)

  return parser

def tagged_metric(metric_name,args):
  """Add tag postfix to given metric name if needed"""
  if args.tag is not None:
    return "{0}_{1}".format(metric_name,args.tag)
  else:
    return metric_name

def main():
  parser = build_parser()
  args = parser.parse_args()
  args.func(args)

if __name__ == '__main__':
  main()

