import xml.etree.ElementTree as ET
from lxml import etree as ET2
import argparse
import os
import platform
from clangTest import *
def createBlockName( func ):
    name = func.name
    name[0].title()
    i = 0
    for param in func.params:
        if( i is 0):
	    name = name + " with "
	else:
	    name = name + " and "
        name = name + param[0] + " as "
	name = name + " %'" + param[0] + "'"
	i = i + 1
    return name
def determineBlockType( func ):
    type = func.returnType.lower()
    if( type == "int" or type == "float" or type == "double"):
        return "reporter"
    if( type == "bool" or type == "boolean" ):
        return "predicate"
    else:
        return "command"
def determineParamType( param ):
    cleaned = param.lower()
    if( cleaned == "int" or cleaned == "float" or cleaned == "double"):
        return "%n"
    if( cleaned == "std::string" or "string" ):
        return "%txt"
    else:
        print "FunctionParam Error: Could not determine parameter type in determineParamType in BlockGenerator.py"
	raise
# Arg parse stuff
parser = argparse.ArgumentParser(description="Generates XML objects that represent each function in our arduino libraries")
parser.add_argument("-l", "--library", required=True)
args = parser.parse_args()
# Xml stuff
libxml = ET.parse( args.library )
library = libxml.getroot()
# Clang stuff
clang.cindex.Config.set_library_path('/usr/lib/x86_64-linux-gnu')
if(platform.platform().split('-')[0].lower() == "darwin"):
    clang.cindex.Config.set_library_path('/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib')
index = clang.cindex.Index.create()
# lxml generator stuff
root = ET2.Element("blocks")
root.set("app", "Snap! 4.0, http://snap.berkeley.edu") 
root.set("version", "1") 
for component in library:
    path = component.attrib["path"]
    path = os.path.expandvars( path )
    #print path
    translation_unit = index.parse(path, ['-x', 'c++', '-std=c++11', '-D__CODE_GENERATOR__'])
    classes = build_classes(translation_unit.cursor, path)
    for aClass in classes:
        hasSetup = False
        for aFunction in aClass.functions:
            #print aFunction
	    newBlock = ET.SubElement( root, "block-definition" )
	    newBlock.set("s", createBlockName(aFunction) )
	    newBlock.set("type", determineBlockType(aFunction))
	    ET.SubElement( newBlock, "header" )
	    ET.SubElement( newBlock, "code" )
	    inputs = ET.SubElement( newBlock, "inputs" )
	    for param in aFunction.params:
	        input = ET.SubElement( inputs, "input" )
		input.set("type", determineParamType( param[1] ))
		if( param[0] is "setup" ):
		    hasSetup = True
        if hasSetup is False:
            raise Exception( aClass.name + " has no setup() method!")
print ET2.tostring( root, pretty_print=True )
#tree = ET2.ElementTree( root )
