from cdo import *
import sys, time, shutil
from package.MP import IterMP


def add_to_file_name(path, add):
    return(os.path.join(
        os.path.split(path)[0],
        os.path.split(path)[1][:-3] + str(add) +
        os.path.split(path)[1][-3:]))

def diurnal_substep(ifile, agg_mode):
    ofile = add_to_file_name(ifile, '_agg')
    if agg_mode == 'MEAN':
        ofile = cdo.timmean(input=ifile, output=ofile)
    elif agg_mode == 'SUM':
        ofile = cdo.timsum(input=ifile, output=ofile)
    return(ofile)



def calc_diurnal(var_name, njobs, inp_path, out_path,
                    temp_path, run_async=False):
    # remove files in tmp dir
    for file in os.listdir(temp_path):
        os.remove(os.path.join(temp_path,file))

    # remove first field (initial data)
    tmp_out = os.path.join(temp_path,'removed_field.nc')
    cdo.delete('timestep=1', input=inp_path, output=tmp_out)

    # split into hours
    ofiles = cdo.splithour(input=tmp_out, output=temp_path)
    ofiles.remove(tmp_out)

    if var_name == 'nTOT_PREC':
        agg_mode = 'SUM'
    else:
        agg_mode = 'MEAN'

    t0 = time.time()
    IMP = IterMP(njobs=njobs, run_async=True)
    fargs = {'agg_mode':agg_mode,}
    step_args = []
    for fI,ofile in enumerate(ofiles):
        ifile = os.path.join(temp_path,ofile)
        step_args.append({'ifile':ifile})
    IMP.run(diurnal_substep, fargs, step_args)
    t1 = time.time()
    print(t1 - t0)
    inp_files = IMP.output
    ofile = cdo.mergetime(input=IMP.output, output=out_path)
    print(ofile)
    print('done')






if __name__ == '__main__':

    if len(sys.argv) < 3:
        raise ValueError('Not Enough arguments given.')

    try:
        var_name = sys.argv[1]
        print('variable is ' + var_name)
    except IndexError:
        print('Variable not given')

    try:
        njobs = int(sys.argv[2])
        print('number of jobs is ' + str(njobs))
    except IndexError:
        print('Number of Jobs not given. Assume 1')
        njobs = 1

    members = ['4.4', '4.4f']
    members = ['4.4', '4.4f', '2.2', '2.2f', '1.1', '1.1f']
    run_async = False

    temp_path = '/scratch/snx3000/heimc/.tmp/'
    cdo = Cdo()
    # the following options do not work:
    #cdo = Cdo(tempdir=temp_path)
    #cdo.cleanTempDir()
    #cdo.forceOutput = False

    for member in members:
        inp_path = os.path.join('..','topocut',member,var_name+'.nc')
        out_path = os.path.join('..','diurnal',member,var_name+'.nc')
        if os.path.exists(out_path):
            print('Skip member ' + member)
        else:
            print(member)
            calc_diurnal(var_name, njobs, inp_path, out_path,
                            temp_path, run_async=run_async)
    
