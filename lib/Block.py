#-------------------------------------------------------------------------------
#   PROJECT:   VHDL Code Generator
#   NAME:      Block
#
#   LICENSE:   GNU-GPL V3
#-------------------------------------------------------------------------------

__author__ = "BlakeTeam"

from visual.BlockVisual import *

IN = 1
OUT = 0
TEMP = 2



class Block:
    """ Description of the block.

        This is the generic block.
    """
    def __init__(self, input_vector, output_vector, system, name = None):
        """ Structure that handles an abstract Block.
            Each block has a name(string) that is given by default for the system.

        :Int[] input_vector:      Size of the inner ports of the block.
        :Int[] output_vector:     Size of the outer ports of the block.
        :System system:           Reference to the system where this block belong.
        """
        # Comprehension list that generates list of ports initialized by default
        self.input_ports = [Port("in"+str(i),input_vector[i],IN) for i in range(len(input_vector))]
        self.output_ports = [Port("out"+str(i),output_vector[i],OUT) for i in range(len(output_vector))]

        self.system = system
        self.variables = [] # Variables(SIGNALS) to be used on the block

        if name == None:
            self.name = self.get_name()
        else:
            self.setName(name)

        # Position on the screen to visualize the block
        self.screenPos = (0,0)

    def getVariableSignalSize(self,index):
        return self.variables[index][1]

    def getOutputSignalSize(self,index):
        return self.getOutputPort(index).size

    def getInputSignalSize(self,index):
        return self.getInputPort(index).size

    def getVariableSignalName(self,index):
        return self.getSignalName(self.variables[index][0])

    def getOutputSignalName(self,index):
        return self.getSignalName(self.getOutputPort(index).name)

    def getInputSignalName(self,index):
        return self.getSignalName(self.getInputPort(index).name)

    def getSignalName(self,name):
        """ Valid name of the signal to be implemented on the VHDL Code
        """
        return "%s__%s"%(self.name,name)

    # TODO: validate the name, there cant be 2 ports with the same name (Variables too)
    def addVariable(self,name,size):
        self.variables.append((name,size))

    def setInputName(self,name,index):
        self.getInputPort(index).name = name

    def setOutputName(self,name,index):
        self.getOutputPort(index).name = name

    def getInputPort(self,index):
        return self.input_ports[index]

    def getOutputPort(self,index):
        return self.output_ports[index]

    def getCoords(self,mode,index):
        if mode == IN:
            return self.screenPos[0] - QBlock.PORT_SIZE,self.screenPos[1] + (index + 1)*(QBlock.DX*(max(len(self.block.input_ports), len(self.block.output_ports))+1)/len(self.input_ports))
        else:
            return self.screenPos[0] + QBlock.PORT_SIZE + QBlock.WIDTH, self.screenPos[1] + (index + 1)*(QBlock.DX*(max(len(self.block.input_ports), len(self.block.output_ports))+1)/len(self.output_ports))

    def get_name(self):
        """ Return a valid name for the block.
            A name that is not in the list of names in the current system.
        """
        ind = 0
        while True:
            name = "block" + str(ind)
            if not name in self.system.block_name:
                self.system.block_name.add(name)
                return name
            else:
                ind += 1
    def generate(self):
        """ Method to be overridden. It generates the VHDL code.
        """
        raise NotImplemented("Generate not implemented")

    def getSignals(self):
        """ Method to be overridden.

            Return a list of tuple that represent signals of the form:
            (name, size, type) where type can be IN,OUT,TEMP
        """
        signals = []

        for i in self.input_ports:
            signals.append((i.name,i.size,i.mode))
        for i in self.output_ports:
            signals.append((i.name,i.size,i.mode))
        for i in self.variables:
            signals.append((i[0],i[1],TEMP))

        return signals

    def __getitem__(self, name):
        """ Find a port for its name.
            This function starts for input ports.
            If the port exist it returns the reference to the port & mode(IN/OUT)
            Else it returns -1

        :String name: The name of the wanted port/
        """
        try:
            pos = self.input_ports.index(name)
            return pos,IN
        except ValueError:
            try:
                pos = self.output_ports.index(name)
                return pos,OUT
            except ValueError:
                return -1

    def setName(self,name):
        """ Set the name of the current block.
            It is safely change the name using this method.

        :String name:      The new name of this block.
        """
        # Check that the new name do not already exist

        if name in self.system.block_name:
            pos = 2
            while True:
                curName = name + "_" + str(pos)
                if not curName in self.system.block_name:
                    name = curName
                    break
                else:
                    pos += 1

        try:
            self.system.block_name.remove(self.name)
        except KeyError:
            pass
        self.system.block_name.add(name)
        self.name = name

class Port:
    def __init__(self,name,size,mode):
        """ Structure that handles an abstract port.
            Each Port has a connection property,
            If the mode is IN:
                connection property is a reference to other port of mode OUT.
            If the mode is OUT:
                connection property is an array of Ports of mode IN.
            connection is the one who keep the links between blocks.

        :String name:   Name of the port.
        :Int size:      The total of bits that the port handles.
        :IN/OUT mode:   Mode of the port.
        """
        self.name = name
        self.size = size
        self.mode = mode
        self.pin = None

        if self.mode == IN:
            self.connection = None
        else:
            self.connection = []

    def __eq__(self, other):
        if isinstance(other,str):
            return other == self.name
