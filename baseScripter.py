import pymel.core as pmc
import math
import random
import pymel.core as pmc
from pymel.core import *

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
from maya.common.ui import LayoutManager
from maya.common.ui import showMessageBox
from maya.common.ui import showConfirmationDialog
from maya.common.utils import getSourceNodes
from maya.common.utils import getSourceNodeFromPlug
from maya.common.utils import getSourceNode
from maya.common.utils import getIndexAfterLastValidElement
import json
from math import degrees , fabs , sqrt
from functools import partial , wraps


import maya.api.OpenMaya as om

import unittest

# import maya.cmds as cmds

# # Clear caches in all dependency graph nodes
# cmds.clearCache( all=True )


# ----------------------V1-------------------------
# import sys
# path = r'G:\My Drive\Maya\scripts\BaseScripter'
# if path not in sys.path:
#     sys.path.append(path)


# import baseScripter
# reload(baseScripter)

# bs= baseScripter.BaseScripter()

# ------------------------V2-----------------------
# import sys
# path = r'G:\My Drive\Maya\MyScripts\BaseScripter'
# if path not in sys.path:
#     sys.path.append(path)

# import baseScripter

# reload(baseScripter)

# bs= baseScripter.BaseScripter()


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
        if("v" in args):
            pmc.setAttr(this.ag(obj, "visibility"), lock=1, k=0, channelBox=0)

        if (len(args) > 0):
            for attr in args:
                pmc.setAttr(this.ag(obj, attr), lock=1, k=0, channelBox=0)

    def __init__(this, *args, **kwargs):
        """
        Initializes the BaseScripter Class

        If selection is present at runtime, it will be stored in this.target

        KWArgs:
        - name: [String] Name of feature being built
        - side: [String] Included in the label if present
        - cleanup: [String] Name of Object in scene to be deleted during intialization
        """
        
        this.__dict__.update(kwargs)
        this.groups = {}
        this.target = pmc.ls(sl=1)
        print(this.target)
        this.debug = True
        
        this.cleanupList = ["pointMatrixMult", "setRange", "decomposeMatrix", "composeMatrix", "motionPath", "cluster", "tweak", "wire", "blendShape", "condition", "blendTwoAttr","distanceBetween", "setRange", "multiplyDivide","plusMinusAverage"]

        if("name" in kwargs):
            if("side" in kwargs):
                this.label = this.ng(kwargs['side'], this.name, n=0)
            else:
                this.label = this.name
 
            cleanupNodes = lambda : pmc.delete(pmc.ls("*" + this.label + "*", type=this.cleanupList))
            
            if('cleanup' in kwargs and len(pmc.ls(kwargs["cleanup"])) > 0):
                try:
                    pmc.delete(kwargs["cleanup"])
                except: 
                    print("error")
            
            try:
                if(pmc.objExists(this.ng('grp',this.label, n=1 ))):
                    pmc.delete(this.ng('grp',this.label, n=1))
            except:
                pass
            try:
                cleanupNodes()
            except:
                pass
            this.cleanup = pmc.group(n = this.ng('grp',this.label, n=1, w=1), em=1)
            this.groups['cleanup'] = this.cleanup
            this.name = kwargs['name']
           
        else: 
            this.name = "BaseScripterDefaultName"
            this.label = this.name

        # scene cleanup on reset
        
    def setIHI(self, targets=[], n=1, v=0):
        """
        Sets isHistoricallyInteresteing on targets
        
        kwargs:
        targets: (Object/String/Array): Objects to effeect
        n: [Int/Bool]: If true, neighbors will be effected, else only the target will be
        v: [Int]: Value to set ihi to. Default 0
        """
        if(type(targets)!= list):
            targets = [targets]
        for target in pmc.ls(sl=1):
            if(not n):
                target.attr("ihi").set(v)
            else:
                conx=pmc.listConnections()
                for con in conx:
                    con.attr("ihi").set(v)

    def createContainer(this):
        """
        This method creates a container object which fields can be assigned
        dynamically.
        
        For instance, the object returned by this method will allow:
        
        obj = createContainer()
        obj.newAttribute = 'my new attribute value'
        """
        
        # Way to create temporary structure.
        return type( 'TempStruct' , ( object , ) , {} )

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
        if("parent" in kwargs):
            pmc.parent(offsetGrp, kwargs['parent'])

        if(hasattr(this, "cleanup") and "parent" not in kwargs):
            pmc.parent(offsetGrp, this.cleanup)
        return offsetGrp
    
    def execute(this, *args):
        execution_generator = (x for x in args)
        for procs in execution_generator:
            try:
                procs()
            except Exception as error:
                try:
                    print("Error at function: " + procs.__name__ )
                except: 
                    print("Error in BaseScripter Execution")
                print(error)
                return
        if(this.debug and this.target and len(pmc.ls(this.target)))>0:
            pmc.select(this.target)  
        else:
            pmc.select(cl=1)
        # print(this.name +  " execution complete")

    def colorCCs(self, targets, color=[1,1,1]):
        """
        Recursivley colors all nurbs curve in target
        
        Args:
        - target: [List/Object] Target Curves to be recolored
        - color: [List/Tuple], [0-1] Space, RGB color to apply

        """
        for child in targets:
            if(pmc.objectType(child, isAType="nurbsCurve")):
                    child.attr("overrideEnabled").set(1)
                    child.attr("overrideRGBColors").set(1)
                    child.attr("overrideColorRGB").set(color)
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
        print(type(t1), type(t2))
        supportedTypes = ['list', "vector", "Vector", "pymel.core.datatypes.Vector"]
        if type(t1) not in supportedTypes :
            t1 = pmc.xform(t1, q=1, ws=1, t=1)
        if type(t2) not in supportedTypes:
            t2 = pmc.xform(t2, q=1, ws=1, t=1)
        v1, v2 = om.MVector(t1), om.MVector(t2)
        # ((X1 + X2)/2), ((Y1 + Y2)/2), ((Z1 + Z2)/2)
        if "mid" in kwargs and bool(kwargs['mid']):
            return ((v1[0] + v2[0])/2), ((v1[1] + v2[1])/2), ((v1[2] + v2[2])/2)
        else: return om.MVector(v2-v1).length() 
    
    def applyToAxis(this, val, vect = [0,1,0]):
        ret = [val * vect[0], val * vect[1], val * vect[2]]
        return ret

    def midpoint(this, p1, p2):
        '''Returns the midpoint or 2 points in space'''
        return([(p1[0] + p2[0])/2, (p1[1] + p2[1])/2, (p1[2] + p2[2])/2 ])


