import os
print(os.path.realpath('{}/../../runs.log'.format(os.path.realpath(__file__))))
