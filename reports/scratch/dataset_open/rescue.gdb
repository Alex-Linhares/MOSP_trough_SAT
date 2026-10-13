set pagination off
call (int) PyGILState_Ensure()
call (int) PyRun_SimpleString("exec(open('/home/al/dev/MOSP/reports/scratch/dataset_open/rescue.py').read())")
call (void) PyGILState_Release($1)
detach
quit
