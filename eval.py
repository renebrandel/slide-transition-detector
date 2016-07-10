import subprocess

for i in xrange(20):
    subprocess.call(['touch', 'hello_world'])