# UI
     
    @staticmethod
    def handleError( message ):
        """
        This method is the default error handler for user errors.
        
        It simply shows a dialog box with the error message.
        """
        
        showMessageBox(
            title=maya.stringTable['y_quickRigUI.kErrorTitle' ] ,
            message=message ,
            icon='critical'
            )
    
    
    @staticmethod
    def requestConfirmation( title , message ):
        """
        This method is the default handler to request confirmation.
        
        It simply shows a ok / cancel dialog box with the message.
        """
        
        return showConfirmationDialog( title , message )
    
    
    @staticmethod
    def callbackWrapper( *args , **kwargs ):
        """
        This method is a wrapper in the form expected by UI elements.
        
        Its signature allows it to be flexible with regards to what UI elements
        expects.  Then it simply calls the given functor.
        """
        
        kwargs[ 'functor' ]( )
    
    
    # def callbackTool( self , function ):
    #     """
    #     This method returns a callback method that can be used by the UI
    #     elements.
        
    #     It wraps the "easier to define" callbacks that only takes the tool as
    #     an element into the callbacks that UI element expects.
    #     """
        
    #     functor = partial( function , tool=self )
    #     return partial( QuickRigTool.callbackWrapper , functor=functor )



# react syle UI binding test under the cut
#region
        
# # class BoundObject(object):
# #     '''Alpha version of a Reactjs style binding of UI elements to values that automatically re-render the element on value change
# #     '''
# #     def __init__(self, pymelUIElement, **kwargs):
# #         # element must be executed at runtime, deferred to elemGetter
# #         self._elem = pymelUIElement
# #         # ref to self element to update it on valueSetter
# #         self._ref = None
# #         # stored kwargs
# #         self._kwargs = kwargs
# #         # when this value is updated, the UI element is rerendered
# #         self._value = None
       

# #     @property
# #     def elem(self):
# #         # Getter of element
# #         # execute UI generation, and stor reference for updating
# #         self._ref = self._elem(**self._kwargs)
# #         return self._ref

# #     @elem.setter
# #     def elem(self):
# #         # Elem Setter
# #         return self._ref

# #     @elem.deleter
# #     def elem(self):
# #         del self._elem

# #     @property
# #     def value(self):
# #         return self._value

# #     @value.setter
# #     def value(self, updatedValue):
# #         # On call of statChanger, the UI elements wil be rerendered

# #         # if kwarg v is lambda, execute callback and inject kwargs to be mutated
# #         if(callable(updatedValue['v']) and updatedValue['v'].__name__ == "<lambda>"):
# #             # Update kwargs
# #             updatedValue['v'](self._kwargs)
# #             temp = self._kwargs.copy()
# #             temp.update({"e": 1})
# #             # Refresh the UI
# #             return self._elem(self._ref, **temp)
# #         else:
            
# #             temp = self._kwargs.copy()
# #             temp.update(**updatedValue)
# #             temp.update({"e": 1})

# #             return self._elem(self._ref, **temp)


# # def ReactComponent(elem, **staticValues):
# #     '''Reactify function that generates the class, and exposees the element and the setValue function bound to it
    
# #     Example:
# #     //Create a checkbox and inject kwargs
# #     [elem, setValue] = ReactComponent(pmc.checkBox, label = "TestL Label", v=1) 
    
# #     with window:
# #         with pmc.columnLayout():
# #             with pmc.frameLayout():
                
# #                 //render window in hierarchy
# #                 elem()
                
