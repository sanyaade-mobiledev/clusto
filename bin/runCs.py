import libDigg
import parseCs
import clustoScript
import sys


def usage():

    print "runCs.py --script=clusterscript.cs key1=value1 key2=value2, etc"
    sys.exit(1)


if __name__ == '__main__':


    # the arg parsing is so simple because we want to allow any arbitrary --key=value 
    # pairs to be passed in for resolution

    Args = {}
    for arg in sys.argv[1:]:
        # get rid of the '--' that starts argumments
        sarg = arg.strip('--')
        k, v = sarg.split('=')
        Args[k] = v

    # the only arg we really require is the script one
    if not Args.has_key('script'):
        usage()

    #filename = "../test/clusterscript.cs"
    cs = parseCs.parseCsFile(Args['script'])
    cs.parseCsHeader()
    cs.parseChunks()

    script = clustoScript.Script(cs)
    script.createChunks()
    script.resolveChunks()
   
    # make up some bullshit resolved tasks
    # it will make as many of these as you have chunks in your real clusterscript
    # so if you have two chunks in your clusterscript, it will ignore the content 
    # of those chunks and make three tasks (below) for each of your two chunks

    tasks = []
    for c in script.chunks:
        # skip the special header chunk
        if c.tasknum == 0: 
            continue 
        # make up some bullshit resolved tasks for now and attach them to a chunk
        # even though the real parsed-in task might not look anything like this
        for i in 1,2,3:
            mydict = {'user':'root','name':'testing chunk','body':['echo "blah blah"\n', 'ls /trlkaijs'], 'shell':'bash', 'services_include':'32G', 'runmode':'hostwithrole', 'task':2, 'cluster_root':'/foo', 'services':'foo1-3', 'mykey':'myvalue', 'ip':'192.168.243.42', 'transport':'ssh', 'onError':'continue' , 'maxParallel':'10' , 'debug':0,'verbose':1}                
            t = clustoScript.Task(i,mydict)
            tasks.append(t)
            c.tasks = tasks
        tasks = []
    
    for chunk in script.chunks:

        # skip the first chunk
        # which is just the global header data
        if chunk.tasknum == 0:
            continue
        q = clustoScript.QueueRunner(chunk)
        q.writeTasks()
        q.execute()
        #q.cleanUp()
