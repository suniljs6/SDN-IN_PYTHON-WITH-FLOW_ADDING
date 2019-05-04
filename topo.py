from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.cli import CLI
from graph import *
from algorithm import *
import os
import random

graph = Graph()
cost_func = lambda u, v, e, prev_e: e['cost']
switches_list = []
hosts_list = []
class createMeshTopo(Topo):
        def build(self,n):
                #Add Hosts
        global graph
        global switches_list
        global hosts_list
                switches = []
                hosts = []
        count=1
                for x in range(n):
            pre_switches=[]
            pre_hosts=[]
            pre_switches_list = []
            pre_hosts_list = []
            for j in range(n):
                        pre_switches.append(self.addSwitch('s%s'%(count),cls=OVSKernelSwitch,dpid='%s'%(count)))
                        pre_hosts.append(self.addHost('h%s'%(count),ip='10.0.0.%s'%(count),defaultRoute=None))
                        self.addLink(pre_hosts[-1],pre_switches[-1])
                graph.add_edge('h%s'%(count),'s%s'%(count),{'cost':1})
                graph.add_edge('s%s'%(count),'h%s'%(count),{'cost':1})
                pre_switches_list.append('s%s'%(count))
                pre_hosts_list.append('h%s'%(count))
                count+=1
            switches.append(pre_switches)
            hosts.append(pre_hosts)
            switches_list.append(pre_switches_list)
            hosts_list.append(pre_hosts_list)
        count=1       
        for i in range(n-1):
            for j in range(n-1):
                self.addLink(switches[i][j],switches[i][j+1])
                graph.add_edge('s%s'%(count),'s%s'%(count+1),{'cost':1})
                graph.add_edge('s%s'%(count+1),'s%s'%(count),{'cost':1})
                self.addLink(switches[i][j],switches[i+1][j])
                graph.add_edge('s%s'%(count),'s%s'%(count+n),{'cost':1})
                graph.add_edge('s%s'%(count+n),'s%s'%(count),{'cost':1})
                print("1st:"+str(count))
                count+=1
            count+=1
        for i in range(n-1):
            self.addLink(switches[n-1][i],switches[n-1][i+1])
            self.addLink(switches[i][n-1],switches[i+1][n-1])
        count1=n
        count2=((n*n)-n)+1
        for _ in range(n-1):
            graph.add_edge('s%s'%(count1),'s%s'%(count1+n),{'cost':1})
            graph.add_edge('s%s'%(count1+n),'s%s'%(count1),{'cost':1})
            graph.add_edge('s%s'%(count2),'s%s'%(count2+1),{'cost':1})
            graph.add_edge('s%s'%(count2+1),'s%s'%(count2),{'cost':1})
            count1+=1
            count2+=1

               


def MyController(net,array):
        """Controller Program """
    global graph
    if len(array)>0:
        x = find_path(graph, array[0], array[1], cost_func=cost_func)
        return x[0]
        #net

def createLinks(dl_src,dl_dst,port,values,net):
    if(len(dl_src)==2):
        dl_src="00:00:00:00:00:0%s"%(dl_src[1])
    else:
        dl_src="00:00:00:00:00:%s"%(dl_src[1:])
    if(len(dl_dst)==2):
        dl_dst="00:00:00:00:00:0%s"%(dl_dst[1])
    else:
        dl_dst="00:00:00:00:00:%s"%(dl_dst[1:])
    print(dl_src,dl_dst)
    output_port = port[(values[0],values[1])][0]
    input_port = port[(values[1],values[0])][1]
    net.getNodeByName(values[1]).dpctl('add-flow','dl_src=%s,dl_dst=%s,actions=output:%d'%(dl_src,dl_dst,output_port))
    net.getNodeByName(values[1]).dpctl('add-flow','dl_src=%s,dl_dst=%s,actions=output:%d'%(dl_dst,dl_src,input_port))
    for i in range(1,len(values)-1):
        #print('dl_src=%s,dl_dst=%s,actions=%d'%(dl_src,dl_dst,port[(values[i],values[i+1])]))
        output_port = port[(values[i],values[i+1])][0]
        input_port = port[(values[i],values[i+1])][1]
        net.getNodeByName(values[i]).dpctl('add-flow','dl_src=%s,dl_dst=%s,priority=500,actions=output:%d'%(dl_src,dl_dst,output_port))
        net.getNodeByName(values[i]).dpctl('add-flow','dl_src=%s,dl_dst=%s,priority=500,actions=output:%d'%(dl_dst,dl_src,input_port))
        net.getNodeByName(values[i]).dpctl('add-flow','dl_type=0x806,nw_proto=1,actions=flood')
        net.getNodeByName(values[i]).dpctl('add-flow','actions=normal')




