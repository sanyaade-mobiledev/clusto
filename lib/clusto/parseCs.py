import libDigg

class parseCsFile:


    def __init__(self,filename):
    
        self.filename = libDigg.fopen (filename,"r")

    def parseCsHeader(self):

        """parses the global header section of a clusterscript and puts those values into the globalHeader dict"""

        clusterScript = {}
        # global header is task 0
        clusterScript.setdefault('globalHeader', {})['task'] = 0
        #globalHeader = {}
        for rline in self.filename:

            line = rline.rstrip()
            if line ==">>":
                self.clusterScript = clusterScript
                return

            if line == "":
                continue
          
            sline = line.split(':',1) 
            k = sline[0].rstrip(':')
            v = sline[1]
            clusterScript.setdefault('globalHeader', {})[k] = v



    def parseChunks(self):
    
        """parses the rest of the clusterscript file to put into each task into a dictionary"""

        taskHeader = {}
        isHeader = 1
        tasknum = 1
        body = []
        file = self.filename
        clusterScript = self.clusterScript
        for rline in self.filename:
            line = rline.rstrip()

            if line == "":
                continue
             
            if line =="---":
                isHeader=0
                continue

            if line ==">>":
                isHeader=1
                continue

            if line =="<<":
                clusterScript.setdefault(tasknum, {})['body'] = body
                clusterScript.setdefault(tasknum, {})['task'] = tasknum
                tasknum+=1
                self.clusterscript = clusterScript
                body=[]
                isHeader=0
                continue

            if isHeader==1:
                sline = line.split(':',1)
                clusterScript.setdefault(tasknum, {})[sline[0]] = sline[1]
            else:
                body.append(line)

if __name__ == '__main__':

    filename = "clusterscript.cs"
    cs = parseCs(filename)
    cs.parseCsHeader()
    cs.parseChunks()
    foo = cs.clusterScript
    print foo.keys()
    for k in foo.values():
        print k