# #                 //Explicitly change its value
# #                 setValue(v= lambda x : x.update({'v': 0}) )

# #                 with pmc.columnLayout():
# #                         pmc.button(label = "Toggle", 
                        
# #                         //setValue can also be passed a lambda that updates the kwargs dict, injected into x
# #                         c=lambda x : setValue(v = lambda x : x.update({'v': not x['v']})))

# #     '''
# #     c = BoundObject(elem, **staticValues)
# #     return lambda : c.elem, lambda **staticValues : c.__setattr__("value", staticValues)


# # inputs = {'active' : True}

# # [elem, setValue] = ReactComponent(pmc.checkBox, label = "TestL Label", v=inputs['active']) 


# # def printer():
# #      print(inputs)
# # with window:
# #             # Enable/Disable sections of rig, setting rig parameters
# #     with pmc.columnLayout():
# #             with pmc.frameLayout(mw=15, mh = 10):
# #                 # ShouldersSettings
# #                 # pmc.checkBox(label = "Shoulders")
# #                 elem()
# #                 setValue(v= lambda x : x.update({'v': 0}) )


# #                 with pmc.columnLayout():
# #                         pmc.button(label = "Toggle", c=lambda x : setValue(v = lambda x : x.update({'v': not x['v']})))
# #                         pmc.button(label = "Toggle", c= lambda x : printer())

# class BoundObject(object):
#     '''Alpha version of a Reactjs style binding of UI elements to values that automatically re-render the element on value change
#     '''
#     def __init__(self, pymelUIElement, **kwargs):
#         # element must be executed at runtime, deferred to elemGetter
#         self._elem = pymelUIElement
#         # ref to self element to update it on valueSetter
#         self._ref = None
#         # stored kwargs
#         self._kwargs = kwargs
#         # when this value is updated, the UI element is rerendered
#         self._value = None
       

#     @property
#     def elem(self):
#         # Getter of element
#         # execute UI generation, and stor reference for updating
#         self._ref = self._elem(**self._kwargs)
#         return self._ref

#     @elem.setter
#     def elem(self):
#         # Elem Setter
#         return self._ref

#     @elem.deleter
#     def elem(self):
#         del self._elem

#     @property
#     def value(self, query):
#         print(query)
#         return self._value


#     @value.setter
#     def value(self, updatedValue):
#         # On call of statChanger, the UI elements wil be rerendered

#         # if kwarg v is lambda, execute callback and inject kwargs to be mutated
#         if(callable(updatedValue['v']) and updatedValue['v'].__name__ == "<lambda>"):
#             # Update kwargs
#             updatedValue['v'](self._kwargs)
#             temp = self._kwargs.copy()
#             temp.update({"e": 1})
#             # Refresh the UI
#             return self._elem(self._ref, **temp)
#         else:
            
#             temp = self._kwargs.copy()
#             temp.update(**updatedValue)
#             temp.update({"e": 1})

#             return self._elem(self._ref, **temp)


# inputs = {'active' : True}



# def ReactComponent(elem, **staticValues):

#     inputs['active'] = [inputs['active']]
#     c = BoundObject(elem, **staticValues)
#     print(c._value)

#     return lambda : c.elem, lambda **staticValues : c.__setattr__("value", staticValues), lambda query : c.__getattribute__("value", query)



# [elem, setValue, getAttr ] = ReactComponent(pmc.checkBox, label = "TestL Label", v=1) 


# def printer(input):
#      print("pringint", input)
# with window:
#             # Enable/Disable sections of rig, setting rig parameters
#     with pmc.columnLayout():
#             with pmc.frameLayout(mw=15, mh = 10):
#                 # ShouldersSettings
#                 # pmc.checkBox(label = "Shoulders")
#                 elem()
#                 setValue(v= lambda x : x.update({'v': 0}) )
#                 print(getAttr("v"))


#                 with pmc.columnLayout():
#                         pmc.button(label = "Toggle", c=lambda x : setValue(v = lambda x : x.update({'v': not x['v']})))
#                         pmc.button(label = "Toggle", c=lambda x : printer(getAttr("v")))




# # class BoundObject(object):
# #     def __init__(self, pymelUIElement, **kwargs):
# #         self._value = None
# #         self._elem = lambda : pymelUIElement(**kwargs)
# #         self._kwargs = kwargs

# #     @property
# #     def elem(self):
# #         print("getter of elem called")
# #         return lambda : self._elem(**self._kwargs)

# #     @elem.setter
# #     def elem(self, value):
# #         print("setter of elem called")
# #         print(self._kwargs)
# #         self._elem(**self._kwargs)

# #     @elem.deleter
# #     def elem(self):
# #         del self._elem

# # def ReactComponent(elem, **kwargs):
# #     c = BoundObject(elem, **kwargs)
# #     print(c._elem)
# #     return c._value, lambda : c._elem(), lambda x : c.__setattr__("elem", x)

# # [value, elem, setValue] = ReactComponent(pmc.checkBox, label = "10", v=1)
#endregion