def get_defect_node_pos(defect_node):
    global switches_list
    pos=None
    for i in range(len(switches_list)):
        if defect_node in switches_list[i]:
            pos = (i,switches_list[i].index(defect_node))
            break
        else:
            pos=None
    print(pos)   
    neighbours = []
    if(pos!=None):
        n = len(switches_list)
        if(pos[0]-1>=0):
            neighbours.append((pos[0]-1,pos[1]))
        if(pos[0]+1<=(n-1)):
            neighbours.append((pos[0]+1,pos[1]))
        if(pos[1]-1>=0):
            neighbours.append((pos[0],pos[1]-1))
        if(pos[1]+1<=(n-1)):
            neighbours.append((pos[0],pos[1]+1))
    return neighbours
   
   

def Test(a):
    global switches_list
        topo = createMeshTopo(n=a)
        net = Mininet(topo)
    port={}
        net.start()
        MyController(net,[])
        print("Dumping Node Connections")
        dumpNodeConnections(net.switches)
    print(switches_list)
    print(hosts_list)
    connections = net.links
    for i in range(len(connections)):
        x=str(connections[i].intf1)
        y=str(connections[i].intf2)
        x1=x.split("-")[0]
        x2=(x.split("-")[1]).replace("eth","")
        y1=y.split("-")[0]
        y2=(y.split("-")[1]).replace("eth","")
        port[(x1,y1)]=(int(x2),int(y2))
        port[(y1,x1)]=(int(y2),int(x2))
    print(port)
    x='n'
    while(x!='y'):
        print("Enter hosts which you want to ping seperating them by space")
        array = list(raw_input().split(" "))
        dl_src=array[0]
        dl_dst=array[1]
        values = MyController(net,array)
        print(values)
        print("do you want to consider another path or do you wish to continue with the given path press y to get second path")
        inputer = raw_input()
        if(inputer=='y'):
            print("choose an node which you dont want to include in the path")
            defect_node = raw_input()
            neighbours = get_defect_node_pos(defect_node)
            print(neighbours)
            for i in neighbours:
                nodes = switches_list[i[0]][i[1]]
                print(nodes)
                if nodes not in values:
                    break
            first_set = MyController(net,[array[0],nodes])
            second_set = MyController(net,[nodes,array[1]])
            print(first_set,second_set)
            values=first_set+second_set[1:]
            print(values)
        createLinks(dl_src,dl_dst,port,values,net)
        net.ping([net.getNodeByName(array[0]),net.getNodeByName(array[1])])
        print("Enter y to exit")
        x=raw_input()
    #net.getNodeByName('h1').cmd('ping -c 10 %s > ping.log'%('10.0.0.2'))
    #print(topo.hosts)
    #for m in range(1,(a*a)+1):
    #    for n in range(m+1,(a*a)+1):
    #        dl_src='h%s'%(m)
    #        dl_dst='h%s'%(n)
    #        print(dl_src,dl_dst)
    #        values = MyController(net,[dl_src,dl_dst])
    #        createLinks(dl_src,dl_dst,port,values,net)
    #        x = 'h%s'%(m)
    #        y = 'h%s'%(n)
    #        print(x,y)
    #        if(len(str(n))==2):
    #            net.getNodeByName(x).cmd('ping -c 10 %s > h%s_h%s.log'%('10.0.0.'+str(n),m,n))
    #        else:
    #            net.getNodeByName(x).cmd('ping -c 10 %s > h%s_h%s.log'%('10.0.0.0'+str(n),m,n))
           
       
           
       
    #net.cmd("net")   
    CLI(net)
        net.stop()

if __name__ == '__main__':
        setLogLevel('info')
    n = int(input())
        Test(n+1)
