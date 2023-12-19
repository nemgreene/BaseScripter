import pymel.core as pmc

import pymel.core as pmc
import maya.api.OpenMaya as om

# import maya.cmds as cmds

# # Clear caches in all dependency graph nodes
# cmds.clearCache( all=True )

# import sys
# path = r'G:\My Drive\Maya\scripts\BaseScripter'
# if path not in sys.path:
#     sys.path.append(path)

# from baseScripter import BaseScripter

# bg = BaseScripter("test")


class BaseScripter():
    """
    Create the BaseScripter Instance
    
    Args:
    - name: [string]           Overall Name of the feature being built
        Will be perpetuated along into all nodes created by this class

    Kwargs:
    - name: [string]           Overall Name of the feature being built
        Will be perpetuated along into all nodes created by this class
    - side: [string]           Overall side of the feature being built
        Will be perpetuated along into all nodes created by this class
    
    Class Variables:
    - cleanup: [this.cleanup]
        Parent folder that will hold all the generated nodes, instanced with the class
    -selection: [this.selection]
        Selection made by the user when script has run. 
        This may cause some looping issues. 
        To start with no selection, clear the maya selection before the scripter is instanced
        To end the script with a selection, set Basescripter.instance.selection to the selection
    Methods:
        -ng
        -ag
    """
    class CustomException(Exception):
        def __init__(self, message = "Default Custom Error Message"):            
            super(BaseScripter.CustomException, self).__init__(message)

    def ng(this, *args, **kwargs):
        """
        Name generator
        
        Args:
        - : [*String/Array] Ordered names to be concatenated with a "_" between args

        Kwargs:
        - n : [Truthy/Falsey]:
            If true, "01" will be added to the end
        
        Examples:
        Basescripter.instance.ng("grp","all")
        //returns -> ("grp_all")[String]
        Basescripter.instance.ng("grp","one", n=1)
        //returns -> ("grp_all01")[String]
        """
        number = None if ("n" in kwargs and (bool(kwargs['n']) == False)) else "01"
        ret = ""
        for index, arg in enumerate(args):
            ret += str(arg) + ("_" if index < len(args)-1 else "")
        return ret + number if number else ret

    def ag(this, *args):
        ret = ""
        for index, arg in enumerate(args):
            ret += str(arg) + ("." if index < len(args)-1 else "")
        return ret

    def makeNesting(this, hierarchy = {}, parent = None):
        """
        Initialize project group hierarchy
        
        Args:
        - hierarchy: [str/obj/array]           
        - parent: [str/transform node]

        Generates a folder hierarchy based on data schema passed to it

        Examples:

        bs = BaseScripter("DemoScripter") \n
        bs.makeNesting(hierarchy)  \n
        hierarchy = "foo"  \n
        // result  \n

        |grp_DemoScripter01 \n
        |--grp_foo01 \n

        hierarchy = ["foo", "bar"]  \n
        bs.makeNesting(hierarchy)  \n
        // result  \n
        |grp_DemoScripter01 \n
        |--grp_foo01 \n
        |--grp_bar01 \n

        hierarchy = {"foo": "bar", "fa": ["do", "re", "mi"]}  \n
        bs.makeNesting(hierarchy)  \n
        // result  \n
        |grp_DemoScripter01 \n
        |--|grp_foo01 \n
        |--|--|grp_bar01 \n
        |--|grp_fa01 \n
        |--|--|grp_do01 \n
        |--|--|grp_re01 \n
        |--|--|grp_mi01 \n
        """
        grp = None
        if(type(hierarchy) == dict):
            for key in hierarchy.keys():
                grp = this.makeNesting(key)
                this.makeNesting(hierarchy[key], grp)
        elif(type(hierarchy) == list):
            for key in hierarchy:
                this.makeNesting(key, parent)
        elif(type(hierarchy) == str):
            grp = pmc.group(em=1, n=this.ng("grp", this.label,hierarchy ))
            this.groups[hierarchy] = grp
            if(parent):
                pmc.parent(grp, pmc.ls(parent)[0])
            else:
                pmc.parent(grp, this.cleanup)
            pmc.select(cl=1)
            return grp
        else:
            raise("Hierarchy Error")
            return
        
    def attrCleanup(this, obj, args=['t', 'r', 's', 'v']):
        """
        Removes attributes from the channel box
        
        Args:
        - obj: [String/Obj] Target object 
        - args(Optional): [*String] [t/r/s/v/AttrName] Attributes to remove from channel 
        """
        if ("t" in args):
            pmc.setAttr(this.ag(obj, "tx"), lock=1, k=0, channelBox=0)
            pmc.setAttr(this.ag(obj, "ty"), lock=1, k=0, channelBox=0)
            pmc.setAttr(this.ag(obj, "tz"), lock=1, k=0, channelBox=0)
            args = filter(lambda x: "t" not in x, args)
        if ("r" in args):
            pmc.setAttr(this.ag(obj, "rx"), lock=1, k=0, channelBox=0)
            pmc.setAttr(this.ag(obj, "ry"), lock=1, k=0, channelBox=0)
            pmc.setAttr(this.ag(obj, "rz"), lock=1, k=0, channelBox=0)
            args = filter(lambda x: "r" not in x, args)
        if ("s" in args):
            pmc.setAttr(this.ag(obj, "sx"), lock=1, k=0, channelBox=0)
            pmc.setAttr(this.ag(obj, "sy"), lock=1, k=0, channelBox=0)
            pmc.setAttr(this.ag(obj, "sz"), lock=1, k=0, channelBox=0)
            args = filter(lambda x: "s" not in x, args)
        if (len(args) > 0):
            for attr in args:
                pmc.setAttr(this.ag(obj, attr), lock=1, k=0, channelBox=0)

    def __init__(this, *args, **kwargs):
        this.title = args[0] or "BaseScripterInstance"
        this.__dict__.update(kwargs)
        this.groups = {}

        this.selection = pmc.ls(sl=1)
        this.debug = True

        this.cleanupList = ["pointMatrixMult", "decomposeMatrix", "composeMatrix", "motionPath", "cluster", "tweak", "wire", "blendShape", "condition", "blendTwoAttr",
                    "distanceBetween", "setRange", "multiplyDivide", "plusMinusAverage"]


        if("side" in kwargs):
            this.label = this.ng(kwargs['side'], this.name, n=0)
        else:
            this.label = this.name

        # scene cleanup on reset
        deleteCleanup = lambda : pmc.delete(this.ng('grp',this.label, n=1 )) 
        cleanupNodes = lambda : pmc.delete(pmc.ls("*" + this.label + "*", type=this.cleanupList))
        try:
            deleteCleanup() or cleanupNodes()
        except:
            print("No cleanup")
        

        this.cleanup = pmc.group(n = this.ng('grp',this.label, n=1 ), em=1)
        this.groups['cleanup'] = this.cleanup
        pmc.select(cl=1)

    def makeNested(this, asset, parent =None):
        """
        Accepts an obj to store in either a parent folder or default into this.cleanup
        
        Args:
        - asset: [String/Obj] Target object 
        - parent : [String/Obj] Parent folder to leave the offsetGrp in 
        """
        parent = parent if parent else this.cleanup
        pmc.parent(asset[0] if type(asset) == list else asset, parent)
        return asset

    def movePivot(this, obj,v = [0.,0.,0.], **kwargs ):
        """
        Move pivot to vector
        
        Args:
        - Object: [String/Array] Object pivot to move
        - Vector(Optional): [Array/Tuple] Vector transformation to apply

        Kwargs:
        - target : [String/Obj]:
            Object to move the pivot to
        - All applicable kwargs will be  passed directly to the move function.
            Derived from mel command `maya.cmds.move`
        """
        if "target" in kwargs:
            v = pmc.xform(kwargs['target'], q=1, t=1, ws=1)
            del kwargs['target']

        if(type(obj) == "list"):
            obj = obj[0]

        
        
        pmc.move(this.ag(obj, "scalePivot"), v, **kwargs)
        pmc.move(this.ag(obj, "rotatePivot"), v, **kwargs)

    def makeDistance(this, obj1, obj2, **kwargs):
        """
        Makes a distance node between two objects
        
        Args:
        - obj1: [String/Obj] Target object1 
        - obj2: [String/Obj] Target object2

        Kwargs:
        -name(Optional): [String] Replaces default name with specific name declared 
        """
        name = this.ng(kwargs['name'], this.label) if 'name' in kwargs else this.ng("dist", this.label, n=0) 
        dist = pmc.shadingNode('distanceBetween',au=1, n = name )
        for index, obj in enumerate([obj1, obj2]):
            if pmc.nodeType(obj) == "joint":
                pmc.connectAttr(this.ag(obj1 if index == 0 else obj2, "worldMatrix"),this.ag(dist, ("inMatrix1" if index == 0 else "inMatrix2")))
            else:
                print("make distance node type not covered")
        return dist

    def ghostConstraint(this, type,driver, driven, **kwargs):
        """
        Applies then deletes a constraint to an object
        
        Args:
        - type: [String] [point/parent/orient/aim/scale] type of constraint to apply.
        - driver: [Array/String] Constraint driver
        - driven: [Array/String] Constraint driven

        Kwargs:
        - All applicable kwargs will be  passed directly to the constraint function.
            Derived from mel commands from:
              `maya.cmds.pointConstraint`
              `maya.cmds.parentConstraint`
              `maya.cmds.orientConstraint`
              `maya.cmds.aimConstraint`
              `maya.cmds.scaleConstraint`
        """
        result = {
            'point' : lambda : pmc.delete(pmc.pointConstraint(driver, driven, **kwargs)),
            'parent' : lambda : pmc.delete(pmc.parentConstraint(driver, driven, **kwargs)),
            'orient' : lambda : pmc.delete(pmc.orientConstraint(driver, driven, **kwargs)),
            'aim' : lambda : pmc.delete(pmc.aimConstraint(driver, driven, **kwargs)),
            'scale' : lambda : pmc.delete(pmc.scaleConstraint(driver, driven, **kwargs)),

        }
        result[type]()

    def clusterAndOffset(this, cv, name):
        """
        Creates a cluster and transform offset group
        
        Args:
        - cvs: [Array/String/PymelObj] Cluster Target 
        - name: [String] Cluster name, perpetuated to cluster offset group name

        Return [offsetGrp/cluster][String/String]
        """
        cluster = pmc.cluster(cv, n=this.ng("cls", this.label, name ))
        grp = pmc.group(em=1, n=this.ng("grp_clsOffset", this.label, name ))
        pmc.xform(grp, cp=1)
        pmc.makeIdentity(grp, t=1, s=1, r=1)

        pmc.parent(cluster[1], grp)
        pmc.parent(grp, this.cleanup)
        return [grp, cluster]
    
    def groupAndOffset(this, obj, name, **kwargs):
        """
        Creates an empty group, mirrors target transforms, then parents target into it
        
        Args:
        - Obj:[String]          Obj to be nested
        - Name:[String]         Name of the group

        Kwargs:
        - parent(Optional):[string]       Name of the parent group to leave the offsetGrp in once complete

        Return [offsetGrp][String]
        """
        offsetGrp = pmc.group(em=1, n=name)
        this.ghostConstraint("parent", obj, offsetGrp)
        pmc.parent(obj, offsetGrp)
        pmc.parent(offsetGrp, this.cleanup if "parent" not in kwargs else kwargs['parent'] )
        return offsetGrp
    
    def execute(this, *args):
        print("executing")
        execution_generator = (x for x in args)
        for procs in execution_generator:
            try:
                procs()
            except Exception as error:
                print("Error at function: " + procs.__name__ )
                print(error)
                return
        if(this.debug):
            if(this.selection):
                pmc.select(this.selection)  
        print(this.title +  " execution complete")

    # Mathematical
    def __gen_exponential_distro_rand_variable(this):
        return -( math.log( (  random.random() ) ) )

    def __accept_or_reject(this,  num_iterations ):

        # https://tonypoer.io/2016/03/25/generating-standard-normal-random-variates-with-python/

        # https://github.com/adpoe/STD-Normal-Rand-Variates/blob/master/data_and_histograms/Accept_or_Reject_Histogram.png

        # Generates a normal distribution or random numbers between a range of [-4,4]


        # RAND =  a draw from the U[0,1)
        RAND = random.random
        accept = False
        reject = False
        rejections = 0
        Z = 0      # The z-value we are generating


        # f(x) = the standard normal pdf function
        # f_of_x = (2.0 / math.sqrt(2.0 * math.pi)) * math.e.__pow__(- (RAND ** 2) / 2.0)

        # g(x) = the exponential density function with mean 1, that is: (lambda=1)
        # g_of_x = math.e.__pow__(-RAND)

        # c = max{f(x)/g(x)}
        # Formula from Sheldon Ross's Simulation: 5th addition
        c = math.sqrt( (2.0 * math.e) / math.pi )

        counter = 0

        # Open a file for output
        outFile = []

        #Perfom number of iterations requested by user
        while counter < num_iterations:

            # PROCEDURE, From ROSS: Simulation (5th Edition) Page 78
            # Step 1:  Generate Y1, an exponential random variable with rate 1
            Y1 = this.__gen_exponential_distro_rand_variable()
            # Step 2:  Generate Y2, an exponential random variable with rate 2
            Y2 = this.__gen_exponential_distro_rand_variable()
            # Step 3:  If Y2 - (Y1 - 1)^2/2 > 0, set Y = Y2 - (Y1 - 1)^2/2, and go to Step 4 (accept)
            #          Otherwise, go to Step 1 (reject)
            subtraction_value = ( math.pow( ( Y1 - 1 ), 2 ) ) / 2
            critical_value = Y2 - subtraction_value
            if critical_value > 0:
                accept = True
            else:
                reject = True

            # Step 4:  Generate a random number, U, and set:
            #          Z = Y1 if U <= 1/2
            #          Z = Y2 if U >- 1/2
            if accept == True:
                U = random.random()
                if (U > 0.5):
                    Z = Y1
                if (U <= 0.5):
                    Z = -1.0 * Y1

                # write to output file
                outFile.append(Z)
                counter += 1

            # Else, increment our rejection count
            else:
                rejections += 1


            # Reset boolean values
            accept = False
            reject = False

        return outFile

    def randomStandardNormal(this, new_min, new_max, **kwargs):
        """
        Returns a random normal distributed number/s in the range
        
        Args:
        - new_min: [Integer] Start of the range
        - new_max: [Integer] End of the range
        Kwargs:
        - ls: [integer]

        Returns random number: [Int] If Truthy, will return that many numbers
        """
        # num = 1 if "ls" not in kwargs else kwargs['ls']
        # for i in 

        return((this.__accept_or_reject(1)[0] + 4) / (4 + 4) ) * (new_max - new_min) + new_min
    
    def euclid3D(this, t1, t2,**kwargs ):
        """
        Returns Euclidean distance in 3D, or the midpoint coords
        
        Args:
        - t1: [Tuple/Array] Vector1
        - t2: [Tuple/Array] Vector2
        Kwargs:
        - mid: [Truthy]
            Return [x,y,z][om.MVector] middle point
        Returns distance: [float]
        """
        if type(t1) != "list" or type(t1) != "vector" :
            t1 = pmc.xform(t1, q=1, ws=1, t=1)
        if type(t2) != "list" or type(t2) != "vector" :
            t2 = pmc.xform(t2, q=1, ws=1, t=1)
        v1, v2 = om.MVector(t1), om.MVector(t2)
        # ((X1 + X2)/2), ((Y1 + Y2)/2), ((Z1 + Z2)/2)
        if "mid" in kwargs and bool(kwargs['mid']):
            return ((v1[0] + v2[0])/2), ((v1[1] + v2[1])/2), ((v1[2] + v2[2])/2)
        else: return om.MVector(v2-v1).length() 
    
    def applyToAxis(this, val, vect = [0,1,0]):
        ret = [val * vect[0], val * vect[1], val * vect[2]]
        return ret




